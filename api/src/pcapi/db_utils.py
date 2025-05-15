import logging
import typing

from sqlalchemy import text

from pcapi import settings
from pcapi.core.offers import models as offers_models
from pcapi.core.reference import models as reference_models
from pcapi.models import db


def install_database_extensions() -> None:
    _create_text_search_configuration_if_not_exists()
    _create_index_btree_gist_extension()
    _create_postgis_extension()


def _create_text_search_configuration_if_not_exists() -> None:
    with db.engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))

        french_unaccent_configuration_query = connection.execute(
            text("SELECT * FROM pg_ts_config WHERE cfgname='french_unaccent';")
        )
        if french_unaccent_configuration_query.fetchone() is None:
            connection.execute(text("CREATE TEXT SEARCH CONFIGURATION french_unaccent ( COPY = french );"))
            connection.execute(
                text(
                    "ALTER TEXT SEARCH CONFIGURATION french_unaccent"
                    " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;"
                )
            )


def _create_index_btree_gist_extension() -> None:
    with db.engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))


def _create_postgis_extension() -> None:
    with db.engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))


def clean_all_database(*args: typing.Any, reset_ids: bool = False, **kwargs: typing.Any) -> None:
logger = logging.getLogger(__name__)

tables_to_keep: list[str] = [
    "alembic_version",
    "spatial_ref_sys",
    offers_models.BookMacroSection.__tablename__,
    reference_models.ReferenceScheme.__tablename__,
    # From unit tests:
    "test_pc_object",
    "test_time_interval",
    if settings.ENV not in ("development", "testing") and not settings.IS_RUNNING_TESTS:
        raise ValueError(f"You cannot do this on this environment: '{settings.ENV}'")

    metadata = sa.MetaData(schema="public")
    metadata.reflect(db.engine)
    table_names = [item for item in metadata.tables.keys() if f"public.{item}" not in tables_to_keep]

    db.session.execute(
        sa.text(f"""
        TRUNCATE {", ".join(table_names)} {"RESTART IDENTITY" if reset_ids else ""};
        """)
    )

    db.session.commit()
    install_feature_flags()
    install_local_providers()
    perm_models.sync_db_permissions(db.session)
    perm_models.sync_db_roles(db.session)
