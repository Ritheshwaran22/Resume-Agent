# Resume Agent — Production Deployment Guide & Checklist (Phase 4E)

This document outlines the deployment architecture, configuration steps, and environment requirements for deploying the Resume Agent application into production.

---

## 1. Architecture Overview

```text
[ React / Vite Frontend (SPA) ]
             |
             | HTTPS (REST API requests via VITE_API_BASE_URL)
             v
[ Django REST Framework (WSGI / Gunicorn) ]
             |
             +---> Managed PostgreSQL Database (DATABASE_URL)
             |
             +---> Persistent Media Storage (resumes/)
             |
             +---> Google Gemini API (GEMINI_API_KEY)
             |
             +---> SMTP Email Delivery (Gmail / SendGrid / SES)
             |
             +---> Distributed Cache / Redis (Optional: multi-instance rate limiting)
```

---

## 2. Environment Variables Specification

### Backend Configuration (`backend/.env`)

| Variable | Required in Production | Description / Format | Example Value |
| :--- | :---: | :--- | :--- |
| `DEBUG` | **Yes** | Must be `False` in production | `False` |
| `SECRET_KEY` | **Yes** | 50+ char cryptographic random secret | *(Generate with secrets.token_urlsafe(50))* |
| `ALLOWED_HOSTS` | **Yes** | Comma-separated backend domains | `api.resumeagent.ai,resumeagent.ai` |
| `FRONTEND_URL` | **Yes** | Canonical HTTPS URL of the frontend | `https://resumeagent.ai` |
| `CORS_ALLOWED_ORIGINS` | **Yes** | Explicit allowed frontend origins | `https://resumeagent.ai` |
| `CSRF_TRUSTED_ORIGINS` | **Yes** | Explicit trusted CSRF origins | `https://resumeagent.ai` |
| `DATABASE_URL` | **Yes** | Managed PostgreSQL connection URI | `postgres://user:pass@host:5432/dbname?sslmode=require` |
| `GEMINI_API_KEY` | **Yes** | Google Gemini API key for analysis | `AIzaSy...` |
| `EMAIL_BACKEND` | **Yes** | Production SMTP email backend | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | **Yes** | SMTP server hostname | `smtp.gmail.com` |
| `EMAIL_PORT` | **Yes** | SMTP port (typically 587 for TLS) | `587` |
| `EMAIL_USE_TLS` | **Yes** | Enable TLS encryption | `True` |
| `EMAIL_HOST_USER` | **Yes** | SMTP username / sender account | `noreply@resumeagent.ai` |
| `EMAIL_HOST_PASSWORD` | **Yes** | SMTP App Password / API token | `your-16-char-app-password` |
| `DEFAULT_FROM_EMAIL` | **Yes** | Display sender in outgoing emails | `Resume Agent <noreply@resumeagent.ai>` |
| `PASSWORD_RESET_RATE_LIMIT`| No | Throttle rate for reset requests | `5/hour` (Default) |
| `SECURE_SSL_REDIRECT` | Recommended | Redirect all HTTP traffic to HTTPS | `True` |
| `SESSION_COOKIE_SECURE` | Recommended | Restrict session cookie to HTTPS | `True` |
| `CSRF_COOKIE_SECURE` | Recommended | Restrict CSRF cookie to HTTPS | `True` |
| `SECURE_HSTS_SECONDS` | Recommended | HTTP Strict Transport Security | `31536000` (1 year) |
| `REDIS_URL` | Optional | Shared cache for multi-instance DRF | `redis://default:pass@redis-host:6379/0` |
| `DEFAULT_FILE_STORAGE` | Optional | Cloud storage class (S3/R2/GCS) | `django.core.files.storage.FileSystemStorage` |

### Frontend Configuration (`frontend/.env`)

| Variable | Required in Production | Description | Example Value |
| :--- | :---: | :--- | :--- |
| `VITE_API_BASE_URL` | **Yes** | Deployed backend HTTPS domain | `https://api.resumeagent.ai` |

> [!CAUTION]
> **Client-Side Secret Warning:** `VITE_*` environment variables are bundled into browser-visible JavaScript. Never place `SECRET_KEY`, `GEMINI_API_KEY`, SMTP passwords, or database credentials in frontend configuration.

---

## 3. Build & Deployment Commands

### Backend Deployment Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```
3. **Collect static assets:**
   ```bash
   python manage.py collectstatic --no-input
   ```
4. **Start WSGI HTTP Server:**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   ```

*(PaaS platforms such as Railway, Render, or Heroku will automatically detect `Procfile` and `runtime.txt`)*

### Frontend Deployment Steps

1. **Install dependencies:**
   ```bash
   npm install
   ```
2. **Compile production bundle:**
   ```bash
   npm run build
   ```
3. **Serve output:**
   Host the generated `dist/` directory via a static site hosting platform (e.g., Cloudflare Pages, Vercel, Netlify, AWS S3/CloudFront) with client-side SPA routing rewrite (`/*` -> `/index.html`).

---

## 4. Current State vs. Future Infrastructure Requirements

### What Is Implemented Now (Phase 4E Ready)
- [x] Environment-driven settings with automated local fallbacks (`DEBUG=True`, SQLite).
- [x] Production startup validation requiring strong `SECRET_KEY` and non-wildcard `ALLOWED_HOSTS` when `DEBUG=False`.
- [x] PostgreSQL database adapter (`psycopg2-binary`) and connection parser supporting `DATABASE_URL` with SSL mode and URL-encoded credentials.
- [x] Static files configuration (`STATIC_ROOT = BASE_DIR / 'staticfiles'`) verified with `collectstatic`.
- [x] WSGI entrypoint (`config.wsgi:application`) and Gunicorn web server dependency.
- [x] PaaS process definition (`Procfile`) and Python runtime specification (`runtime.txt`).
- [x] Flexible storage design (`STORAGES`) that permits switching between local filesystem and cloud object storage via environment variables without modifying Django models.
- [x] Cache abstraction supporting local memory (`LocMemCache`) and Redis (`RedisCache`).
- [x] Centralized error handling and production-safe logging.
- [x] Frontend API URL normalization supporting `VITE_API_BASE_URL`.

### What Is Required Later (Hosting & Infrastructure Provisioning)
- [ ] Domain registration and DNS record configuration.
- [ ] Managed PostgreSQL database instance (e.g. Neon, Supabase, AWS RDS, Railway Postgres).
- [ ] HTTPS / TLS certificates (e.g. Let's Encrypt or Cloudflare automated SSL).
- [ ] Persistent file storage: If hosting the backend in ephemeral container filesystems (e.g., Render, Railway, Heroku), a cloud bucket (AWS S3 or Cloudflare R2 via `django-storages`) or a persistent volume mount must be provisioned for uploaded resume PDFs.
- [ ] Distributed Redis cache: Required if scaling the backend to multiple horizontal server replicas.

---

## 5. Mobile (Android APK) Preparation Note

Before wrapping the React frontend into an Android APK with Capacitor/Cordova:
1. The backend API must be deployed and accessible over a public HTTPS domain.
2. `VITE_API_BASE_URL` must point to the public HTTPS backend.
3. Capacitor dependencies (`@capacitor/core`, `@capacitor/cli`, `@capacitor/android`) will be initialized in a dedicated mobile phase.
