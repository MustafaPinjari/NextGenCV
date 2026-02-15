# NextGenCV v2.0 Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Dependency Installation](#dependency-installation)
5. [Static Files Configuration](#static-files-configuration)
6. [Security Configuration](#security-configuration)
7. [Performance Tuning](#performance-tuning)
8. [Deployment Steps](#deployment-steps)
9. [Post-Deployment Verification](#post-deployment-verification)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Troubleshooting](#troubleshooting)
12. [Deployment Checklist](#deployment-checklist)

---

## Prerequisites

### System Requirements

**Minimum Requirements**:
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- OS: Ubuntu 20.04 LTS or later (recommended), CentOS 7+, or Debian 10+

**Recommended for Production**:
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv or venv
- PostgreSQL 12+ (recommended for production) or SQLite (development only)
- Nginx or Apache (web server)
- Gunicorn or uWSGI (WSGI server)
- Redis (optional, for caching)
- Supervisor or systemd (process management)

### External Dependencies

- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)
- SMTP server (for email notifications)
- Cloud storage (optional, for file uploads - AWS S3, Google Cloud Storage)

---

## Environment Configuration

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
# .env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nextgencv_db
DATABASE_USER=nextgencv_user
DATABASE_PASSWORD=your-secure-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Upload Settings
MEDIA_ROOT=/var/www/nextgencv/media
MEDIA_URL=/media/
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes

# Static Files
STATIC_ROOT=/var/www/nextgencv/static
STATIC_URL=/static/

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Cache Configuration (Redis)
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
CACHE_LOCATION=redis://127.0.0.1:6379/1

# Logging
LOG_LEVEL=INFO
LOG_DIR=/var/log/nextgencv

# Performance
CONN_MAX_AGE=600
```

### 2. Generate Secret Key

Generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Update Django Settings

Update `config/settings.py` to read from environment variables:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DATABASE_USER', ''),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', ''),
        'PORT': os.getenv('DATABASE_PORT', ''),
        'CONN_MAX_AGE': int(os.getenv('CONN_MAX_AGE', 0)),
    }
}

# Email
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Media Files
MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media')
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')

# Static Files
STATIC_ROOT = os.getenv('STATIC_ROOT', BASE_DIR / 'staticfiles')
STATIC_URL = os.getenv('STATIC_URL', '/static/')

# Security
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', 0))

# Cache
CACHES = {
    'default': {
        'BACKEND': os.getenv('CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': os.getenv('CACHE_LOCATION', 'unique-snowflake'),
    }
}
```

---

## Database Setup

### Option 1: PostgreSQL (Recommended for Production)

#### 1. Install PostgreSQL

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**CentOS/RHEL**:
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. Create Database and User

```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE nextgencv_db;
CREATE USER nextgencv_user WITH PASSWORD 'your-secure-password';
ALTER ROLE nextgencv_user SET client_encoding TO 'utf8';
ALTER ROLE nextgencv_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE nextgencv_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nextgencv_db TO nextgencv_user;
\q
```

#### 3. Configure PostgreSQL Authentication

Edit `/etc/postgresql/*/main/pg_hba.conf`:

```
# Add this line:
local   nextgencv_db    nextgencv_user                          md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

#### 4. Install Python PostgreSQL Adapter

```bash
pip install psycopg2-binary
```

### Option 2: SQLite (Development Only)

SQLite is included with Python and requires no additional setup. However, it's **not recommended for production** due to:
- Limited concurrent write support
- No user management
- Performance limitations

---

## Dependency Installation

### 1. Create Virtual Environment

```bash
cd /var/www/nextgencv
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install System Dependencies

**For WeasyPrint (PDF generation)**:

**Ubuntu/Debian**:
```bash
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**CentOS/RHEL**:
```bash
sudo yum install python3-devel python3-pip python3-cffi cairo pango gdk-pixbuf2 libffi-devel
```

**For pdfplumber (PDF parsing)**:
```bash
# Usually no additional system dependencies needed
```

### 4. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Verify Installation

```bash
python manage.py check
```

---

## Static Files Configuration

### 1. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 2. Configure Web Server to Serve Static Files

**Nginx Configuration** (`/etc/nginx/sites-available/nextgencv`):

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Static Files
    location /static/ {
        alias /var/www/nextgencv/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media Files
    location /media/ {
        alias /var/www/nextgencv/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # File Upload
        client_max_body_size 10M;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/nextgencv /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Security Configuration

### 1. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 2. Firewall Configuration

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. File Permissions

```bash
# Set ownership
sudo chown -R www-data:www-data /var/www/nextgencv

# Set permissions
sudo chmod -R 755 /var/www/nextgencv
sudo chmod -R 775 /var/www/nextgencv/media
sudo chmod -R 775 /var/www/nextgencv/logs

# Secure sensitive files
sudo chmod 600 /var/www/nextgencv/.env
```

### 4. Database Security

- Use strong passwords
- Restrict database access to localhost
- Enable SSL for database connections
- Regular backups

### 5. Application Security Checklist

- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (50+ characters)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS` set (31536000 recommended)
- [ ] File upload validation enabled
- [ ] XSS protection enabled
- [ ] CSRF protection enabled

---

## Performance Tuning

### 1. Database Optimization

**PostgreSQL Configuration** (`/etc/postgresql/*/main/postgresql.conf`):

```ini
# Memory
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 128MB

# Connections
max_connections = 100

# Query Planning
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200

# Write Ahead Log
wal_buffers = 16MB
checkpoint_completion_target = 0.9
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 2. Gunicorn Configuration

Create `/var/www/nextgencv/gunicorn_config.py`:

```python
import multiprocessing

# Server Socket
bind = '127.0.0.1:8000'
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = '/var/log/nextgencv/gunicorn_access.log'
errorlog = '/var/log/nextgencv/gunicorn_error.log'
loglevel = 'info'

# Process Naming
proc_name = 'nextgencv'

# Server Mechanics
daemon = False
pidfile = '/var/run/nextgencv/gunicorn.pid'
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

# SSL (if terminating SSL at Gunicorn)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'
```

### 3. Redis Cache Setup

Install Redis:
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Configure Redis (`/etc/redis/redis.conf`):
```ini
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 4. Django Cache Configuration

Already configured in `.env` file. Verify cache is working:

```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
'value'
```

---

## Deployment Steps

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx postgresql redis-server supervisor git -y

# Create application directory
sudo mkdir -p /var/www/nextgencv
sudo chown $USER:$USER /var/www/nextgencv
```

### Step 2: Clone Repository

```bash
cd /var/www
git clone <repository-url> nextgencv
cd nextgencv
```

### Step 3: Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 4: Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your configuration
```

### Step 5: Setup Database

```bash
# Create PostgreSQL database (see Database Setup section)
# Then run migrations
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Populate Templates

```bash
python manage.py populate_templates
```

### Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 9: Create Log Directory

```bash
sudo mkdir -p /var/log/nextgencv
sudo chown www-data:www-data /var/log/nextgencv
```

### Step 10: Configure Supervisor

Create `/etc/supervisor/conf.d/nextgencv.conf`:

```ini
[program:nextgencv]
command=/var/www/nextgencv/venv/bin/gunicorn config.wsgi:application -c /var/www/nextgencv/gunicorn_config.py
directory=/var/www/nextgencv
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/nextgencv/supervisor.log
environment=PATH="/var/www/nextgencv/venv/bin"
```

Start Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nextgencv
```

### Step 11: Configure Nginx

```bash
sudo cp /var/www/nextgencv/nginx.conf /etc/nginx/sites-available/nextgencv
sudo ln -s /etc/nginx/sites-available/nextgencv /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 12: Setup SSL

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Step 13: Verify Deployment

```bash
# Check Gunicorn is running
sudo supervisorctl status nextgencv

# Check Nginx is running
sudo systemctl status nginx

# Check application is accessible
curl https://yourdomain.com
```

---

## Post-Deployment Verification

### 1. Functional Testing

- [ ] Homepage loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Resume creation works
- [ ] PDF upload works
- [ ] Resume optimization works
- [ ] Version management works
- [ ] Analytics dashboard loads
- [ ] PDF export works
- [ ] DOCX export works

### 2. Performance Testing

```bash
# Test response time
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com

# Load testing with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/
```

### 3. Security Testing

- [ ] HTTPS is enforced
- [ ] Security headers are present
- [ ] File upload validation works
- [ ] XSS protection works
- [ ] CSRF protection works
- [ ] Data isolation works

### 4. Monitoring Setup

Install monitoring tools:

```bash
# Install monitoring agent (example: New Relic, Datadog, etc.)
# Configure error tracking (example: Sentry)
```

---

## Monitoring and Maintenance

### 1. Log Monitoring

**Application Logs**:
```bash
tail -f /var/log/nextgencv/gunicorn_error.log
tail -f /var/log/nextgencv/django.log
```

**Nginx Logs**:
```bash
tail -f /var/nginx/access.log
tail -f /var/nginx/error.log
```

**PostgreSQL Logs**:
```bash
tail -f /var/log/postgresql/postgresql-*.log
```

### 2. Database Backups

Create backup script (`/usr/local/bin/backup_nextgencv.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/nextgencv"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="nextgencv_db"
DB_USER="nextgencv_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/nextgencv/media

# Delete backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
sudo chmod +x /usr/local/bin/backup_nextgencv.sh
sudo crontab -e

# Add this line to run daily at 2 AM:
0 2 * * * /usr/local/bin/backup_nextgencv.sh
```

### 3. System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
source /var/www/nextgencv/venv/bin/activate
pip install --upgrade -r requirements.txt

# Run migrations
python manage.py migrate

# Restart application
sudo supervisorctl restart nextgencv
```

### 4. Performance Monitoring

Monitor key metrics:
- Response time
- Error rate
- Database query performance
- Memory usage
- CPU usage
- Disk usage

---

## Troubleshooting

### Issue: Application Won't Start

**Check Gunicorn logs**:
```bash
tail -f /var/log/nextgencv/gunicorn_error.log
```

**Common causes**:
- Missing environment variables
- Database connection issues
- Permission problems
- Port already in use

### Issue: 502 Bad Gateway

**Causes**:
- Gunicorn not running
- Wrong socket/port configuration
- Firewall blocking connection

**Solution**:
```bash
sudo supervisorctl status nextgencv
sudo supervisorctl restart nextgencv
```

### Issue: Static Files Not Loading

**Solution**:
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Issue: Database Connection Errors

**Check PostgreSQL is running**:
```bash
sudo systemctl status postgresql
```

**Test connection**:
```bash
psql -U nextgencv_user -d nextgencv_db -h localhost
```

### Issue: High Memory Usage

**Check processes**:
```bash
ps aux | grep gunicorn
```

**Reduce Gunicorn workers**:
Edit `gunicorn_config.py` and reduce `workers` value.

### Issue: Slow Performance

**Check database queries**:
```bash
# Enable query logging in Django settings
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

**Optimize database**:
```bash
sudo -u postgres psql nextgencv_db
VACUUM ANALYZE;
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Code reviewed and tested
- [ ] All tests passing
- [ ] Database migrations created
- [ ] Static files collected
- [ ] Environment variables configured
- [ ] SSL certificate obtained
- [ ] Backup strategy in place
- [ ] Monitoring configured

### Deployment

- [ ] Server prepared and updated
- [ ] Application deployed
- [ ] Database migrated
- [ ] Static files served correctly
- [ ] Gunicorn running
- [ ] Nginx configured
- [ ] SSL enabled
- [ ] Firewall configured

### Post-Deployment

- [ ] Functional testing completed
- [ ] Performance testing completed
- [ ] Security testing completed
- [ ] Monitoring active
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Team notified

### Security Checklist

- [ ] DEBUG = False
- [ ] Strong SECRET_KEY
- [ ] ALLOWED_HOSTS configured
- [ ] SSL/HTTPS enabled
- [ ] Security headers configured
- [ ] File upload validation enabled
- [ ] Database credentials secure
- [ ] Firewall configured
- [ ] Regular backups enabled
- [ ] Monitoring and alerting active

---

## Rollback Procedure

If deployment fails:

1. **Stop the application**:
```bash
sudo supervisorctl stop nextgencv
```

2. **Restore database backup**:
```bash
gunzip < /var/backups/nextgencv/db_YYYYMMDD_HHMMSS.sql.gz | psql -U nextgencv_user nextgencv_db
```

3. **Revert code**:
```bash
cd /var/www/nextgencv
git checkout <previous-commit-hash>
```

4. **Restart application**:
```bash
sudo supervisorctl start nextgencv
```

---

## Support and Resources

- **Documentation**: `/Docs/` directory
- **Issue Tracker**: GitHub Issues
- **Community**: Discord/Slack channel
- **Email Support**: support@yourdomain.com

---

## Conclusion

This deployment guide provides comprehensive instructions for deploying NextGenCV v2.0 to production. Follow each step carefully and verify at each stage. For additional help, consult the documentation or contact support.

**Remember**: Always test in a staging environment before deploying to production!
