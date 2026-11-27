from sqlalchemy import orm as sa_orm
from sqlalchemy import select

from pcapi.core.users.models import SingleSignOn
from pcapi.core.users.models import User
from pcapi.models import db


def get_single_sign_on_from_provider(sso_provider: str, sso_user_id: str) -> SingleSignOn | None:
    return (
        db.session.query(SingleSignOn)
        .filter(
            SingleSignOn.ssoProvider == sso_provider,
            SingleSignOn.ssoUserId == sso_user_id,
        )
        .options(sa_orm.joinedload(SingleSignOn.user))
        .one_or_none()
    )


def get_single_sign_on_from_id(sso_id: int) -> SingleSignOn | None:
    stmt = select(SingleSignOn).where(SingleSignOn.id == sso_id)

    return db.session.execute(stmt).scalar_one_or_none()


def create_single_sign_on(
    user: User,
    sso_provider: str,
    sso_user_id: str,
    sso_extra_data: dict | None = None,
) -> SingleSignOn:
    sso_user = SingleSignOn(
        user=user,
        ssoProvider=sso_provider,
        ssoUserId=sso_user_id,
        ssoExtraData=sso_extra_data,
    )

    db.session.add(sso_user)
    db.session.flush()

    return sso_user


def delete_sso_user(sso_id: int) -> None:
    db.session.query(SingleSignOn).filter_by(id=sso_id).delete(synchronize_session=False)
