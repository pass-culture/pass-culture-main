from typing import Optional

from pcapi.core.offerers.models import UserOfferer


def filter_query_where_user_is_user_offerer_and_is_validated(query, user):
    return query.join(UserOfferer).filter_by(user=user).filter(UserOfferer.validationToken.is_(None))


def find_one_or_none_by_user_id(user_id: int) -> Optional[UserOfferer]:
    return UserOfferer.query.filter_by(userId=user_id).one_or_none()


def find_one_or_none_by_user_id_and_offerer_id(user_id: int, offerer_id: int) -> UserOfferer:
    return UserOfferer.query.filter_by(userId=user_id, offererId=offerer_id).one_or_none()


def find_all_by_offerer_id(offerer_id: int) -> list[UserOfferer]:
    return UserOfferer.query.filter_by(offererId=offerer_id).all()


def find_one_or_none_by_id(user_offerer_id: int) -> Optional[UserOfferer]:
    return UserOfferer.query.filter_by(id=user_offerer_id).one_or_none()
