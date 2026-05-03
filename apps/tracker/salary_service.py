import re


# Salary data based on publicly available market research (US market, USD)
# Source: aggregated from BLS, Glassdoor public reports, LinkedIn Salary Insights
SALARY_DATA = {
    'software engineer': {'entry': 75000, 'mid': 115000, 'senior': 155000, 'lead': 185000},
    'frontend developer': {'entry': 65000, 'mid': 100000, 'senior': 140000, 'lead': 170000},
    'backend developer': {'entry': 70000, 'mid': 110000, 'senior': 150000, 'lead': 180000},
    'full stack developer': {'entry': 70000, 'mid': 110000, 'senior': 148000, 'lead': 178000},
    'data scientist': {'entry': 80000, 'mid': 120000, 'senior': 160000, 'lead': 195000},
    'data analyst': {'entry': 55000, 'mid': 80000, 'senior': 110000, 'lead': 135000},
    'data engineer': {'entry': 80000, 'mid': 120000, 'senior': 158000, 'lead': 190000},
    'machine learning engineer': {'entry': 90000, 'mid': 135000, 'senior': 175000, 'lead': 210000},
    'devops engineer': {'entry': 75000, 'mid': 115000, 'senior': 150000, 'lead': 180000},
    'cloud engineer': {'entry': 80000, 'mid': 120000, 'senior': 155000, 'lead': 185000},
    'product manager': {'entry': 80000, 'mid': 120000, 'senior': 160000, 'lead': 200000},
    'ux designer': {'entry': 60000, 'mid': 90000, 'senior': 125000, 'lead': 155000},
    'ui designer': {'entry': 55000, 'mid': 85000, 'senior': 115000, 'lead': 145000},
    'marketing manager': {'entry': 55000, 'mid': 80000, 'senior': 110000, 'lead': 140000},
    'project manager': {'entry': 60000, 'mid': 90000, 'senior': 120000, 'lead': 150000},
    'business analyst': {'entry': 55000, 'mid': 80000, 'senior': 110000, 'lead': 135000},
    'cybersecurity engineer': {'entry': 80000, 'mid': 120000, 'senior': 158000, 'lead': 190000},
    'mobile developer': {'entry': 70000, 'mid': 108000, 'senior': 145000, 'lead': 175000},
    'qa engineer': {'entry': 55000, 'mid': 85000, 'senior': 115000, 'lead': 140000},
    'site reliability engineer': {'entry': 85000, 'mid': 125000, 'senior': 162000, 'lead': 195000},
}

# Location multipliers (relative to US national average)
LOCATION_MULTIPLIERS = {
    'san francisco': 1.45, 'sf': 1.45, 'bay area': 1.45,
    'new york': 1.35, 'nyc': 1.35, 'manhattan': 1.35,
    'seattle': 1.25, 'boston': 1.20, 'austin': 1.10,
    'chicago': 1.10, 'los angeles': 1.20, 'la': 1.20,
    'denver': 1.05, 'atlanta': 1.00, 'dallas': 1.00,
    'remote': 1.05, 'india': 0.25, 'uk': 0.85,
    'canada': 0.80, 'europe': 0.75, 'australia': 0.90,
}

# Seniority keywords
SENIORITY_MAP = {
    'junior': 'entry', 'entry': 'entry', 'associate': 'entry', 'intern': 'entry',
    'mid': 'mid', 'intermediate': 'mid', 'ii': 'mid',
    'senior': 'senior', 'sr': 'senior', 'iii': 'senior',
    'lead': 'lead', 'principal': 'lead', 'staff': 'lead', 'head': 'lead',
    'director': 'lead', 'manager': 'lead',
}


class SalaryIntelligenceService:

    def get_salary_range(self, role: str, location: str = '') -> dict:
        role_lower = role.lower().strip()
        location_lower = location.lower().strip()

        # Detect seniority
        seniority = 'mid'
        for keyword, level in SENIORITY_MAP.items():
            if keyword in role_lower:
                seniority = level
                break

        # Match role to salary data
        base_data = None
        role_clean = re.sub(r'\b(junior|senior|sr|lead|principal|staff|head|mid|ii|iii|associate|intern)\b', '', role_lower).strip()

        for key, data in SALARY_DATA.items():
            if key in role_clean or role_clean in key:
                base_data = data
                break

        # Fuzzy fallback
        if not base_data:
            for key, data in SALARY_DATA.items():
                key_words = set(key.split())
                role_words = set(role_clean.split())
                if key_words & role_words:
                    base_data = data
                    break

        if not base_data:
            base_data = SALARY_DATA['software engineer']  # generic fallback

        base_salary = base_data[seniority]

        # Apply location multiplier
        multiplier = 1.0
        for loc_key, mult in LOCATION_MULTIPLIERS.items():
            if loc_key in location_lower:
                multiplier = mult
                break

        low = int(base_salary * multiplier * 0.88)
        mid = int(base_salary * multiplier)
        high = int(base_salary * multiplier * 1.15)

        return {
            'role': role,
            'seniority': seniority,
            'location': location or 'US (national average)',
            'low': low,
            'mid': mid,
            'high': high,
            'low_fmt': f"${low:,}",
            'mid_fmt': f"${mid:,}",
            'high_fmt': f"${high:,}",
            'currency': 'USD',
            'note': 'Estimates based on public market data. Actual salaries vary by company, experience, and negotiation.',
            'negotiation_tips': self._negotiation_tips(seniority, mid),
        }

    def _negotiation_tips(self, seniority: str, mid: int) -> list:
        tips = [
            "Always negotiate — 85% of employers expect it and rarely rescind offers.",
            f"Anchor high: start at ${int(mid * 1.15):,} to land near ${mid:,}.",
            "Get the offer in writing before negotiating other benefits.",
        ]
        if seniority in ('senior', 'lead'):
            tips.append("At senior level, equity/RSUs can be worth more than base — negotiate both.")
        else:
            tips.append("Ask about performance review timelines — a 6-month review can accelerate your raise.")
        return tips
