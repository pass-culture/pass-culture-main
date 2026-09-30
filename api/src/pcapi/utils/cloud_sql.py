"""Native Cloud SQL connection using IAM authentication.

When ``settings.DATABASE_USE_IAM_AUTH`` is enabled (static/production GKE environments), the app
connects to Cloud SQL in-process through the Cloud SQL Python Connector — no Auth Proxy sidecar
and no stored database password. The connector is used as a SQLAlchemy ``creator`` with the
``pg8000`` driver and ``enable_iam_auth=True``; it handles mTLS, instance discovery and IAM
access-token minting/refresh.

Local and preview environments keep the user/password ``psycopg2`` connection: there
``get_engine_kwargs()`` returns an empty mapping and none of the connector code runs.
"""

import logging
import threading
import typing

from google.cloud.sql.connector import Connector

from pcapi import settings


logger = logging.getLogger(__name__)


class _ConnectorHolder:
    lock = threading.Lock()
    connector: Connector | None = None


def _get_connector() -> Connector:
    """Return the process-local Cloud SQL ``Connector``, creating it on first use."""
    with _ConnectorHolder.lock:
        if _ConnectorHolder.connector is None:
            _ConnectorHolder.connector = Connector(refresh_strategy="lazy")
            logger.info(
                "Created Cloud SQL connector",
                extra={"instance_connection_name": settings.DATABASE_INSTANCE_CONNECTION_NAME},
            )
        return _ConnectorHolder.connector


def get_iam_connection() -> typing.Any:
    """Open a new connection to Cloud SQL authenticated with IAM."""
    try:
        return _get_connector().connect(
            settings.DATABASE_INSTANCE_CONNECTION_NAME,
            settings.DATABASE_DRIVER,
            user=settings.DATABASE_IAM_USER,
            db=settings.DATABASE_NAME,
            ip_type=settings.DATABASE_IP_TYPE,
            enable_iam_auth=True,
        )
    except Exception:
        logger.exception(
            "Could not open IAM connection to Cloud SQL",
            extra={
                "instance_connection_name": settings.DATABASE_INSTANCE_CONNECTION_NAME,
                "iam_user": settings.DATABASE_IAM_USER,
                "database": settings.DATABASE_NAME,
                "ip_type": settings.DATABASE_IP_TYPE,
            },
        )
        raise


def get_engine_kwargs() -> dict:
    """Extra ``create_engine`` kwargs shared by every engine-creation site.

    Returns a ``creator`` when IAM auth is enabled, else an empty mapping so the default
    user/password behavior is untouched.
    """
    if settings.DATABASE_USE_IAM_AUTH:
        return {"creator": get_iam_connection}

    return {}


def dispose_connector() -> None:
    """Close and reset the process-local connector (called before forking Gunicorn workers)."""
    with _ConnectorHolder.lock:
        if _ConnectorHolder.connector is not None:
            try:
                _ConnectorHolder.connector.close()
            except Exception:
                logger.exception("Could not close Cloud SQL connector")
            _ConnectorHolder.connector = None


def apply_session_timeouts(
    dbapi_connection: typing.Any,
    *,
    lock_timeout: int = 0,
    statement_timeout: int = 0,
    idle_in_transaction_session_timeout: int = 0,
) -> None:
    """Apply server-side timeouts (in ms) via ``SET SESSION`` statements.

    In user/password mode these are passed through the libpq ``options`` connect arg, which is
    ``psycopg2``-specific and unsupported by ``pg8000``. This helper reproduces the same effect on
    a pg8000 connection from a SQLAlchemy ``connect`` event. Timeouts left at ``0`` are skipped.
    """
    statements = []
    if lock_timeout:
        statements.append(f"SET SESSION lock_timeout = {int(lock_timeout)}")
    if statement_timeout:
        statements.append(f"SET SESSION statement_timeout = {int(statement_timeout)}")
    if idle_in_transaction_session_timeout:
        statements.append(
            f"SET SESSION idle_in_transaction_session_timeout = {int(idle_in_transaction_session_timeout)}"
        )
    if not statements:
        return

    # Run outside a transaction so the settings are not rolled back and no transaction is left open
    # on the pooled connection (see SQLAlchemy "setting alternate search paths on connect" recipe).
    existing_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    try:
        for statement in statements:
            cursor.execute(statement)
    finally:
        cursor.close()
        dbapi_connection.autocommit = existing_autocommit
