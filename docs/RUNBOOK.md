# Runbook

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
```

## Start Backend

```powershell
uvicorn backend.app.main:app --reload
```

## Start Frontend

```powershell
streamlit run frontend\streamlit_app.py
```

The backend health endpoint is available at `http://localhost:8000/health`.
