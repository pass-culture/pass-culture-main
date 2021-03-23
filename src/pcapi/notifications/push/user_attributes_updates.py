from pcapi.core.users.models import User


BATCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_user_attributes(user: User) -> dict:
    from pcapi.core.users.api import get_domains_credit

    credit = get_domains_credit(user)
    return {
        "u.credit": int(credit.all.remaining * 100) if credit else 0,
        "date(u.date_of_birth)": user.dateOfBirth.strftime(BATCH_DATETIME_FORMAT) if user.dateOfBirth else None,
        "u.postal_code": user.postalCode,
        "date(u.date_created)": user.dateCreated.strftime(BATCH_DATETIME_FORMAT),
        "u.marketing_push_subscription": user.get_notification_subscriptions().marketing_push,
        "u.is_beneficiary": user.isBeneficiary,
        "date(u.deposit_expiration_date)": user.deposit_expiration_date.strftime(BATCH_DATETIME_FORMAT)
        if user.deposit_expiration_date
        else None,
    }
