import argparse
import logging

from pcapi.app import app
from pcapi.core.subscription.api import activate_beneficiary_if_no_missing_step
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

user_ids = [
    1709498,
    1956623,
    2384521,
    2620324,
    2628753,
    2629220,
    2629380,
    2631712,
    2635748,
    2636023,
    2636361,
    2636495,
    2642188,
    2664760,
    2667515,
    2686585,
    2692353,
    2713168,
    2719291,
    2733570,
    2763858,
    2770334,
    2787525,
    2844403,
    2849910,
    2856292,
    2860080,
    2892884,
    2910314,
    2944621,
    2988730,
    3124571,
    3146232,
    3147569,
    3247600,
    3283440,
    3293228,
    3306495,
    3321845,
    3367445,
    3375276,
    3384768,
    3388871,
    3396237,
    3438071,
    3452508,
    3480339,
    3541590,
    3553233,
    3587225,
    3608858,
    3662190,
    3719337,
    3721971,
    3791266,
    3812776,
    3851583,
    3856336,
    3929474,
    3946629,
    3946655,
    3953483,
    4171100,
    4205324,
    4237329,
    4256459,
    4287234,
    4317499,
    4327293,
    4386146,
    4398584,
    4406175,
    4434540,
    4496715,
    4519217,
    4553427,
    4558691,
    4584798,
    4619940,
    4643628,
    4663255,
    4940538,
    4946890,
    4949002,
    4996393,
    5045138,
    5081124,
    5719947,
    5754021,
    5766793,
    5883458,
    5897509,
    5990069,
    6000601,
    6047234,
    6048096,
    6104617,
    6171233,
    6171462,
    6192696,
    6230183,
    6302368,
]


def unlock_users() -> None:
    users_to_unlock = users_models.User.query.filter(users_models.User.id.in_(user_ids)).all()
    for user in users_to_unlock:
        if user.deposit.type == users_models.DepositType.GRANT_18:
            continue
        if users_models.UserRole.BENEFICIARY in user.roles:
            user.roles.remove(users_models.UserRole.BENEFICIARY)
        db.session.add(user)
        try:
            activate_beneficiary_if_no_missing_step(user)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Could not activate user %s: %s", user.id, exc)


if __name__ == "__main__":
    # https://github.com/pass-culture/pass-culture-main/blob/pc-34888/api/src/pcapi/scripts/unlock_users/main.py
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    unlock_users()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
