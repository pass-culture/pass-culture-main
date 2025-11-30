- Docker Compose services:
  - `postgres`: Current DB (PostgreSQL + PostGIS), kept as is for comparison. Port: `5434`.
  - `timescaledb`: Poke DB (PostgreSQL + PostGIS + TimescaleDB). Port: `5435`.

## Prepare

```sh
podman compose -f ./docker-compose-backend.yml down -v
podman compose -f ./docker-compose-backend.yml up postgres timescaledb
```

```sh
./scripts/prepare/migrate.sh
```

## Seed

All seeding scripts now insert identical data into both databases (postgres on port 5434 and timescaledb on port 5435) in a single run, ensuring a fair comparison for benchmarking.

### Base entities

- user
- deposit
- offerer
- address
- offerer_address

```sh
python ./scripts/seed/01-seed_base_entities.py --num-users 100 --num-offerers 100
```
