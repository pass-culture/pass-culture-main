from postgresql_audit.flask import versioning_manager
from sqlalchemy import orm
from sqlalchemy.exc import ProgrammingError

from models import PcObject
from models.db import db
from models.feature import FeatureToggle, Feature


def create_text_search_configuration_if_not_exists():
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

    french_unaccent_configuration_query = db.engine.execute(
        "SELECT * FROM pg_ts_config WHERE cfgname='french_unaccent';")
    if french_unaccent_configuration_query.fetchone() is None:
        db.engine.execute("CREATE TEXT SEARCH CONFIGURATION french_unaccent ( COPY = french );")
        db.engine.execute(
            "ALTER TEXT SEARCH CONFIGURATION french_unaccent ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;")


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


def install_database_extensions():
    create_text_search_configuration_if_not_exists()


def install_models():
    orm.configure_mappers()

    create_versionning_tables()

    db.create_all()
    db.session.commit()


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
    PcObject.save(*features)
