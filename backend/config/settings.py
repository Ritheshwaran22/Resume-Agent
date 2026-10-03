"""
Django settings for Resume Agent backend.
Phases 2-48: Full-Stack AI Resume Agent implementation.
"""
import os
import urllib.parse
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

from django.core.exceptions import ImproperlyConfigured

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Gemini API configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Safe environment parsing for DEBUG
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

# Secret key handling: env-driven; fails explicitly in production if missing
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-phase1-resume-agent-secret-key-1234567890'
    else:
        raise ImproperlyConfigured("SECRET_KEY environment variable must be set in production when DEBUG=False.")

# Host validation: comma-separated list, whitespace trimmed, no wildcard in production
allowed_hosts_raw = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = []
for host in allowed_hosts_raw.split(','):
    host = host.strip()
    if host.startswith('http://'):
        host = host[7:]
    elif host.startswith('https://'):
        host = host[8:]
    host = host.rstrip('/')
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# Always allow local loopback interfaces for development and internal serverless proxying
for local_host in ['localhost', '127.0.0.1', 'testserver']:
    if local_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(local_host)

# Automatically permit Vercel deployment domains
for vercel_domain in ['.vercel.app', 'resume-agent-backend-kappa.vercel.app']:
    if vercel_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(vercel_domain)

vercel_url = os.getenv('VERCEL_URL', '').strip().rstrip('/')
if vercel_url:
    if vercel_url.startswith('https://'):
        vercel_url = vercel_url[8:]
    elif vercel_url.startswith('http://'):
        vercel_url = vercel_url[7:]
    if vercel_url and vercel_url not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(vercel_url)

# Trust reverse-proxy headers from Vercel edge infrastructure
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Local apps
    'accounts.apps.AccountsConfig',
    'resumes.apps.ResumesConfig',
    'jobs.apps.JobsConfig',
    'analysis.apps.AnalysisConfig',
    'agent.apps.AgentConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
# Supports PostgreSQL via DATABASE_URL or DB_* environment variables,
# with clean fallback to SQLite for local development when PostgreSQL is offline.
DATABASE_URL = os.getenv('DATABASE_URL', '')

if DATABASE_URL.startswith(('postgres://', 'postgresql://')):
    url = urllib.parse.urlparse(DATABASE_URL)
    query_params = urllib.parse.parse_qs(url.query)
    db_options = {}
    if 'sslmode' in query_params:
        db_options['sslmode'] = query_params['sslmode'][0]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': urllib.parse.unquote(url.username or 'postgres'),
            'PASSWORD': urllib.parse.unquote(url.password or ''),
            'HOST': url.hostname or 'localhost',
            'PORT': url.port or 5432,
            'OPTIONS': db_options,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Cache configuration (Rate limiting and performance caching)
# Uses LocMemCache by default for local development and single-instance deployments.
# Automatically switches to Redis if REDIS_URL is configured in production.
REDIS_URL = os.getenv('REDIS_URL', '')
if REDIS_URL.startswith(('redis://', 'rediss://')):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-resume-agent-cache',
        }
    }

# Storage configuration (Django 4.2+)
# Local development uses standard FileSystemStorage within MEDIA_ROOT.
# Structured so production cloud storage (e.g. S3 / Cloudflare R2 / GCS)
# can be activated via DEFAULT_FILE_STORAGE without modifying models.
STORAGES = {
    "default": {
        "BACKEND": os.getenv("DEFAULT_FILE_STORAGE", "django.core.files.storage.FileSystemStorage"),
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Resume uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password Reset Rate Limiting (Phase 4B)
PASSWORD_RESET_RATE_LIMIT = os.getenv('PASSWORD_RESET_RATE_LIMIT', '5/hour')

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'password_reset': PASSWORD_RESET_RATE_LIMIT,
    },
    'EXCEPTION_HANDLER': 'config.exceptions.production_exception_handler',
}

# Simple JWT Configuration: derived from Django SECRET_KEY
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS & CSRF configuration
CORS_ALLOW_ALL_ORIGINS = False
cors_origins_raw = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_raw.split(',') if origin.strip()]
CORS_ALLOW_CREDENTIALS = True

csrf_trusted_raw = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_trusted_raw.split(',') if origin.strip()]

# Sync trusted origins with CORS origins and Vercel domains
for origin in CORS_ALLOWED_ORIGINS:
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

for default_trusted in [
    'https://resume-agent-backend-kappa.vercel.app',
    'https://resume-agent-flame.vercel.app',
    'https://*.vercel.app'
]:
    if default_trusted not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(default_trusted)

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = os.getenv('SECURE_REFERRER_POLICY', 'same-origin')

# Session & CSRF Cookie Security (Environment-driven, preserves HTTP local development)
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False' if DEBUG else 'True').lower() in ('true', '1')
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False' if DEBUG else 'True').lower() in ('true', '1')
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax')

# HTTPS / SSL / HSTS configuration (only active in production when explicitly enabled)
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1') if not DEBUG else False
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ('true', '1')
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'True').lower() in ('true', '1')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# File upload security limits (10 MB max)
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('DATA_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv('FILE_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024))


# Email Configuration (Environment-driven, supports Console and SMTP backends)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '').replace(' ', '').strip()

# Determine default email backend:
# Only default to SMTP if SMTP credentials are provided, or if explicitly configured via EMAIL_BACKEND.
# Otherwise, fall back to console backend so build/import steps without credentials do not crash.
default_email_backend = (
    'django.core.mail.backends.smtp.EmailBackend'
    if (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
    else 'django.core.mail.backends.console.EmailBackend'
)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', default_email_backend)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Resume Agent <noreply@resumeagent.ai>').strip()

# Frontend application URL for password reset and notification links
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173').rstrip('/')

# Password Reset Token Timeout (in seconds: 86400s = 24 hours)
PASSWORD_RESET_TIMEOUT = int(os.getenv('PASSWORD_RESET_TIMEOUT', 86400))

# ==============================================================================
# Production Logging Configuration (Phase 4D)
# ==============================================================================
# Diagnoses application issues in production and development without exposing secrets
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'config': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'analysis': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'resumes': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'jobs': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'agent': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'services': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ==============================================================================
# Production Startup Validation (Phase 4D)
# ==============================================================================
if not DEBUG:
    # 1. Require non-empty, strong SECRET_KEY (32+ chars, non-insecure default)
    if not SECRET_KEY or 'django-insecure' in SECRET_KEY or len(SECRET_KEY) < 32:
        raise ImproperlyConfigured(
            "Production security error: A strong, random SECRET_KEY (32+ characters) is required when DEBUG=False."
        )

    # 2. Prevent wildcard or empty ALLOWED_HOSTS
    if not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
        raise ImproperlyConfigured(
            "Production security error: Wildcard '*' or empty ALLOWED_HOSTS is not permitted when DEBUG=False."
        )

    # 3. Validate SMTP configuration when SMTP backend is active
    if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
        if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
            raise ImproperlyConfigured(
                "Production email error: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set when using smtp.EmailBackend."
            )

