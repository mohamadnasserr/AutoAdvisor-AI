# AutoAdvisor AI Runbook

This runbook explains how to run the local AutoAdvisor AI MVP on Windows CMD.

## Prerequisites

- Docker Desktop running.
- Python virtual environment created at `.venv`.
- Node.js and npm installed.
- Project dependencies installed.
- `.env` created from `.env.example`.

## Environment Setup

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

If dependencies are already installed, activate the environment only:

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
.venv\Scripts\activate
set PYTHONPATH=%CD%
```

## Run Docker Services

PostgreSQL with pgvector and Redis are provided through Docker Compose.

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
docker compose up -d
```

Check containers:

```cmd
docker compose ps
```

## Seed Demo Data

Seed cars, dealerships, and demo dealer users:

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
.venv\Scripts\activate
set PYTHONPATH=%CD%
python -m scripts.seed_database
```

The seed is idempotent. Re-running it should not duplicate inventory.

## Run Backend

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
.venv\Scripts\activate
set PYTHONPATH=%CD%
uvicorn backend.app.main:app
```

Useful URLs:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Run React Frontend

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI\web-frontend
npm install
npm run dev
```

Main app:

```text
http://localhost:5173
```

Dealer portal:

```text
http://localhost:5173/dealer-dashboard
```

## Optional Streamlit Backup UI

Streamlit remains as a legacy/backup demo dashboard.

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
.venv\Scripts\activate
streamlit run frontend\streamlit_app.py
```

## Reset Demo Leads

Before a clean presentation, clear saved buyer interests:

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
.venv\Scripts\activate
set PYTHONPATH=%CD%
python scripts\reset_demo_leads.py
```

This deletes `DealerLead` rows only. Cars, dealerships, dealer users, RAG documents, and image data are preserved.

## Run Tests

Backend tests:

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
.venv\Scripts\activate
set PYTHONPATH=%CD%
python -m pytest tests
```

React build:

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI\web-frontend
npm run build
```

## Troubleshooting

### Backend routes not active

Restart Uvicorn after adding or changing routes.

```cmd
CTRL+C
uvicorn backend.app.main:app
```

Then check:

```text
http://127.0.0.1:8000/docs
```

### Dealer login fails

Run the seed script to create demo dealer accounts:

```cmd
python -m scripts.seed_database
```

Use one of:

```text
beirut@autoadvisor.demo / demo123
jounieh@autoadvisor.demo / demo123
tripoli@autoadvisor.demo / demo123
```

If tokens stop working after a backend restart, set a stable `DEALER_JWT_SECRET` in `.env`.

### Frontend calls wrong API URL

The React app uses `VITE_API_BASE_URL`, defaulting to:

```text
http://127.0.0.1:8000
```

Create `web-frontend\.env` if needed:

```cmd
echo VITE_API_BASE_URL=http://127.0.0.1:8000> web-frontend\.env
```

Restart `npm run dev` after changing Vite environment variables.

### Database has old leads

Clear demo leads:

```cmd
python scripts\reset_demo_leads.py
```

### sklearn warnings

Some tests or local model loading may print non-blocking scikit-learn warnings if package versions differ from training time. Treat them as warnings unless a test fails.

### Docker not running

Start Docker Desktop, then run:

```cmd
docker compose up -d
docker compose ps
```
