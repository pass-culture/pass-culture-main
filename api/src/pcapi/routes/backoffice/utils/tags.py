import sqlalchemy.orm as sa_orm

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def get_all_offerer_tags_query() -> sa_orm.Query:
    return (
        db.session.query(offerers_models.OffererTag)
        .order_by(offerers_models.OffererTag.label)
        .options(
            sa_orm.load_only(
                offerers_models.OffererTag.id,
                offerers_models.OffererTag.name,
                offerers_models.OffererTag.label,
            )
        )
    )


def get_validation_tags_query() -> sa_orm.Query:
    return (
        db.session.query(offerers_models.OffererTag)
        .join(offerers_models.OffererTagCategoryMapping)
        .join(offerers_models.OffererTagCategory)
        .filter(offerers_models.OffererTagCategory.name == "homologation")
        .order_by(offerers_models.OffererTag.label)
    )
