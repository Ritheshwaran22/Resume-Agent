# AI Resume Agent (Full-Stack)

An intelligent, full-stack AI Resume Agent designed to analyze candidate resumes against targeted job descriptions and provide truthful, structured, actionable recommendations without hallucinating qualifications.

Built with **Django (Django REST Framework)** on the backend, **Google ADK & Gemini API** for reasoning, **PostgreSQL** for persistence, **PyMuPDF** for secure text extraction, **Pydantic** for structured output validation, and **React (Vite + Tailwind CSS v4 + Motion)** on the frontend.

---

## 1. High-Level Architecture

```text
React (Vite + Tailwind CSS + Motion)
  ↓ [JWT Authenticated REST Requests]
Django REST Framework (Endpoints & Serializers)
  ↓ [Strict User Isolation & Ownership Checks]
Resume & Job Ingestion Layer
  ↓ [PyMuPDF Safe Stream Text Extraction]
Google ADK Resume Agent
  ├── Tools (Resume Entities, Job Requirements, Overlap Comparison)
  ├── Modular Prompts (Strict Anti-Hallucination & Truthfulness Rules)
  └── Gemini 2.5 / 1.5 Structured Generation
  ↓ [Pydantic ResumeAnalysisOutput Schema Validation]
PostgreSQL / SQLite Database Persistence
  ↓ [JSON Response]
React Analysis Results Dashboard (Score, Skills, Strengths, Questions, Roadmap)
```

---

## 2. Core Features

1. **Authentication & User Data Isolation**:
   - Secure registration, JWT login, token refresh, and profile endpoints via Simple JWT.
   - Per-user foreign key ownership: users cannot access or tamper with other users' resumes, jobs, or analyses.
2. **Resume PDF Processing & PyMuPDF Extraction**:
   - Secure stream-based PDF parsing with PyMuPDF (`pymupdf`).
   - File validation: PDF type checks, 10 MB size limit, empty file detection, corrupted file handling, and scanned/image-only document detection.
3. **Target Job Description Ingestion**:
   - Manages target job titles, full postings, domain keywords, and qualification requirements.
4. **Google ADK & Gemini Resume Agent**:
   - Modular tools: `resume_tools.py`, `job_tools.py`, `analysis_tools.py`.
   - **Strict Truthfulness Rule**: Never invents skills, experiences, degrees, companies, or metrics.
   - Missing qualifications are objectively marked as *"not clearly demonstrated in the resume"*, never claiming the user lacks knowledge.
   - All improvement suggestions are conditional (*"If you have genuinely used Docker, consider adding it..."*).
5. **Pydantic Schema Validation**:
   - Crash-proof JSON schema validation with `ResumeAnalysisOutput`.
6. **Resume-to-Job Match Indicator**:
   - Informational comparison indicator (0-100%) evaluating demonstrated skills against requirements.
   - Explicitly disclaimed: not a hiring probability or ATS guarantee.
7. **Comprehensive Analysis Report**:
   - Matched skills & missing demonstrated skills
   - Informational keyword analysis
   - Project-level relevance & feedback
   - Factual strengths & weaknesses
   - Truthful suggestions
   - Categorized interview questions (Resume, Technical, Project, Job-Specific, Behavioral)
   - Practical 4-week learning roadmap
8. **Analysis History**:
   - Historical tracking of previous resume-to-job evaluations with direct detail views.

---

## 3. Technology Stack

### Backend
- **Python 3.10+**
- **Django 5.x** & **Django REST Framework**
- **PostgreSQL** (via `psycopg2-binary`) with automatic fallback to **SQLite** for development
- **Google ADK & Gemini API** (`google-genai`)
- **PyMuPDF** (`pymupdf`)
- **Pydantic v2** (`pydantic`)
- **Simple JWT** (`djangorestframework-simplejwt`)
- **CORS Headers** (`django-cors-headers`)
- **python-dotenv**

### Frontend
- **React 19**
- **Vite**
- **Tailwind CSS v4** (`@tailwindcss/vite`)
- **Motion** (`motion/react`)
- **Lucide React** (`lucide-react`)
- **Axios**
- **React Router 7** (`react-router-dom`)
- **clsx** & **tailwind-merge**

---

## 4. Project Structure

```text
Resume Agent/
├── .env.example
├── .gitignore
├── README.md
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   ├── db.sqlite3
│   ├── media/
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── accounts/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── resumes/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── jobs/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── analysis/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── agent/
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── schemas.py
│   │   └── tools/
│   │       ├── resume_tools.py
│   │       ├── job_tools.py
│   │       └── analysis_tools.py
│   └── services/
│       ├── ai_service.py
│       ├── pdf_service.py
│       └── security_service.py
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        ├── components/
        │   ├── Button.jsx
        │   ├── Navbar.jsx
        │   ├── Container.jsx
        │   ├── Section.jsx
        │   ├── UploadBox.jsx
        │   ├── ResumeCard.jsx
        │   ├── JobForm.jsx
        │   ├── AnalysisCard.jsx
        │   ├── SkillList.jsx
        │   ├── ProgressIndicator.jsx
        │   ├── InterviewQuestionCard.jsx
        │   ├── Roadmap.jsx
        │   ├── HistoryCard.jsx
        │   ├── LoadingState.jsx
        │   ├── MobileMenu.jsx
        │   ├── ProtectedRoute.jsx
        │   └── ScrollToTop.jsx
        ├── context/
        │   └── AuthContext.jsx
        ├── pages/
        │   ├── HomePage.jsx
        │   ├── HowItWorksPage.jsx
        │   ├── FeaturesPage.jsx
        │   ├── PreviewPage.jsx
        │   ├── DashboardShell.jsx
        │   ├── LoginPage.jsx
        │   ├── RegisterPage.jsx
        │   ├── AnalysisDetailPage.jsx
        │   └── NotFoundPage.jsx
        └── services/
            └── api.js
```

---

## 5. API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health/` | System & API Health Check | No |
| `POST` | `/api/accounts/register/` | User registration (returns tokens & user) | No |
| `POST` | `/api/accounts/login/` | JWT login (returns access, refresh, user) | No |
| `POST` | `/api/accounts/refresh/` | Refresh expired access token | No |
| `GET` | `/api/accounts/me/` | Current user profile | Yes |
| `POST` | `/api/accounts/logout/` | Blacklist token & sign out | Yes |
| `POST` | `/api/resumes/upload/` | Upload PDF & extract text via PyMuPDF | Yes |
| `GET` | `/api/resumes/` | List current user's resumes | Yes |
| `GET` | `/api/resumes/<id>/` | Retrieve user's resume details | Yes |
| `DELETE` | `/api/resumes/<id>/` | Delete user's resume | Yes |
| `POST` | `/api/jobs/` | Create target job description | Yes |
| `GET` | `/api/jobs/` | List user's job descriptions | Yes |
| `GET` | `/api/jobs/<id>/` | Retrieve user's job description | Yes |
| `POST` | `/api/analysis/start/` | Run Google ADK Resume Agent analysis | Yes |
| `GET` | `/api/analysis/` | List user's analysis history | Yes |
| `GET` | `/api/analysis/<id>/` | Retrieve full analysis results | Yes |

---

## 6. Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL (optional for local development; SQLite fallback supported)

### Backend Setup
```bash
cd backend

# Create & activate virtual environment (if not already done)
python -m venv ../venv
..\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env)
cp .env.example .env

# Run database migrations
python manage.py migrate

# Verify Django configuration
python manage.py check

# Run backend development server
python manage.py runserver 127.0.0.1:8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 7. Running Tests

### Backend Unit Tests
```bash
cd backend
python manage.py test
```
Runs 12 comprehensive unit tests covering:
- Account registration, login, password validation, protected routes
- Resume PDF upload, PyMuPDF text extraction, file rejection, ownership isolation
- Job description creation and cross-user isolation
- Resume Agent analysis, match scoring, and Pydantic validation

### Frontend Production Build
```bash
cd frontend
npm run build
```
Compiles and bundles the multi-page React application with 0 errors.

---

## 8. Security & Production Considerations

- **Strict User Isolation**: All database queries filter on `request.user`. User A cannot access, update, or analyze User B's resumes or job postings.
- **Credential Protection**: `GEMINI_API_KEY`, database credentials, and `SECRET_KEY` are kept strictly in backend `.env` and never exposed to the frontend.
- **File Validation**: PyMuPDF parses files from in-memory byte buffers without executing uploaded content. Scanned/image-only PDFs and non-PDFs are rejected with clear error messages.
- **Production Headers**: CORS origins and allowed hosts are restricted via environment variables. For production, set `DEBUG=False` and supply a strong random `SECRET_KEY`.
