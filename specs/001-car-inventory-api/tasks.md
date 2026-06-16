# Tasks - Car Inventory API

## Completed

- [x] Configure PostgreSQL with Docker Compose.
- [x] Create SQLAlchemy database session and table initialization.
- [x] Define `Car` and `Dealership` SQLAlchemy models.
- [x] Define Pydantic car search response schemas.
- [x] Add `GET /health`.
- [x] Add `GET /cars`.
- [x] Add `GET /cars/{car_id}` with 404 behavior.
- [x] Add `GET /search/cars`.
- [x] Support `budget_max`, `listing_type`, make, model, body type, fuel,
  region, transmission, `max_mileage_km`, and `availability_status` filters.
- [x] Use Pydantic response schemas for inventory API responses.
- [x] Create seeded CSV containing new and used cars.
- [x] Expand curated demo inventory to about 120 cars.
- [x] Seed approximately 80 used cars and 40 new cars.
- [x] Seed 11 demo dealerships.
- [x] Keep `listing_type` and `is_new` consistent in seed data.
- [x] Add representative demo `image_url` values for inventory cars.
- [x] Update seed behavior so existing cars can receive updated `image_url`
  values without duplication.
- [x] Fix and test seed-script repeat-run/idempotency behavior.
- [x] Verify repeat seeding skips existing cars instead of duplicating them.
- [x] Add inventory/search API tests in `tests/test_inventory_api.py`.
- [x] Verify nullable mileage and warranty fields across every API path.

## Missing or Needs Verification

- [ ] Update stale SQLite/ChromaDB documentation and remove or clarify the
  unused SQLite helper in `backend/app/database.py`.
- [ ] Decide whether to add `/cars/search` as an alias or keep only the working
  `/search/cars` route.
- [ ] Add production-grade pagination for larger inventories.

## Verification

- `python -m pytest tests\test_inventory_api.py` -> passed.
- `python -m pytest tests` -> latest full suite passes.
- `cd web-frontend && npm run build` -> passes.
- Manual React inventory demo verified where appropriate.
- Non-blocking warnings may include FastAPI `on_event` deprecation warning and
  Starlette/httpx TestClient warning.
