# TimescaleDB Poke

The goal of this technical poke is to compare TimescaleDB performance against our current PostgreSQL setup.

## Description

### Problem

Some queries are currently so slow and heavy that we don't even load them by default when the end-user load the page that should list them.
They first have to set their filters and then click on "Afficher" in order to see those lists.

A good example of such a query is `get_bookings_pro` in `api/src/pcapi/routes/pro/bookings.py`.

### Potential Solution

In my last (unrelated) project, we successfully used [TimescaleDB](https://github.com/timescale/timescaledb) (by TigerData) to massively improve period-based queries.
And period-based queries seem to be a perfect match for our needs regarding bookings and offers.

## Setup

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

- `user`
- `deposit`
- `offerer`
- `address`
- `offerer_address`
- `user_offerer`

```sh
python ./scripts/seed/01-seed_base_entities.py --num-users 100 --num-offerers 100
```

### Venues

- `venue`

```sh
python ./scripts/seed/02-seed_venues.py --num-venues 200
```

### Offers

- `offer`

```sh
python ./scripts/seed/03-seed_offers.py --num-offers 1000
```

### Stocks

- `stock`

```sh
python ./scripts/seed/04-seed_stocks.py --num-stocks 1000
```

### Bookings

- `booking`

```sh
python ./scripts/seed/05-seed_bookings.py --num-bookings 1000

# or, with sharding (CI):
python ./scripts/seed/05-seed_bookings.py --num-bookings 1000 --shard="1/2"
python ./scripts/seed/05-seed_bookings.py --num-bookings 1000 --shard="2/2"
```

## Benchmark

### Baseline (PostgreSQL without TimescaleDB)

```sh
python ./scripts/benchmark/benchmark_bookings_query.py --service postgres --run 10 --output ./results/baseline.json
```

### TimescaleDB with `booking` hypertable

```sh
python ./scripts/benchmark/benchmark_bookings_query.py --service timescaledb --run 10 --output ./results/timescaledb_with_hypertable.json
```

## Notes

- There is no `uv` / `venv` on GHA `benchmark_timescaledb.yml` workflow, that's why scripts are run from `api/` directory.
