from sqlalchemy import orm
from sqlalchemy.exc import ProgrammingError

from repository.discovery_view_queries import _order_by_digital_offers
from repository.discovery_view_v3_queries import _order_by_digital_offers
from models.db import db, \
    versioning_manager
from models.feature import FeatureToggle, \
    Feature
from repository import repository, \
    discovery_view_queries, \
    discovery_view_v3_queries


def install_models():
    orm.configure_mappers()

    create_versionning_tables()

    db.session.commit()


def install_materialized_views():
    discovery_view_queries.create(db.session, _order_by_digital_offers)
    discovery_view_v3_queries.create(db.session, _order_by_digital_offers)


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
