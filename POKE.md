- Docker Compose services:
  - `postgres`: Current DB (PostgreSQL + PostGIS), kept as is for comparison. Port: `5434`.
  - `timescaledb`: Poke DB (PostgreSQL + PostGIS + TimescaleDB). Port: `5435`.

## Prepare

```sh
podman compose -f ./docker-compose-backend.yml down -v
podman compose -f ./docker-compose-backend.yml up postgres timescaledb

cd api
# Old Postgre service migrations (port 5434)
alembic upgrade pre@head
alembic upgrade post@head
# New TimescaleDB service migrations (port 5435)
DATABASE_URL_OVERRIDE="postgresql://pass_culture:passq@localhost:5435/pass_culture" alembic upgrade pre@head
DATABASE_URL_OVERRIDE="postgresql://pass_culture:passq@localhost:5435/pass_culture" alembic upgrade post@head
# New TimescaleDB service specific migrations ('booking' table conversion to hypertable)
alembic -c alembic_timescaledb.ini upgrade head
cd ..
```

## Seed

```sh
```
