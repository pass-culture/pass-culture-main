from sqlalchemy import text

from pcapi.models import db


def install_database_extensions() -> None:
    _create_text_search_configuration_if_not_exists()
    _create_index_btree_gist_extension()
    _create_postgis_extension()
    _create_pgcrypto_extension()


def _create_text_search_configuration_if_not_exists() -> None:
    db.engine.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))

    french_unaccent_configuration_query = db.engine.execute(
        text("SELECT * FROM pg_ts_config WHERE cfgname='french_unaccent';")
    )
    if french_unaccent_configuration_query.fetchone() is None:
        db.engine.execute(text("CREATE TEXT SEARCH CONFIGURATION french_unaccent ( COPY = french );"))
        db.engine.execute(
            text(
                "ALTER TEXT SEARCH CONFIGURATION french_unaccent"
                " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;"
            )
        )


def _create_index_btree_gist_extension() -> None:
    db.engine.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))


def _create_postgis_extension() -> None:
    db.engine.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))


def _create_pgcrypto_extension() -> None:
    # The `pgcrypto` is required to use `gen_random_uuid()` until PostgreSQL 13.
    db.engine.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
