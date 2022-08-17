from datetime import datetime
from datetime import timedelta

from pcapi.core.users.models import EmailHistoryEventTypeEnum
from pcapi.core.users.models import User
from pcapi.core.users.models import UserEmailHistory


def has_been_validated(entry: UserEmailHistory) -> bool:
    query = UserEmailHistory.query.filter_by(
        userId=entry.userId,
        oldUserEmail=entry.oldUserEmail,
        oldDomainEmail=entry.oldDomainEmail,
        newUserEmail=entry.newUserEmail,
        newDomainEmail=entry.newDomainEmail,
    ).filter(
        UserEmailHistory.eventType.in_(
            [
                EmailHistoryEventTypeEnum.ADMIN_VALIDATION.value,
                EmailHistoryEventTypeEnum.VALIDATION.value,
            ]
        ),
    )

    return query.first() is not None


def get_latest_pending_email_validation(user: User) -> None | UserEmailHistory:
    a_day_ago = datetime.utcnow() - timedelta(days=1)
    latest_entry = (
        UserEmailHistory.query.filter_by(user=user)
        .filter(UserEmailHistory.creationDate >= a_day_ago)
        .order_by(UserEmailHistory.creationDate.desc())
        .first()
    )
    if not latest_entry or latest_entry.eventType != EmailHistoryEventTypeEnum.UPDATE_REQUEST:
        return None
    return latest_entry
