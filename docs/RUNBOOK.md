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

## Clean Demo Leads

Before a clean demo, run `python scripts/reset_demo_leads.py` to clear saved
buyer interests. This deletes dealer leads only; inventory, dealerships, RAG
documents, and image data are preserved.
