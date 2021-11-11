from typing import List
from typing import Tuple

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.external.models import UserAttributes
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import User
from pcapi.models.db import db
from pcapi.models.user_offerer import UserOfferer

from .batch import update_user_attributes as update_batch_user
from .sendinblue import update_contact_attributes as update_sendinblue_user


# make sure values are in [a-z0-9_] (no uppercase characters, no '-')
TRACKED_PRODUCT_IDS = {3084625: "brut_x"}


def update_external_user(user: User, skip_batch: bool = False, skip_sendinblue: bool = False) -> None:
    user_attributes = get_user_attributes(user)

    update_batch = user.has_enabled_push_notifications()
    if not skip_batch and update_batch:
        update_batch_user(user.id, user_attributes)

    if not skip_sendinblue:
        update_sendinblue_user(user.email, user_attributes)


def get_user_attributes(user: User) -> UserAttributes:
    from pcapi.core.users.api import get_domains_credit

    is_pro_user = user.has_pro_role or db.session.query(UserOfferer.query.filter_by(userId=user.id).exists()).scalar()
    user_bookings: List[Booking] = _get_user_bookings(user) if not is_pro_user else []
    last_favorite = (
        Favorite.query.filter_by(userId=user.id).order_by(Favorite.id.desc()).first() if not is_pro_user else None
    )
    domains_credit = get_domains_credit(user, user_bookings) if not is_pro_user else None
    booking_categories, booking_subcategories = _get_bookings_categories_and_subcategories(user_bookings)

    return UserAttributes(
        booking_categories=booking_categories,
        booking_count=len(user_bookings),
        booking_subcategories=booking_subcategories,
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth,
        departement_code=user.departementCode,
        deposit_activation_date=user.deposit_activation_date,
        deposit_expiration_date=user.deposit_expiration_date,
        domains_credit=domains_credit,
        eligibility=user.eligibility,
        first_name=user.firstName,
        has_completed_id_check=user.hasCompletedIdCheck,
        user_id=user.id,
        is_beneficiary=user.has_beneficiary_role,
        is_eligible=user.is_eligible,
        is_email_validated=user.isEmailValidated,
        is_pro=is_pro_user,
        last_booking_date=user_bookings[0].dateCreated if user_bookings else None,
        last_favorite_creation_date=last_favorite.dateCreated if last_favorite else None,
        last_name=user.lastName,
        last_visit_date=user.lastConnectionDate,
        marketing_email_subscription=user.get_notification_subscriptions().marketing_email,
        marketing_push_subscription=user.get_notification_subscriptions().marketing_push,
        postal_code=user.postalCode,
        products_use_date={
            f"product_{TRACKED_PRODUCT_IDS[booking.stock.offer.productId]}_use": booking.dateUsed
            for booking in user_bookings
            if booking.dateUsed and booking.stock.offer.productId in TRACKED_PRODUCT_IDS
        },
        roles=user.roles,
    )


def _get_bookings_categories_and_subcategories(user_bookings: list[Booking]) -> Tuple[list[str], list[str]]:
    booking_subcategories_ids = list(set(booking.stock.offer.subcategoryId for booking in user_bookings))
    booking_categories_ids = list(set(booking.stock.offer.subcategory.category_id for booking in user_bookings))
    return booking_categories_ids, booking_subcategories_ids


def _get_user_bookings(user: User) -> List[Booking]:
    return (
        Booking.query.join(IndividualBooking, Booking.individualBookingId == IndividualBooking.id)
        .options(joinedload(Booking.individualBooking))
        .options(joinedload(Booking.venue).load_only(Venue.isVirtual))
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .load_only(Offer.url, Offer.productId, Offer.subcategoryId)
            .joinedload(Offer.venue)
        )
        .filter(IndividualBooking.userId == user.id, Booking.status != BookingStatus.CANCELLED)
        .order_by(db.desc(Booking.dateCreated))
        .all()
    )
