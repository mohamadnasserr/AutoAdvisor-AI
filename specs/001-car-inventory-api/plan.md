# Plan - Car Inventory API

## Existing Components

- `backend/app/main.py`: startup initialization, health route, routers.
- `backend/app/api/car_routes.py`: current filtered `/search/cars` route.
- `backend/app/models/db_models.py`: SQLAlchemy inventory/dealership models.
- `backend/app/models/schemas.py`: `CarResponse` and `CarSearchResponse`.
- `backend/app/db/database.py`: PostgreSQL SQLAlchemy engine/session.
- `scripts/seed_database.py`: CSV-to-PostgreSQL seed process.
- `data/seed/cars.csv`: mixed new/used demo inventory.
- `docker-compose.yml`: PostgreSQL service.

## Implementation Approach

1. Preserve `/search/cars` and extract reusable query/filter logic only if it
   simplifies adding inventory routes.
2. Add `GET /cars` and `GET /cars/{car_id}` to the existing car router.
3. Reuse `CarResponse`; add a bounded list response only if needed.
4. Fix and verify seed idempotency before relying on repeatable local setup.
5. Add API tests covering new/used listings, filters, 404s, and nullable fields.
6. Document PostgreSQL as the active database; do not introduce Alembic yet.

## Validation

- Run `docker compose up -d`.
- Run the seed script twice and verify stable row counts.
- Exercise health, list, detail, and search routes.
- Confirm new and used listing counts and nullable-field serialization.

## Future Improvements

- Add pagination and validated filter enums.
- Add database indexes based on measured query needs.
- Introduce Alembic only after the schema stabilizes.
