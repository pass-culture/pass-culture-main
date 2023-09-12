from sqlalchemy.orm import joinedload

from pcapi.core.history import models


def find_all_actions_by_user(user_id: int) -> list[models.ActionHistory]:
    return (
        models.ActionHistory.query.filter(models.ActionHistory.userId == user_id)
        .order_by(models.ActionHistory.actionDate.desc())
        .options(joinedload(models.ActionHistory.authorUser))
        .all()
    )
