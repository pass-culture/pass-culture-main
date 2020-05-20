
from models.db import db


def install_database_extensions(app):
    with app.app_context():
        _create_text_search_configuration_if_not_exists()
        _create_index_btree_gist_extension()
        _create_postgis_extension()


def _create_text_search_configuration_if_not_exists():
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

    french_unaccent_configuration_query = db.engine.execute(
        "SELECT * FROM pg_ts_config WHERE cfgname='french_unaccent';")
    if french_unaccent_configuration_query.fetchone() is None:
        db.engine.execute("CREATE TEXT SEARCH CONFIGURATION french_unaccent ( COPY = french );")
        db.engine.execute(
            "ALTER TEXT SEARCH CONFIGURATION french_unaccent"
            " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;")


def _create_index_btree_gist_extension():
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")


def _create_postgis_extension():
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS postgis;")


if __name__ == "__main__":
    from flask_app import app
    install_database_extensions(app)
