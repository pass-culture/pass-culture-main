import logging
import typing

import sqlalchemy as sa

from pcapi import settings
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.reference import models as reference_models
from pcapi.local_providers.install import install_local_providers
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.feature import install_feature_flags


logger = logging.getLogger(__name__)

tables_to_keep: list[type[Model]] = [
    offers_models.BookMacroSection,
    reference_models.ReferenceScheme,
]


def clean_all_database(*args: typing.Any, reset_ids: bool = False, **kwargs: typing.Any) -> None:
    if settings.ENV not in ("development", "testing") and not settings.IS_RUNNING_TESTS:
        raise ValueError(f"You cannot do this on this environment: '{settings.ENV}'")

    table_names = {table.name for table in Base.metadata.sorted_tables if not table.name.startswith("test_")}

    for name in table_names:
        logger.info("## %s", name)

    for table_to_keep in tables_to_keep:
        table_names.remove(table_to_keep.__tablename__)

    db.session.execute(
        sa.text(f"""
        TRUNCATE {", ".join([f'"{name}"' for name in table_names])} {"RESTART IDENTITY" if reset_ids else ""};
        """)
    )

    db.session.commit()
    install_feature_flags()
    install_local_providers()
    perm_models.sync_db_permissions(db.session)
    perm_models.sync_db_roles(db.session)
