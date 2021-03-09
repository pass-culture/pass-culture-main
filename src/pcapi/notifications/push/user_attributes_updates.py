from pcapi.core.users.models import User


BATCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_user_attributes(user: User) -> dict:
    return {
        "u.credit": int(user.wallet_balance * 100),
        "date(u.date_of_birth)": user.dateOfBirth.strftime(BATCH_DATETIME_FORMAT) if user.dateOfBirth else None,
        "u.postal_code": user.postalCode,
        "date(u.date_created)": user.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "u.marketing_push_subscription": user.get_notification_subscriptions().marketing_push,
    }
