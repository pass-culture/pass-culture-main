"""Recreate invalid indexes.

This script is a Python version of the main.sql script. It drops and recreates
a list of indexes that have been reported as invalid.

It's designed to be run manually to fix database index issues.

Link to script : https://github.com/pass-culture/pass-culture-main/blob/pc-38005-recreate-invalid-sql-indices/api/src/pcapi/scripts/recreate_invalid_indexes/main.py
"""

import argparse
import logging
import time
import typing
from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

import sqlalchemy as sa
import sqlalchemy.exc

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)

DATE_FORMAT = "%d-%m-%Y:%H:%M"
LOCAL_TZ = ZoneInfo("Europe/Paris")
INDEXES_TO_RECREATE = [
    (
        "ix_recredit_depositId",
        'ON public."recredit" USING btree ("depositId")',
    ),
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
    (
        "ix_highlight_request_highlightId",
        'ON public."highlight_request" USING btree ("highlightId")',
    ),
    (
        "ix_highlight_request_offerId",
        'ON public."highlight_request" USING btree ("offerId")',
    ),
]
INDEXES_TABLE_MAP = {
    "ix_recredit_depositId": 'public."recredit"',
    "idx_product_trgm_name": 'public."product"',
    "ix_achievement_bookingId": 'public."achievement"',
    "ix_artist_alias_trgm_unaccent_name": 'public."artist_alias"',
    "ix_artist_trgm_unaccent_name": 'public."artist"',
    "ix_chronicle_productIdentifier": 'public."chronicle"',
    "ix_collective_offer_locationType_offererAddressId": 'public."collective_offer"',
    "ix_collective_offer_template_locationType_offererAddressId": 'public."collective_offer_template"',
    "ix_user_departementCode": 'public."user"',
    "ix_validation_rule_collective_offer_link_collectiveOfferId": 'public."validation_rule_collective_offer_link"',
    "ix_validation_rule_collective_offer_template_link_colle_8ea2": 'public."validation_rule_collective_offer_template_link"',
    "ix_highlight_request_highlightId": 'public."highlight_request"',
    "ix_highlight_request_offerId": 'public."highlight_request"',
}


@contextmanager
def autocommit_connection(
    lock_timeout: int, statement_timeout: int
) -> typing.Generator[sa.engine.Connection, None, None]:
    with db.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(sa.text(f"SET SESSION statement_timeout = {statement_timeout};"))
        conn.execute(sa.text(f"SET SESSION lock_timeout = {lock_timeout};"))

        yield conn

        conn.execute(sa.text(f"SET SESSION statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT};"))
        conn.execute(sa.text(f"SET SESSION lock_timeout = '{settings.DATABASE_LOCK_TIMEOUT}';"))


def get_temporary_indexes() -> list[str]:
    statement = """
select
        relname
from
        pg_class
        join pg_index on pg_index.indexrelid = pg_class.oid
where
        pg_index.indisvalid = false
        and (relname like '%ccnew%' or relname like '%ccold%');
    """
    res = db.session.execute(sa.text(statement))
    return sorted(row[0] for row in res.fetchall())


def get_invalid_indexes() -> list[str]:
    statement = """
select
        relname
from
        pg_class
        join pg_index on pg_index.indexrelid = pg_class.oid
where
        pg_index.indisvalid = false
        and relname not like '%ccnew%';
    """
    res = db.session.execute(sa.text(statement))
    return sorted(row[0] for row in res.fetchall())


def log_locks_on_table(table_name: str) -> None:
    statement = f"""
SELECT
        age (clock_timestamp (), xact_start) as transaction_time,
        *
FROM    pg_stat_activity
WHERE   pid IN (
    SELECT pid
    FROM pg_locks
    WHERE relation = '{table_name}'::regclass
) ORDER BY transaction_time DESC;
    """
    res = db.session.execute(sa.text(statement))
    logger.info(
        "transaction_time,datid,datname,pid,leader_pid,usesysid,usename,application_name,client_addr,client_hostname,client_port,backend_start,xact_start,query_start,state_change,wait_event_type,wait_event,state,backend_xid,backend_xmin,query_id,query,backend_type"
    )
    for row in list(res.fetchall())[:5]:
        logger.info(row)


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
                log_locks_on_table(INDEXES_TABLE_MAP[index_name])
                logger.info("Failed due to lock timeout, retrying...")
                time.sleep(attempts * 10)
        else:
            logger.info(f"Created index {index_name}")


def drop_index(connection: sa.engine.Connection, index_name: str, max_retries: int) -> None:
    logger.info(f"Dropping index {index_name}...")
    attempts = 0
    retry = True
    while retry and attempts < max_retries:
        attempts += 1
        retry = False
        try:
            connection.execute(sa.text(f'DROP INDEX CONCURRENTLY IF EXISTS "{index_name}";'))
        except sqlalchemy.exc.OperationalError as exc:
            logger.info(f"Failed to drop index {index_name}: {exc}")
            if "lock timeout" in str(exc):
                retry = True
                logger.info("Failed due to lock timeout, retrying...")
                time.sleep(attempts * 10)
            elif "statement timeout" in str(exc):
                retry = True
                logger.info("Failed due to statement timeout, retrying...")
                time.sleep(attempts * 10)
        else:
            logger.info(f"Dropped index {index_name}")


def recreate_invalid_indexes(
    lock_timeout: int, statement_timeout: int, max_retries: int, index_to_recreate: str | None = None
) -> None:
    invalid_indexes = get_invalid_indexes()
    indexes_to_recreate = [index for index in INDEXES_TO_RECREATE if index[0] in invalid_indexes]
    if index_to_recreate:
        indexes_to_recreate = [index_info for index_info in indexes_to_recreate if index_info[0] == index_to_recreate]
        if not indexes_to_recreate:
            logger.info(f"Index {index_to_recreate} is not in the list of invalid indexes.")
            return
    logger.info("Indexes to recreate: %s", [index for index, _ in indexes_to_recreate])
    with autocommit_connection(lock_timeout, statement_timeout) as connection:
        logger.info("Dropping indexes...")
        for index_name, _ in indexes_to_recreate:
            drop_index(connection, index_name, max_retries=max_retries)

    time.sleep(5)  # let's just wait a bit before recreating
    with autocommit_connection(lock_timeout, statement_timeout) as connection:
        logger.info("Recreating indexes...")
        for index_name, index_definition in indexes_to_recreate:
            create_index(connection, index_name, index_definition, max_retries=max_retries)


def log_invalid_indexes() -> None:
    logger.info("Checking for invalid indexes remaining...")
    invalid_indexes_remaining = get_invalid_indexes()
    if invalid_indexes_remaining:
        logger.error("Found invalid PostgreSQL indexes remaining: %s", invalid_indexes_remaining)
    else:
        logger.info("No invalid PostgreSQL indexes found")


def clean_temporary_indexes(lock_timeout: int, statement_timeout: int, max_retries: int) -> None:
    temporary_indexes = get_temporary_indexes()
    logger.info("Removing temporary indexes: %s", temporary_indexes)
    with autocommit_connection(lock_timeout, statement_timeout) as connection:
        for index in temporary_indexes:
            drop_index(connection, index, max_retries)


def create_missing_indexes(lock_timeout: int, statement_timeout: int, max_retries: int) -> None:
    logger.info("Checking for missing indexes...")
    missing_indexes = [index for index in INDEXES_TO_RECREATE if index[0] not in get_invalid_indexes()]
    logger.info("Indexes to create: %s", [index for index, _ in missing_indexes])
    with autocommit_connection(lock_timeout, statement_timeout) as connection:
        for index_name, index_definition in missing_indexes:
            create_index(connection, index_name, index_definition, max_retries=max_retries)


def toggle_feature_flag(is_active: bool) -> None:
    update_feature_query = """
    UPDATE feature
    SET "isActive" = :active_status
    WHERE name = 'ENABLE_RECURRENT_CRON';
    """
    db.session.execute(sa.text(update_feature_query), params={"active_status": is_active})
    db.session.commit()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--lock-timeout", type=int, default=5, help="Lock timeout in seconds")
    parser.add_argument("--statement-timeout", type=int, default=3600, help="Statement timeout in seconds")
    parser.add_argument("--max-retries", type=int, default=10)
    parser.add_argument("--deactivate-cron", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--only-recreate-indexes", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument(
        "--schedule-date",
        type=str,
        default=datetime.now(LOCAL_TZ).strftime(DATE_FORMAT),
        help="Date et heure de planification au format DD-MM-YYYY:HH:MM. Par défaut, l'instant de lancement",
    )
    parser.add_argument("--index", type=str, default=None, help="Nom de l'index à recréer (optionnel)")
    args = parser.parse_args()

    if args.index:
        assert args.index in INDEXES_TABLE_MAP, f"L'index {args.index} n'est pas dans la liste des index gérés"

    statement_timeout = args.statement_timeout * 1000  # en ms
    lock_timeout = args.lock_timeout * 1000  # en ms

    now = int(time.time())
    scheduled_timestamp = int(datetime.strptime(args.schedule_date, DATE_FORMAT).replace(tzinfo=LOCAL_TZ).timestamp())
    if scheduled_timestamp > now:
        time_to_wait = scheduled_timestamp - now
        logger.info("Recréation d'indexes planifiée pour %s. Attente de %s secondes", args.schedule_date, time_to_wait)
        time.sleep(time_to_wait)
        logger.info("Lancement de la recréation d'indexes")

    try:
        if args.deactivate_cron:
            toggle_feature_flag(is_active=False)  # désactive le FF au moment du lancement
        if not args.only_recreate_indexes:
            clean_temporary_indexes(lock_timeout, statement_timeout, args.max_retries)
            create_missing_indexes(lock_timeout, statement_timeout, args.max_retries)
        recreate_invalid_indexes(lock_timeout, statement_timeout, args.max_retries, index_to_recreate=args.index)
        log_invalid_indexes()
    finally:
        if args.deactivate_cron:
            toggle_feature_flag(is_active=True)
