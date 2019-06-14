from pprint import pprint
from uuid import UUID

from models import UserSession, PcObject


def register_user_session(user_id: int, session_uuid: UUID):
    session = UserSession()
    session.userId = user_id
    session.uuid = session_uuid
    PcObject.save(session)


def delete_user_session(user_id: int, session_uuid: UUID):
    session = UserSession.query \
        .filter_by(userId=user_id, uuid=session_uuid) \
        .first()

    if session:
        PcObject.delete(session)


def existing_user_session(user_id: int, session_uuid: UUID) -> bool:
    session = UserSession.query \
        .filter_by(userId=user_id, uuid=session_uuid) \
        .first()
    return session is not None
