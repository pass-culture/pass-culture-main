from datetime import datetime
import itertools
import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.models as users_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


NPP_DATETIME = datetime(2024, 7, 9, 3, 3)  # 09/07/2024, 03:03
EXCLUDED_OFFERERS_IDS = {
    7938,
    2061,
    3598,
    36110,
    5136,
    4112,
    3094,
    1558,
    40984,
    30237,
    33,
    3106,
    1059,
    20771,
    34596,
    38,
    38955,
    5165,
    1587,
    15923,
    5173,
    1337,
    22844,
    3397,
    4421,
    1610,
    26444,
    16719,
    849,
    37721,
    602,
    3164,
    865,
    41828,
    613,
    43364,
    358,
    3178,
    620,
    2676,
    4214,
    636,
    27275,
    29579,
    2955,
    1422,
    913,
    1426,
    403,
    27288,
    2975,
    675,
    420,
    43429,
    23208,
    5290,
    426,
    1966,
    4016,
    436,
    4025,
    4284,
    192,
    193,
    4290,
    195,
    22211,
    2244,
    25286,
    4038,
    4296,
    203,
    207,
    4047,
    723,
    5332,
    4054,
    217,
    730,
    3810,
    3044,
    229,
    998,
    239,
    499,
    248,
    6907,
    30463,
}
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
            offerers_models.UserOfferer.offererId.not_in(EXCLUDED_OFFERERS_IDS),
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
            offerers_models.UserOfferer.offererId.not_in(EXCLUDED_OFFERERS_IDS),
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
