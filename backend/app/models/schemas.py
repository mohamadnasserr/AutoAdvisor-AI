from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str


class CarResponse(BaseModel):
    id: int
    listing_type: str
    is_new: bool

    make: str
    model: str
    trim: str | None = None

    year: int
    price_usd: float
    mileage_km: int | None = None

    body_type: str
    fuel: str
    transmission: str
    color: str | None = None

    condition: str | None = None
    warranty_years: float | None = None

    region: str
    availability_status: str
    image_url: str | None = None

    model_config = {"from_attributes": True}


class CarSearchResponse(BaseModel):
    results: list[CarResponse]
    count: int

class PreferenceExtraction(BaseModel):
    budget_max: float | None = None
    budget_min: float | None = None
    region: str | None = "Lebanon"

    listing_type: str | None = None  # used, new, or both

    use_case: str | None = None
    body_type: str | None = None
    fuel: str | None = None
    transmission: str | None = None
    brand_preference: str | None = None

    family_size: int | None = None
    luxury_preference: bool = False
    performance_intent: bool = False
    exotic_intent: bool = False
    style_preference: str | None = None
    priorities: list[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = "default"


class ChatResponse(BaseModel):
    intent: str
    extracted_preferences: PreferenceExtraction
    answer: str
    session_id: str
    recommended_cars: list[CarResponse] = Field(default_factory=list)


class DealerInquiryRequest(BaseModel):
    selected_car_id: int
    user_location: str | None = "Lebanon"
    preferred_contact_method: str | None = "phone"
    confirm_store_lead: bool = False


class DealerInquiryResponse(BaseModel):
    message_draft: str
    stored: bool
    lead_id: int | None = None

class CompareCarsRequest(BaseModel):
    car_ids: list[int] = Field(..., min_length=2, max_length=5)


class CarComparisonItem(BaseModel):
    id: int
    title: str
    listing_type: str
    is_new: bool

    price_usd: float
    year: int
    mileage_km: int | None = None

    body_type: str
    fuel: str
    transmission: str
    condition: str | None = None
    warranty_years: float | None = None

    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    best_use_case: str
    verdict_score: float


class CompareCarsResponse(BaseModel):
    compared_count: int
    cars: list[CarComparisonItem]
    best_overall_car_id: int | None = None
    final_verdict: str


class UsedCarPricePredictionRequest(BaseModel):
    brand: str
    model: str
    vehicle_age: int
    km_driven: int
    seller_type: str = "Dealer"
    fuel_type: str
    transmission_type: str
    mileage: float
    engine: float
    max_power: float
    seats: int


class UsedCarPricePredictionResponse(BaseModel):
    ml_estimated_price_usd: float | None = None
    inventory_reference_price_usd: float | None = None
    estimated_price_usd: float
    fair_price_low_usd: float | None = None
    fair_price_high_usd: float | None = None
    low_estimate_usd: float
    high_estimate_usd: float
    model_mae_usd: float | None = None
    model_r2: float | None = None
    currency: str = "USD"
    calibration_note: str | None = None
    disclaimer: str

class DealerLeadCreateRequest(BaseModel):
    selected_car_id: int
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    user_location: str | None = None
    preferred_contact_method: str | None = "phone"
    budget: float | None = None
    notes: str | None = None


class DealerLeadResponse(BaseModel):
    lead_id: int
    selected_car_id: int | None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    dealership_name: str | None = None
    dealership_location: str | None = None
    dealership_phone: str | None = None
    dealership_email: str | None = None
    message_draft: str
    status: str


class DealerLeadListItem(BaseModel):
    lead_id: int
    status: str
    selected_car_id: int | None = None
    car_title: str
    car_price_usd: float | None = None
    dealership_id: int | None = None
    dealership_name: str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    preferred_contact_method: str | None = None
    budget: float | None = None
    user_location: str | None = None
    notes: str | None = None
    message_draft: str
    created_at: datetime | None = None


class DealershipListItem(BaseModel):
    id: int
    name: str
    location: str
    phone: str | None = None
    email: str | None = None


class DealerLoginRequest(BaseModel):
    email: str
    password: str


class DealerUserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    dealership_id: int
    dealership_name: str
    role: str


class DealerLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    dealer_user: DealerUserProfile

class ImageAnalysisResponse(BaseModel):
    safe_image: bool
    nsfw_score: float | None = None
    safety_reason: str | None = None

    quality_status: str | None = None
    blur_score: float | None = None
    brightness_score: float | None = None
    edge_density: float | None = None
    vehicle_visibility_status: str | None = None
    warnings: list[str] = []

    width: int | None = None
    height: int | None = None
    dominant_color: str | None = None
    estimated_body_type: str | None = None
    analysis_status: str | None = None

    vision_enabled: bool = False
    possible_make: str | None = None
    possible_model: str | None = None
    vision_body_type: str | None = None
    vision_color: str | None = None
    visible_angle: str | None = None
    visible_condition_notes: str | None = None
    damage_or_issue_hints: list[str] = Field(default_factory=list)
    vision_confidence: str | None = None
    vision_reminder: str | None = None

    accepted_for_analysis: bool
    message: str


class SimilarCarsRequest(BaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    mileage_km: int | None = None
    body_type: str | None = None
    fuel: str | None = None
    transmission: str | None = None
    budget_max: float | None = None
    listing_type: str | None = "used"


class SimilarCarsResponse(BaseModel):
    query_summary: str
    similar_cars: list[CarResponse] = Field(default_factory=list)
    explanation: str
