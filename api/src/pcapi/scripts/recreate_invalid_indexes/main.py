"""Recreate invalid indexes.

This script is a Python version of the main.sql script. It drops and recreates
a list of indexes that have been reported as invalid.

It's designed to be run manually to fix database index issues.
"""

import argparse
import logging

import sqlalchemy as sa
import sqlalchemy.exc

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


INDEXES_TO_RECREATE = [
    ("ix_recredit_depositId", 'ON public."recredit" USING btree ("depositId")'),
    (
        "idx_product_trgm_name",
        'ON public."product" USING gin (name gin_trgm_ops)',
    ),
    (
        "ix_achievement_bookingId",
        'ON public."achievement" USING btree ("bookingId")',
    ),
    (
        "ix_artist_alias_trgm_unaccent_name",
        'ON public."artist_alias" USING gin (immutable_unaccent(artist_alias_name) gin_trgm_ops)',
    ),
    (
        "ix_artist_trgm_unaccent_name",
        'ON public."artist" USING gin (immutable_unaccent(name) gin_trgm_ops)',
    ),
    (
        "ix_chronicle_productIdentifier",
        'ON public."chronicle" USING btree ("productIdentifier")',
    ),
    (
        "ix_collective_offer_locationType_offererAddressId",
        'ON public."collective_offer" USING btree ("locationType", "offererAddressId")',
    ),
    (
        "ix_collective_offer_template_locationType_offererAddressId",
        'ON public."collective_offer_template" USING btree ("locationType", "offererAddressId")',
    ),
    (
        "ix_user_departementCode",
        'ON public."user" USING btree ("departementCode") WHERE "departementCode" IS NOT NULL',
    ),
    (
        "ix_validation_rule_collective_offer_link_collectiveOfferId",
        'ON public."validation_rule_collective_offer_link" USING btree ("collectiveOfferId")',
    ),
    (
        "ix_validation_rule_collective_offer_template_link_colle_8ea2",
        'ON public."validation_rule_collective_offer_template_link" USING btree ("collectiveOfferTemplateId")',
    ),
]


def create_index(connection: sa.engine.Connection, index_name: str, index_definition: str, max_retries: int) -> None:
    logger.info(f"Creating index {index_name}...")
    attempts = 0
    retry = True
    while retry and attempts < max_retries:
        attempts += 1
        retry = False
        try:
            connection.execute(sa.text(f'CREATE INDEX CONCURRENTLY IF NOT EXISTS "{index_name}" {index_definition};'))
        except sqlalchemy.exc.OperationalError as exc:
            logger.info(f"Failed to create index {index_name}: {exc}")
            if "lock timeout" in str(exc):
                retry = True
                logger.info("Failed due to lock timeout, retrying...")
        else:
            logger.info(f"Created index {index_name}")


def recreate_invalid_indexes(lock_timeout: int, statement_timeout: int, max_retries: int) -> None:
    logger.info("Dropping indexes...")
    with db.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for index_name, _ in INDEXES_TO_RECREATE:
            conn.execute(sa.text(f'DROP INDEX CONCURRENTLY IF EXISTS "{index_name}";'))
            logger.info(f"Dropped index {index_name}")

    logger.info("Recreating indexes...")
    with db.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(sa.text(f"SET SESSION statement_timeout = '{statement_timeout}s';"))
        conn.execute(sa.text(f"SET SESSION lock_timeout = '{lock_timeout}s';"))
        for index_name, index_definition in INDEXES_TO_RECREATE:
            create_index(conn, index_name, index_definition, max_retries=max_retries)

        conn.execute(sa.text(f"SET SESSION statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT};"))

    logger.info("Checking for invalid indexes...")
    statement = """
      select relname from pg_class
      join pg_index on pg_index.indexrelid = pg_class.oid
      where pg_index.indisvalid = false
    """
    res = db.session.execute(sa.text(statement))
    names = sorted(row[0] for row in res.fetchall())
    if names:
        logger.error("Found invalid PostgreSQL indexes: %s", names)
    else:
        logger.info("No invalid PostgreSQL indexes found")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--lock-timeout", type=int, default=5)
    parser.add_argument("--statement-timeout", type=int, default=3600)
    parser.add_argument("--max-retries", type=int, default=10)
    args = parser.parse_args()

    recreate_invalid_indexes(args.lock_timeout, args.statement_timeout, args.max_retries)
