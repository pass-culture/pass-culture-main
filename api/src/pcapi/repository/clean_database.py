import logging
import typing

import sqlalchemy as sa

from pcapi import settings
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.reference import models as reference_models
from pcapi.local_providers.install import install_local_providers
from pcapi.models import db
from pcapi.models.feature import install_feature_flags


logger = logging.getLogger(__name__)

tables_to_keep: list[str] = [
    "alembic_version",
    "spatial_ref_sys",
    offers_models.BookMacroSection.__tablename__,
    reference_models.ReferenceScheme.__tablename__,
    # From unit tests:
    "test_pc_object",
    "test_time_interval",
]


def clean_all_database(*args: typing.Any, reset_ids: bool = False, **kwargs: typing.Any) -> None:
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
