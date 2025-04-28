from sqlalchemy.orm import joinedload

from pcapi.core.history import models
from pcapi.models import db


def find_all_actions_by_user(user_id: int) -> list[models.ActionHistory]:
    return (
        db.session.query(models.ActionHistory)
        .filter(
            models.ActionHistory.userId == user_id,
            models.ActionHistory.actionType != models.ActionType.FRAUD_INFO_MODIFIED,
        )
        .order_by(models.ActionHistory.actionDate.desc())
        .options(joinedload(models.ActionHistory.authorUser))
        .all()
    )
