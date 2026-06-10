# 001 - Car Inventory API

## Goal

Store seeded new and used vehicle inventory in PostgreSQL and expose it through
FastAPI using validated Pydantic responses.

## Audited Current State

- PostgreSQL runs from `docker-compose.yml` using `pgvector/pgvector:pg16`.
- FastAPI creates SQLAlchemy tables at startup.
- `GET /health` and `GET /search/cars` are implemented and return HTTP 200.
- `data/seed/cars.csv` contains 16 listings: 10 used and 6 new.
- `scripts/seed_database.py` seeds cars and dealerships.
- The running database contained 16 cars and 6 dealerships during the audit.
- `GET /cars` and `GET /cars/{car_id}` are not implemented.

## Car Data Model

The current SQLAlchemy `Car` model contains:

- Identity/link: `id`, `dealer_id`
- Listing state: `listing_type`, `is_new`, `availability_status`,
  `platform_source`
- Vehicle identity: `make`, `model`, `trim`, `year`
- Price/use: `price_usd`, `mileage_km`
- Attributes: `body_type`, `fuel`, `transmission`, `color`, `condition`
- New-car detail: `warranty_years`
- Market: `region`

`trim`, `mileage_km`, `color`, `condition`, `warranty_years`, and `dealer_id`
may be null. API and seed behavior must tolerate those values.

## API Requirements

- Keep the working `GET /search/cars` route for compatibility.
- Add `GET /cars` for a bounded inventory listing.
- Add `GET /cars/{car_id}` with a clear 404 response.
- Optionally alias `GET /cars/search` to the existing search behavior later.
- Search supports budget, listing type, make, body type, fuel, region,
  transmission, and maximum mileage where applicable.
- Responses use `CarResponse` or a related Pydantic response schema.

## Product Rules

- Support both new and used listings.
- New cars may use zero or nullable mileage and usually have warranty data.
- Used cars are the future ML price-estimation target.
- New cars support search, comparison, warranty/zero-mileage alternatives, and
  reference pricing.
- Clearly treat inventory as seeded demo data unless an approved source is used.
- Do not use unauthorized scraping.

## Acceptance Criteria

- API starts without errors.
- PostgreSQL container runs.
- Seed script inserts new and used cars without duplicate or control-flow errors.
- Search filters by budget, `listing_type`, make, body type, fuel, region,
  transmission, and mileage where supported.
- Missing values such as `warranty_years` or `mileage_km` do not crash seeding,
  search, serialization, or recommendation output.
- Responses use Pydantic schemas.
- Inventory and detail endpoints have automated API tests.
