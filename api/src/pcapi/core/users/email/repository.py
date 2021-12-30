from pcapi.core.users.models import EmailHistoryEventTypeEnum
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
