from postgresql_audit.flask import versioning_manager
from sqlalchemy import orm
from sqlalchemy.exc import ProgrammingError

import models
from models import DiscoveryViewV3
from models.db import db
from models.feature import FeatureToggle, Feature
from repository import repository, discovery_view_queries


def install_database_extensions():
    create_text_search_configuration_if_not_exists()
    create_index_btree_gist_extension()
    create_postgis_extension()


def install_models():
    orm.configure_mappers()

    create_versionning_tables()

    for db_model in models.models:
        model_to_create = db_model.__table__
        model_to_create.create(bind=db.engine, checkfirst=True)

    db.session.commit()


def install_materialized_views():
    discovery_view_queries.create(db.session)
    DiscoveryViewV3(session=db.session).create()


def install_features():
    Feature.query.delete()
    features = []
    for toggle in FeatureToggle:
        feature = Feature()
        feature.populate_from_dict(
            {
                'description': toggle.value,
                'name': toggle,
                'is_active': True
            }
        )
        features.append(feature)
    repository.save(*features)


def create_text_search_configuration_if_not_exists():
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

    french_unaccent_configuration_query = db.engine.execute(
        "SELECT * FROM pg_ts_config WHERE cfgname='french_unaccent';")
    if french_unaccent_configuration_query.fetchone() is None:
        db.engine.execute("CREATE TEXT SEARCH CONFIGURATION french_unaccent ( COPY = french );")
        db.engine.execute(
            "ALTER TEXT SEARCH CONFIGURATION french_unaccent"
            " ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;")


def create_versionning_tables():
    # FIXME: This is seriously ugly... (based on https://github.com/kvesteri/postgresql-audit/issues/21)
    try:
        versioning_manager.transaction_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass
    try:
        versioning_manager.activity_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass


def create_index_btree_gist_extension():
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")


def create_postgis_extension():
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
