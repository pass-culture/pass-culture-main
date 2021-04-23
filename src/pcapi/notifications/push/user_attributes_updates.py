from dataclasses import dataclass

from pcapi.core.users.models import User


@dataclass
class UserUpdateData:
    user_id: str
    attributes: dict


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


def get_user_booking_attributes(user: User) -> dict:
    from pcapi.core.users.api import get_domains_credit
    from pcapi.core.users.api import get_last_booking_date

    credit = get_domains_credit(user)
    last_booking_date = get_last_booking_date(user)

    return {
        "date(u.lastBookingDate)": last_booking_date.strftime(BATCH_DATETIME_FORMAT) if last_booking_date else None,
        "u.credit": int(credit.all.remaining * 100) if credit else 0,
    }
