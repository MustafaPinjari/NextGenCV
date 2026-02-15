# Security and Deployment Configuration

## Secure File Storage Configuration

### Development Environment
By default, uploaded files are stored in `media/` directory within the project for development convenience.

### Production Environment
For production deployment, configure secure file storage:

1. **Set MEDIA_ROOT outside web root:**
   ```bash
   export MEDIA_ROOT=/var/www/nextgencv/media
   ```

2. **Create media directory with proper permissions:**
   ```bash
   sudo mkdir -p /var/www/nextgencv/media/uploads
   sudo chown -R www-data:www-data /var/www/nextgencv/media
   sudo chmod 750 /var/www/nextgencv/media
   ```

3. **Disable direct media file serving in Nginx:**
   ```nginx
   # DO NOT add this in production:
   # location /media/ {
   #     alias /var/www/nextgencv/media/;
   # }
   
   # Instead, all file access goes through Django views with authorization
   ```

4. **File Access Control:**
   - All uploaded files are served through Django views with authorization checks
   - See `apps/resumes/views_file_access.py` for implementation
   - URLs: `/resumes/upload/<id>/file/` and `/resumes/upload/<id>/download/`

## Security Features Implemented

### 1. File Upload Security (Task 17.1)
- ✅ File type validation (PDF only)
- ✅ MIME type verification
- ✅ File size limits (10MB max)
- ✅ Embedded script scanner
- Implementation: `apps/resumes/utils/file_validators.py`

### 2. Secure File Storage (Task 17.2)
- ✅ Secure random filename generation (UUID-based)
- ✅ Files stored outside web root (configurable via MEDIA_ROOT)
- ✅ Access control checks on all file access
- Implementation: `apps/resumes/views_file_access.py`

### 3. Text Sanitization (Task 17.3)
- ✅ HTML sanitization using bleach library
- ✅ Control character removal
- ✅ XSS prevention
- Implementation: `apps/resumes/services/pdf_parser.py`

### 4. Data Isolation (Task 17.4)
- ✅ Authorization checks on all views (@login_required)
- ✅ Ownership verification (user can only access their own data)
- ✅ Query filtering by user
- Implementation: All views in `apps/resumes/views.py`, `apps/analytics/views.py`, etc.

### 5. Cascade Deletion (Task 17.5)
- ✅ Proper CASCADE on all foreign keys
- ✅ User deletion cascades to all related data
- Implementation: All models use `on_delete=models.CASCADE`

## Additional Security Recommendations

### For Production Deployment:

1. **Environment Variables:**
   ```bash
   export SECRET_KEY='your-secret-key-here'
   export DEBUG=False
   export ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'
   export MEDIA_ROOT='/var/www/nextgencv/media'
   ```

2. **Database Security:**
   - Use PostgreSQL instead of SQLite
   - Configure database credentials via environment variables
   - Enable SSL for database connections

3. **HTTPS Configuration:**
   - Enable HTTPS in production
   - Set `SECURE_SSL_REDIRECT = True`
   - Set `SESSION_COOKIE_SECURE = True`
   - Set `CSRF_COOKIE_SECURE = True`

4. **Additional Django Security Settings:**
   ```python
   # In production settings:
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   X_FRAME_OPTIONS = 'DENY'
   SECURE_HSTS_SECONDS = 31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True
   ```

5. **File Upload Limits:**
   - Already configured: 10MB max file size
   - Enforced at both Django and web server level

6. **Rate Limiting:**
   - Consider implementing rate limiting for file uploads
   - Use django-ratelimit or similar package

7. **Monitoring and Logging:**
   - All file access is logged
   - Monitor logs for suspicious activity
   - Set up alerts for repeated authorization failures

## Testing Security Features

### Test File Upload Security:
```bash
# Test file type validation
python manage.py shell
>>> from django.core.files.uploadedfile import SimpleUploadedFile
>>> from apps.resumes.utils.file_validators import validate_pdf_file
>>> 
>>> # Test with non-PDF file
>>> fake_file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
>>> is_valid, error = validate_pdf_file(fake_file)
>>> print(is_valid, error)  # Should be False with error message
```

### Test Access Control:
```bash
# Create two users and try to access each other's files
# User A should not be able to access User B's uploaded resumes
```

### Test Cascade Deletion:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from apps.resumes.models import Resume
>>> 
>>> # Create test user with data
>>> user = User.objects.create_user('testuser', 'test@example.com', 'password')
>>> resume = Resume.objects.create(user=user, title='Test Resume')
>>> 
>>> # Delete user
>>> user.delete()
>>> 
>>> # Verify resume is also deleted
>>> Resume.objects.filter(title='Test Resume').exists()  # Should be False
```

## Security Audit Checklist

- [x] File upload validation implemented
- [x] MIME type verification
- [x] File size limits enforced
- [x] Embedded script detection
- [x] Secure filename generation
- [x] Files stored outside web root (configurable)
- [x] Access control on file serving
- [x] Text sanitization (XSS prevention)
- [x] Authorization checks on all views
- [x] Data isolation by user
- [x] Cascade deletion configured
- [ ] HTTPS enabled (production only)
- [ ] Rate limiting configured (optional)
- [ ] Security headers configured (production only)
- [ ] Database credentials secured (production only)

## References

- Django Security Documentation: https://docs.djangoproject.com/en/4.2/topics/security/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- File Upload Security: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
