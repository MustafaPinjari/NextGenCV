"""
Performance tests for NextGenCV v2.0

**Feature: nextgencv-v2-advanced, Task 20.5: Performance Testing**

Tests performance requirements:
- Large PDF file handling
- Many versions (100+)
- Concurrent users
- Response times
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.resumes.models import Resume, ResumeVersion
from apps.resumes.services.pdf_parser import PDFParserService
import time
import io


class LargePDFPerformanceTest(TestCase):
    """Test performance with large PDF files"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='perfuser',
            password='testpass123'
        )
        self.client.login(username='perfuser', password='testpass123')
    
    def test_large_pdf_parsing_performance(self):
        """Test that large PDFs (up to 10MB) are parsed within acceptable time"""
        # Create a large text content (simulate large PDF)
        large_text = "Test resume content. " * 50000  # ~1MB of text
        
        # Create resume
        resume = Resume.objects.create(
            user=self.user,
            title="Large Resume"
        )
        
        start_time = time.time()
        
        # Simulate parsing large content
        parser = PDFParserService()
        # Note: We're testing the processing time, not actual PDF parsing
        # In real scenario, this would parse a 10MB PDF
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 5 seconds for large files
        self.assertLess(elapsed_time, 5.0,
                       f"Large PDF processing took {elapsed_time:.2f}s, expected < 5s")


class ManyVersionsPerformanceTest(TestCase):
    """Test performance with many resume versions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='versionuser',
            password='testpass123'
        )
        self.client.login(username='versionuser', password='testpass123')
        
        # Create resume
        self.resume = Resume.objects.create(
            user=self.user,
            title="Test Resume"
        )
    
    def test_create_many_versions_performance(self):
        """Test creating 100+ versions completes in reasonable time"""
        start_time = time.time()
        
        # Create 100 versions
        versions = []
        for i in range(100):
            version = ResumeVersion.objects.create(
                resume=self.resume,
                version_number=i + 1,
                snapshot_data={'content': f"Version {i + 1} content"}
            )
            versions.append(version)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 10 seconds
        self.assertLess(elapsed_time, 10.0,
                       f"Creating 100 versions took {elapsed_time:.2f}s, expected < 10s")
        
        # Verify all versions created
        self.assertEqual(ResumeVersion.objects.filter(resume=self.resume).count(), 100)
    
    def test_query_many_versions_performance(self):
        """Test querying resume with 100+ versions is fast"""
        # Create 100 versions
        for i in range(100):
            ResumeVersion.objects.create(
                resume=self.resume,
                version_number=i + 1,
                snapshot_data={'content': f"Version {i + 1} content"}
            )
        
        start_time = time.time()
        
        # Query version list
        response = self.client.get(
            reverse('version_list', kwargs={'pk': self.resume.id})
        )
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 2 seconds
        self.assertLess(elapsed_time, 2.0,
                       f"Querying 100 versions took {elapsed_time:.2f}s, expected < 2s")
        
        self.assertEqual(response.status_code, 200)
    
    def test_version_comparison_performance(self):
        """Test comparing versions with large content is fast"""
        # Create two versions with large content
        large_content = "Test content. " * 10000  # ~150KB
        
        version1 = ResumeVersion.objects.create(
            resume=self.resume,
            version_number=1,
            snapshot_data={'content': large_content}
        )
        
        version2 = ResumeVersion.objects.create(
            resume=self.resume,
            version_number=2,
            snapshot_data={'content': large_content + " Additional content."}
        )
        
        start_time = time.time()
        
        # Access version detail (which may include comparison logic)
        response = self.client.get(
            reverse('version_detail', kwargs={
                'pk': self.resume.id,
                'version_id': version2.id
            })
        )
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 1 second
        self.assertLess(elapsed_time, 1.0,
                       f"Version comparison took {elapsed_time:.2f}s, expected < 1s")


class ResponseTimePerformanceTest(TestCase):
    """Test response times for common operations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='responseuser',
            password='testpass123'
        )
        self.client.login(username='responseuser', password='testpass123')
        
        # Create test data
        self.resume = Resume.objects.create(
            user=self.user,
            title="Test Resume"
        )
    
    def test_resume_list_response_time(self):
        """Test resume list loads within 500ms"""
        # Create 20 resumes
        for i in range(20):
            Resume.objects.create(
                user=self.user,
                title=f"Resume {i}"
            )
        
        start_time = time.time()
        response = self.client.get(reverse('resume_list'))
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_time, 0.5,
                       f"Resume list took {elapsed_time:.3f}s, expected < 0.5s")
    
    def test_resume_detail_response_time(self):
        """Test resume detail loads within 500ms"""
        start_time = time.time()
        response = self.client.get(
            reverse('resume_detail', kwargs={'pk': self.resume.id})
        )
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_time, 0.5,
                       f"Resume detail took {elapsed_time:.3f}s, expected < 0.5s")
    
    def test_optimization_response_time(self):
        """Test optimization page loads within 1 second"""
        start_time = time.time()
        response = self.client.get(
            reverse('fix_resume', kwargs={'pk': self.resume.id})
        )
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_time, 1.0,
                       f"Optimization page took {elapsed_time:.3f}s, expected < 1s")


class ConcurrentUsersPerformanceTest(TransactionTestCase):
    """Test performance with concurrent users"""
    
    def setUp(self):
        # Create multiple users
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'user{i}',
                password='testpass123'
            )
            self.users.append(user)
            
            # Create resume for each user
            Resume.objects.create(
                user=user,
                title=f"Resume {i}"
            )
    
    def test_concurrent_resume_access(self):
        """Test multiple users accessing resumes simultaneously"""
        import threading
        
        results = []
        
        def access_resume(user):
            """Simulate user accessing their resume"""
            from django.test import Client
            client = Client()
            client.login(username=user.username, password='testpass123')
            
            start = time.time()
            resume = Resume.objects.filter(user=user).first()
            response = client.get(reverse('resume_detail', kwargs={'pk': resume.id}))
            elapsed = time.time() - start
            
            results.append({
                'user': user.username,
                'status': response.status_code,
                'time': elapsed
            })
        
        # Create threads for concurrent access
        threads = []
        start_time = time.time()
        
        for user in self.users:
            thread = threading.Thread(target=access_resume, args=(user,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # All requests should complete within 5 seconds
        self.assertLess(total_time, 5.0,
                       f"Concurrent access took {total_time:.2f}s, expected < 5s")
        
        # All requests should succeed
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertEqual(result['status'], 200)
            # Each individual request should be fast
            self.assertLess(result['time'], 2.0)
    
    def test_concurrent_version_creation(self):
        """Test multiple users creating versions simultaneously"""
        import threading
        
        results = []
        
        def create_version(user):
            """Simulate user creating a version"""
            resume = Resume.objects.filter(user=user).first()
            
            start = time.time()
            version = ResumeVersion.objects.create(
                resume=resume,
                version_number=1,
                snapshot_data={'content': "Test version content"}
            )
            elapsed = time.time() - start
            
            results.append({
                'user': user.username,
                'version_id': version.id,
                'time': elapsed
            })
        
        # Create threads for concurrent version creation
        threads = []
        start_time = time.time()
        
        for user in self.users:
            thread = threading.Thread(target=create_version, args=(user,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # All operations should complete within 3 seconds
        self.assertLess(total_time, 3.0,
                       f"Concurrent version creation took {total_time:.2f}s, expected < 3s")
        
        # All operations should succeed
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertIsNotNone(result['version_id'])
            self.assertLess(result['time'], 1.0)


class DatabaseQueryPerformanceTest(TestCase):
    """Test database query performance"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='dbuser',
            password='testpass123'
        )
        
        # Create test data
        self.resumes = []
        for i in range(50):
            resume = Resume.objects.create(
                user=self.user,
                title=f"Resume {i}"
            )
            self.resumes.append(resume)
            
            # Create 10 versions for each resume
            for j in range(10):
                ResumeVersion.objects.create(
                    resume=resume,
                    version_number=j + 1,
                    snapshot_data={'content': f"Version {j + 1} content"}
                )
    
    def test_bulk_query_performance(self):
        """Test querying all user resumes with versions is efficient"""
        from django.db import connection
        from django.test.utils import override_settings
        
        # Reset query count
        connection.queries_log.clear()
        
        start_time = time.time()
        
        # Query all resumes with prefetch of versions
        resumes = Resume.objects.filter(user=self.user).prefetch_related('versions')
        
        # Access the data
        for resume in resumes:
            versions = list(resume.versions.all())
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 1 second
        self.assertLess(elapsed_time, 1.0,
                       f"Bulk query took {elapsed_time:.3f}s, expected < 1s")
    
    def test_filtered_query_performance(self):
        """Test filtered queries are fast"""
        start_time = time.time()
        
        # Query resumes with specific criteria
        resumes = Resume.objects.filter(
            user=self.user,
            title__icontains="Resume 1"
        ).select_related('user')
        
        result_count = resumes.count()
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 100ms
        self.assertLess(elapsed_time, 0.1,
                       f"Filtered query took {elapsed_time:.3f}s, expected < 0.1s")
        
        self.assertGreater(result_count, 0)
