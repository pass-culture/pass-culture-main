from uuid import UUID

from pcapi.models.user_session import UserSession
from pcapi.repository import repository


def register_user_session(user_id: int, session_uuid: UUID):  # type: ignore [no-untyped-def]
    session = UserSession()
    session.userId = user_id
    session.uuid = session_uuid  # type: ignore [call-overload]
    repository.save(session)


def delete_user_session(user_id: int, session_uuid: UUID):  # type: ignore [no-untyped-def]
    session = UserSession.query.filter_by(userId=user_id, uuid=session_uuid).one_or_none()

    if session:
        repository.delete(session)


def existing_user_session(user_id: int, session_uuid: UUID) -> bool:
    session = UserSession.query.filter_by(userId=user_id, uuid=session_uuid).one_or_none()
    return session is not None
