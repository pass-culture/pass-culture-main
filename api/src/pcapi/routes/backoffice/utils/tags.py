import sqlalchemy.orm as sa_orm

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def get_validation_tags_query() -> sa_orm.Query:
    return (
        db.session.query(offerers_models.OffererTag)
        .join(offerers_models.OffererTagCategoryMapping)
        .join(offerers_models.OffererTagCategory)
        .filter(offerers_models.OffererTagCategory.name == "homologation")
        .order_by(offerers_models.OffererTag.label)
    )
