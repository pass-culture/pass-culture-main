from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.external.models import UserAttributes
from pcapi.core.users.models import User
from pcapi.models.db import db
from pcapi.models.user_offerer import UserOfferer

from .batch import update_user_attributes as update_batch_user
from .sendinblue import update_contact_attributes as update_sendinblue_user


# make sure values are in [a-z0-9_] (no uppercase characters, no '-')
TRACKED_PRODUCT_IDS = {3084625: "brut_x"}


def update_external_user(user: User):
    user_attributes = get_user_attributes(user)

    update_batch_user(user.id, user_attributes)
    update_sendinblue_user(user.email, user_attributes)


def get_user_attributes(user: User) -> dict:
    from pcapi.core.users.api import get_domains_credit

    user_bookings = _get_user_bookings(user)

    return UserAttributes(
        booking_categories=list(set(booking.stock.offer.type for booking in user_bookings)),
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth,
        departement_code=user.departementCode,
        deposit_expiration_date=user.deposit_expiration_date,
        domains_credit=get_domains_credit(user, [booking for booking in user_bookings if not booking.isCancelled]),
        first_name=user.firstName,
        is_beneficiary=user.isBeneficiary,
        is_pro=user.has_pro_role or db.session.query(UserOfferer.query.filter_by(userId=user.id).exists()).scalar(),
        last_booking_date=user_bookings[0].dateCreated if user_bookings else None,
        last_name=user.lastName,
        marketing_push_subscription=user.get_notification_subscriptions().marketing_push,
        postal_code=user.postalCode,
        products_use_date={
            f"product_{TRACKED_PRODUCT_IDS[booking.stock.offer.productId]}_use": booking.dateUsed
            for booking in user_bookings
            if booking.dateUsed and booking.stock.offer.productId in TRACKED_PRODUCT_IDS
        },
    )


def _get_user_bookings(user: User) -> list[Booking]:
    return (
        Booking.query.options(
            joinedload(Booking.stock).joinedload(Stock.offer).load_only(Offer.type, Offer.url, Offer.productId)
        )
        .filter_by(userId=user.id)
        .order_by(db.desc(Booking.dateCreated))
        .all()
    )
