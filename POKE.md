1. Run `docker compose -f docker-compose-backend.yml up postgres postgres-legacy redis`.
2. Change the `DATABASE_URL` port to `5434` (new DB with TimescalDB) in `api/.env.local.secret`.
3. In another terminal, run:
   - `alembic upgrade pre@head`
   - `alembic upgrade post@head`
   - `python pcapi/
4. Change the `DATABASE_URL` port to `5435` (legacy DB without TimescalDB) in `api/.env.local.secret`.
5. Run:
   - `alembic upgrade pre@b717eddfe468`
   - `alembic upgrade post@head`
6. Run the SQL query from `api/src/pcapi/scripts/generate_offer_data.sql` in both databases.
