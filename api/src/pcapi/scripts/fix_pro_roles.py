"""
Fix wrong pro roles in User table.

In some cases, user may have been set back to NON_ATTACHED_PRO when an offerer was moved to pending state, even if the
user was already PRO because of existing validated attachment to another validated offerer.
"""
import argparse

import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db


def fix_users_who_should_be_pro(do_update: bool = False) -> None:
    """
    Users who don't have PRO role but have at least one validated attachment to a validated offerer
    """
    users = (
        users_models.User.query.join(offerers_models.UserOfferer)
        .join(offerers_models.Offerer)
        .filter(
            users_models.User.has_pro_role.is_(False),  # type: ignore [attr-defined]
            offerers_models.UserOfferer.isValidated,
            offerers_models.Offerer.isValidated,
        )
        .options(sa.orm.load_only(users_models.User.id, users_models.User.email, users_models.User.roles))
    )

    for user in users:
        print(f"Fix {user.id} {user.email} {user.roles} => PRO")
        if do_update:
            user.add_pro_role()
            db.session.commit()


def fix_users_who_should_not_be_pro(do_update: bool = False) -> None:
    """
    Users who have PRO roles but do not have any attachment (any status)
    """
    users = users_models.User.query.outerjoin(offerers_models.UserOfferer).filter(
        users_models.User.has_pro_role.is_(True),  # type: ignore [attr-defined]
        offerers_models.UserOfferer.id.is_(None),
    )

    for user in users:
        print(f"Fix {user.id} {user.email} {user.roles} => NON_ATTACHED_PRO (not PRO)")
        if do_update:
            user.add_non_attached_pro_role()
            db.session.commit()


def fix_users_who_should_be_non_attached_pro(do_update: bool = False) -> None:
    """
    Users who don't have any PRO or NON_ATTACHED_PRO role but have an attachment to an offerer, waiting for validation.
    """
    users = (
        users_models.User.query.join(offerers_models.UserOfferer)
        .join(offerers_models.Offerer)
        .filter(
            users_models.User.has_non_attached_pro_role.is_(False),  # type: ignore [attr-defined]
            sa.or_(
                sa.not_(offerers_models.UserOfferer.isValidated),
                sa.not_(offerers_models.Offerer.isValidated),
            ),
        )
        .options(
            sa.orm.load_only(users_models.User.roles),
            sa.orm.joinedload(users_models.User.UserOfferers)
            .load_only(offerers_models.UserOfferer.validationStatus)
            .joinedload(offerers_models.UserOfferer.offerer)
            .load_only(offerers_models.Offerer.validationStatus),
        )
    )

    for user in users:
        if not any(user_offerer.isValidated and user_offerer.offerer.isValidated for user_offerer in user.UserOfferers):
            print(f"Fix {user.id} {user.email} {user.roles} => NON_ATTACHED_PRO")
            if do_update:
                user.add_non_attached_pro_role()
                db.session.commit()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Fix pro roles in User table")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    fix_users_who_should_be_non_attached_pro(do_update=args.not_dry)
    fix_users_who_should_not_be_pro(do_update=args.not_dry)
    fix_users_who_should_be_pro(do_update=args.not_dry)
