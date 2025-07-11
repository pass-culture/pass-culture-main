from datetime import datetime

import sqlalchemy.orm as sa_orm

from pcapi.core.users import constants
from pcapi.core.users.models import EmailHistoryEventTypeEnum
from pcapi.core.users.models import User
from pcapi.core.users.models import UserEmailHistory
from pcapi.models import db


def _query_ordered_email_update_entry(user: User) -> sa_orm.Query:
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
