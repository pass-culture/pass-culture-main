from sqlalchemy.orm import joinedload

from pcapi.core.history import models
from pcapi.core.users import models as users_models


def find_all_actions_by_offerer(offerer_id: int) -> list[models.ActionHistory]:
    return (
        models.ActionHistory.query.filter(models.ActionHistory.offererId == offerer_id)
        .outerjoin(users_models.User, models.ActionHistory.userId == users_models.User.id)
        .order_by(models.ActionHistory.actionDate.desc())
        .options(joinedload(models.ActionHistory.user))
        .options(joinedload(models.ActionHistory.authorUser))
        .all()
    )
