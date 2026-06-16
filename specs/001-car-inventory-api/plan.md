# Plan - Car Inventory API

## Existing Components

- `backend/app/main.py`: startup initialization, health route, routers.
- `backend/app/api/car_routes.py`: `/cars`, `/cars/{car_id}`, and
  `/search/cars`.
- `backend/app/models/db_models.py`: SQLAlchemy inventory/dealership models.
- `backend/app/models/schemas.py`: car response and search response schemas.
- `backend/app/db/database.py`: PostgreSQL SQLAlchemy engine/session.
- `scripts/seed_database.py`: CSV-to-PostgreSQL seed process.
- `data/seed/cars.csv`: curated new/used demo inventory with representative
  image URLs.
- `docker-compose.yml`: PostgreSQL service.

## Implementation Approach

1. Preserve `/search/cars` and reusable query/filter logic.
2. Keep `/cars` and `/cars/{car_id}` as stable inventory APIs.
3. Reuse Pydantic car response schemas across inventory, recommendation,
   comparison, dealer lead, and similar-car workflows.
4. Keep seed script idempotent and safe for repeat local demos.
5. Allow seed reruns to update representative image URLs without duplicating
   cars.
6. Add API tests covering new/used listings, filters, 404s, nullable fields, and
   optional image URLs.
7. Document PostgreSQL as the active database and keep Alembic as a future
   production hardening step.

## Validation

- Run `docker compose up -d`.
- Run the seed script twice and verify stable row counts.
- Exercise health, list, detail, and search routes.
- Confirm seeded counts are approximately 120 cars and 11 dealerships.
- Confirm new and used listing counts and nullable-field serialization.

## Future Improvements

- Add pagination and validated filter enums.
- Add database indexes based on measured query needs.
- Introduce Alembic only after the schema stabilizes.
- Replace curated demo seed data with approved dealer feeds or marketplace
  partnerships in production.
