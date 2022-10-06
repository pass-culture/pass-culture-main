from pcapi.core.history import models


def find_all_actions_by_offerer(offerer_id: int) -> list[models.ActionHistory]:
    return (
        models.ActionHistory.query.filter(models.ActionHistory.offererId == offerer_id)
        .order_by(models.ActionHistory.actionDate.desc())
        .all()
    )
