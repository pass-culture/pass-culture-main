from datetime import datetime

from pcapi.core.users import constants
from pcapi.core.users.models import EmailHistoryEventTypeEnum
from pcapi.core.users.models import User
from pcapi.core.users.models import UserEmailHistory
from pcapi.models import db
from pcapi.models.pc_object import BaseQuery


def _query_ordered_email_update_entry(user: User) -> BaseQuery:
    latest_entries = (
        db.session.query(UserEmailHistory).filter_by(user=user).order_by(UserEmailHistory.creationDate.desc())
    )
    return latest_entries


def get_latest_pending_email_validation(user: User) -> None | UserEmailHistory:
    creation_date_limit = datetime.utcnow() - constants.EMAIL_CHANGE_TOKEN_LIFE_TIME
    latest_entry = (
        _query_ordered_email_update_entry(user).filter(UserEmailHistory.creationDate >= creation_date_limit).first()
    )
    if not latest_entry or latest_entry.eventType != EmailHistoryEventTypeEnum.UPDATE_REQUEST:
        return None
    return latest_entry


def get_email_update_latest_event(user: User) -> UserEmailHistory | None:
    return _query_ordered_email_update_entry(user).first()
