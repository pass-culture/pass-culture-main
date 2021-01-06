from sqlalchemy import orm
from sqlalchemy.exc import ProgrammingError

from pcapi.models.db import db
from pcapi.models.db import versioning_manager
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository


def install_activity() -> None:
    orm.configure_mappers()

    create_versionning_tables()

    db.session.commit()


def install_features() -> None:
    Feature.query.delete()
    features = []
    for toggle in FeatureToggle:
        feature = Feature()
        feature.populate_from_dict(
            {"description": toggle.value, "name": toggle.name, "isActive": toggle.name != "APPLY_BOOKING_LIMITS_V2"}
        )
        features.append(feature)
    repository.save(*features)


def create_versionning_tables() -> None:
    # FIXME: This is seriously ugly... (based on https://github.com/kvesteri/postgresql-audit/issues/21)
    try:
        versioning_manager.transaction_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass
    try:
        versioning_manager.activity_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass
