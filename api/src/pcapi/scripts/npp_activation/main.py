from datetime import datetime
import itertools
import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.models as users_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


NPP_DATETIME = datetime(2024, 7, 9, 3, 3)  # 09/07/2024, 03:03
ROLES_TO_MIGRATE = [
    users_models.UserRole.NON_ATTACHED_PRO,
    users_models.UserRole.PRO,
    users_models.UserRole.ADMIN,
]
BATCH_SIZE = 1000


# Taken out of the Python 3.12 doc
def batched(iterable, n):  # type: ignore[no-untyped-def]
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(itertools.islice(iterator, n)):
        yield batch


def create_UserProNewNavState_for_pro_users(include_admins: bool = False) -> None:
    for user in (
        users_models.User.query.join(users_models.UserProNewNavState, users_models.User.pro_new_nav_state, isouter=True)
        .join(offerers_models.UserOfferer, users_models.User.UserOfferers)
        .filter(
            users_models.User.roles.overlap(ROLES_TO_MIGRATE),
            users_models.UserProNewNavState.id == None,
        )
    ):
        new_npp_state = users_models.UserProNewNavState(
            user=user,
            eligibilityDate=NPP_DATETIME,
            newNavDate=NPP_DATETIME,
        )
        db.session.add(new_npp_state)

    if include_admins:
        for user in users_models.User.query.join(
            users_models.UserProNewNavState, users_models.User.pro_new_nav_state, isouter=True
        ).filter(
            users_models.User.roles.contains([users_models.UserRole.ADMIN]),
            users_models.UserProNewNavState.id == None,
        ):
            new_npp_state = users_models.UserProNewNavState(
                user=user,
                eligibilityDate=NPP_DATETIME,
                newNavDate=NPP_DATETIME,
            )
            db.session.add(new_npp_state)
    db.session.commit()


def fill_empty_UserProNewNavState() -> None:
    # "eligibilityDate" IS NOT NULL AND "newNavDate" IS NULL -> Activation auto du portail
    user_pro_new_nav_state_ids = [
        i[0]
        for i in users_models.User.query.join(
            users_models.UserProNewNavState, users_models.User.pro_new_nav_state, isouter=True
        )
        .join(offerers_models.UserOfferer, users_models.User.UserOfferers)
        .filter(
            users_models.User.roles.overlap(ROLES_TO_MIGRATE),
            users_models.UserProNewNavState.eligibilityDate != None,
            users_models.UserProNewNavState.newNavDate == None,
        )
        .with_entities(users_models.UserProNewNavState.id)
    ]
    for i, batch_ids in enumerate(batched(user_pro_new_nav_state_ids, BATCH_SIZE)):
        print("Batch %s" % i)
        users_models.UserProNewNavState.query.filter(users_models.UserProNewNavState.id.in_(batch_ids)).update(
            {users_models.UserProNewNavState.newNavDate: NPP_DATETIME}, synchronize_session=False
        )
    db.session.commit()


if __name__ == "__main__":
    app.app_context().push()
    create_UserProNewNavState_for_pro_users(include_admins=True)
    fill_empty_UserProNewNavState()
