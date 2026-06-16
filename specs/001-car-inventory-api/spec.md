# 001 - Car Inventory API

## Goal

Store curated new and used vehicle inventory in PostgreSQL and expose it through
FastAPI using validated Pydantic responses.

## Current State

- PostgreSQL runs from `docker-compose.yml` using `pgvector/pgvector:pg16`.
- FastAPI creates SQLAlchemy tables at startup for the local MVP.
- `GET /health`, `GET /cars`, `GET /cars/{car_id}`, and `GET /search/cars`
  are implemented.
- The curated demo inventory has been expanded to about 120 cars:
  approximately 80 used cars and 40 new cars.
- The seed data includes 11 demo dealerships.
- Seed data includes representative `image_url` values for frontend cards.
- `scripts/seed_database.py` remains idempotent: repeated runs skip duplicate
  cars and can update existing image URLs without creating duplicate listings.
- Inventory is curated demo data, not live scraped marketplace data.

## Car Data Model

The SQLAlchemy `Car` model includes:

- Identity/link: `id`, `dealer_id`
- Listing state: `listing_type`, `is_new`, `availability_status`,
  `platform_source`
- Vehicle identity: `make`, `model`, `trim`, `year`
- Price/use: `price_usd`, `mileage_km`
- Attributes: `body_type`, `fuel`, `transmission`, `color`, `condition`
- New-car detail: `warranty_years`
- Market: `region`
- Demo visual: optional `image_url`

Nullable fields must remain safe across seeding, API serialization,
recommendation output, comparison, and frontend display.

## API Requirements

- Keep `GET /search/cars` as the working filtered search route.
- Keep `GET /cars` for inventory listing.
- Keep `GET /cars/{car_id}` with a clear 404 response.
- Search supports budget, listing type, make, model, body type, fuel, region,
  transmission, maximum mileage, and availability status where applicable.
- Responses use `CarResponse` or related Pydantic response schemas.

## Product Rules

- Support both new and used listings.
- New cars may use zero or nullable mileage and usually have warranty data.
- Used cars are the target for fair-price estimation.
- New cars support search, comparison, warranty/zero-mileage alternatives, and
  reference pricing.
- Treat inventory as curated demo data unless an approved source is added.
- Do not claim live availability unless the data comes from seeded or approved
  inventory.
- Do not use unauthorized scraping.

## Acceptance Criteria

- API starts without errors.
- PostgreSQL container runs.
- Seed script inserts new and used cars without duplicate rows.
- Search filters by budget, `listing_type`, make, body type, fuel, region,
  transmission, mileage, and availability status where supported.
- Missing values such as `warranty_years`, `mileage_km`, and `image_url` do not
  crash seeding, search, serialization, recommendation output, or frontend
  cards.
- Responses use Pydantic schemas.
- Inventory and detail endpoints have automated API tests.
