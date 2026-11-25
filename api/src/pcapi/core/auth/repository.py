from sqlalchemy import select

from pcapi.core.users.models import SingleSignOn
from pcapi.models import db


def get_sso_user_by_provider_and_id(provider: str, sso_id: str) -> SingleSignOn | None:
    query = select(SingleSignOn).where(
        SingleSignOn.ssoProvider == provider,
        SingleSignOn.ssoUserId == sso_id,
    )

    return db.session.execute(query).scalar_one_or_none()
