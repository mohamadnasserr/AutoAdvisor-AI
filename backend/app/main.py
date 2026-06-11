from fastapi import FastAPI

from backend.app.api.car_routes import router as car_router
from backend.app.api.chat_routes import router as chat_router
from backend.app.config import settings
from backend.app.api.price_routes import router as price_router
from backend.app.db.init_db import init_db
from backend.app.models.schemas import HealthResponse
from backend.app.api.comparison_routes import router as comparison_router


app = FastAPI(
    title="AutoAdvisor AI API",
    description="Lebanon-first, MENA-ready intelligent car-buying assistant.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
    }


app.include_router(chat_router)
app.include_router(car_router)
app.include_router(comparison_router)
app.include_router(price_router)