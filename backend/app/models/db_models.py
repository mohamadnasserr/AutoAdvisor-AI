from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base
from pgvector.sqlalchemy import Vector


class Dealership(Base):
    __tablename__ = "dealerships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supported_brands: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[str] = mapped_column(String(100), default="Lebanon")

    cars = relationship("Car", back_populates="dealer")
    dealer_users = relationship("DealerUser", back_populates="dealership")


class DealerUser(Base):
    __tablename__ = "dealer_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dealership_id: Mapped[int] = mapped_column(
        ForeignKey("dealerships.id"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="dealer_admin", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    dealership = relationship("Dealership", back_populates="dealer_users")


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    listing_type: Mapped[str] = mapped_column(String(30), default="used", index=True)
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)

    make: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    trim: Mapped[str | None] = mapped_column(String(100), nullable=True)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)

    mileage_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    body_type: Mapped[str] = mapped_column(String(80), nullable=False)
    fuel: Mapped[str] = mapped_column(String(80), nullable=False)
    transmission: Mapped[str] = mapped_column(String(80), nullable=False)
    color: Mapped[str | None] = mapped_column(String(80), nullable=True)

    condition: Mapped[str | None] = mapped_column(String(80), default="Good")
    warranty_years: Mapped[float | None] = mapped_column(Float, nullable=True)

    region: Mapped[str] = mapped_column(String(100), default="Lebanon")
    availability_status: Mapped[str] = mapped_column(String(50), default="demo_available")
    platform_source: Mapped[str] = mapped_column(String(100), default="seeded_demo")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    dealer_id: Mapped[int | None] = mapped_column(ForeignKey("dealerships.id"), nullable=True)
    dealer = relationship("Dealership", back_populates="cars")


class CarReview(Base):
    __tablename__ = "car_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    make: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(150), default="curated_demo")


class DealerLead(Base):
    __tablename__ = "dealer_leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    selected_car_id: Mapped[int | None] = mapped_column(ForeignKey("cars.id"), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_contact_method: Mapped[str | None] = mapped_column(String(80), nullable=True)
    message_draft: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)

class ImageAnalysis(Base):
    __tablename__ = "image_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    safe_image: Mapped[bool] = mapped_column(Boolean, default=True)
    nsfw_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    quality_status: Mapped[str] = mapped_column(String(80), nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    blur_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    brightness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    vehicle_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_color: Mapped[str | None] = mapped_column(String(80), nullable=True)
    detected_body_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    predicted_make_model: Mapped[str | None] = mapped_column(String(150), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)


class EvalResult(Base):
    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    eval_name: Mapped[str] = mapped_column(String(150), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(150), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
