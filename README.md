# AutoAdvisor AI

AutoAdvisor AI is a Lebanon-first, MENA-ready intelligent used-car buying
assistant. It will help users search, compare, and evaluate cars using natural
language, structured inventory, fair-price estimation, grounded automotive
guidance, image analysis, and confirmed dealer inquiry drafts.

## Project Structure

- `backend`: FastAPI application and AI services.
- `frontend`: Streamlit user interface.
- `data`: raw, processed, and seeded project data.
- `docs`: design, data, evaluation, runbook, and reference documents.
- `models`: trained ML artifacts.
- `chroma_db`: local vector store.
- `uploads`: accepted image uploads.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
uvicorn backend.app.main:app --reload
```

In a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend\streamlit_app.py
```

See [the runbook](./docs/RUNBOOK.md) for startup instructions and
[the project reference](./docs/reference/README.md) for scope and priorities.
