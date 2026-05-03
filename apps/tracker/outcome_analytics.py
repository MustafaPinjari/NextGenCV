from django.db.models import Count, Avg, Q
from apps.tracker.models import JobApplication


class OutcomeAnalyticsService:
    """
    Computes real-world outcome metrics from job application tracking data.
    This closes the feedback loop: ATS score → application → real outcome.
    """

    def get_user_stats(self, user) -> dict:
        qs = JobApplication.objects.filter(user=user)
        total = qs.count()
        if total == 0:
            return self._empty_stats()

        applied = qs.filter(status__in=['applied', 'interview', 'offer', 'rejected']).count()
        interviews = qs.filter(status__in=['interview', 'offer']).count()
        offers = qs.filter(status='offer').count()
        rejected = qs.filter(status='rejected').count()

        callback_rate = round((interviews / applied * 100), 1) if applied else 0
        offer_rate = round((offers / applied * 100), 1) if applied else 0

        return {
            'total': total,
            'applied': applied,
            'interviews': interviews,
            'offers': offers,
            'rejected': rejected,
            'callback_rate': callback_rate,
            'offer_rate': offer_rate,
            'by_status': self._by_status(qs),
            'score_vs_outcome': self._score_vs_outcome(qs),
            'best_performing_resume': self._best_resume(qs),
        }

    def _empty_stats(self) -> dict:
        return {
            'total': 0, 'applied': 0, 'interviews': 0, 'offers': 0,
            'rejected': 0, 'callback_rate': 0, 'offer_rate': 0,
            'by_status': [], 'score_vs_outcome': [], 'best_performing_resume': None,
        }

    def _by_status(self, qs) -> list:
        return list(
            qs.values('status')
              .annotate(count=Count('id'))
              .order_by('status')
        )

    def _score_vs_outcome(self, qs) -> list:
        """
        Groups applications by ATS score bucket and shows callback rate per bucket.
        Reveals whether higher ATS scores actually lead to more interviews.
        """
        buckets = [
            ('0-40', 0, 40),
            ('41-60', 41, 60),
            ('61-75', 61, 75),
            ('76-90', 76, 90),
            ('91-100', 91, 100),
        ]
        result = []
        for label, low, high in buckets:
            bucket_qs = qs.filter(
                ats_score_at_apply__gte=low,
                ats_score_at_apply__lte=high,
                status__in=['applied', 'interview', 'offer', 'rejected']
            )
            total = bucket_qs.count()
            if total == 0:
                continue
            got_interview = bucket_qs.filter(status__in=['interview', 'offer']).count()
            result.append({
                'bucket': label,
                'total': total,
                'interviews': got_interview,
                'callback_rate': round(got_interview / total * 100, 1),
            })
        return result

    def _best_resume(self, qs):
        """Returns the resume with the highest callback rate (min 3 applications)."""
        from django.db.models import FloatField, ExpressionWrapper, F
        resume_stats = (
            qs.filter(resume__isnull=False, status__in=['applied', 'interview', 'offer', 'rejected'])
              .values('resume__id', 'resume__title')
              .annotate(
                  total=Count('id'),
                  interviews=Count('id', filter=Q(status__in=['interview', 'offer']))
              )
              .filter(total__gte=3)
              .order_by('-interviews')
        )
        if not resume_stats:
            return None
        best = resume_stats[0]
        best['callback_rate'] = round(best['interviews'] / best['total'] * 100, 1)
        return best
