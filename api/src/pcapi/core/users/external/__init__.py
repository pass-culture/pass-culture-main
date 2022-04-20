from datetime import datetime
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.bookings.repository import venues_have_bookings
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.repository import find_active_venues_by_booking_email
from pcapi.core.offerers.repository import find_venues_by_offerers
from pcapi.core.offerers.repository import venues_have_offers
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.external.models import ProAttributes
from pcapi.core.users.external.models import UserAttributes
from pcapi.core.users.models import Favorite
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_pro_user_by_email
from pcapi.models import db

from .batch import update_user_attributes as update_batch_user
from .sendinblue import update_contact_attributes as update_sendinblue_user


# make sure values are in [a-z0-9_] (no uppercase characters, no '-')
TRACKED_PRODUCT_IDS = {3084625: "brut_x"}


def update_external_user(user: User, skip_batch: bool = False, skip_sendinblue: bool = False) -> None:
    if user.has_pro_role:
        update_external_pro(user.email)
    else:
        user_attributes = get_user_attributes(user)

        update_batch = user.has_enabled_push_notifications()
        if not skip_batch and update_batch:
            update_batch_user(user.id, user_attributes)

        if not skip_sendinblue:
            update_sendinblue_user(user.email, user_attributes)


def update_external_pro(email: Optional[str]) -> None:
    # Call this function instead of update_external_user in actions which are only available for pro
    # ex. updating a venue, in which bookingEmail is not a User parameter
    from pcapi.tasks.sendinblue_tasks import update_pro_attributes_task
    from pcapi.tasks.serialization.sendinblue_tasks import UpdateProAttributesRequest

    if email:
        now = datetime.utcnow()
        update_pro_attributes_task.delay(
            UpdateProAttributesRequest(email=email, time_id=f"{now.hour}:{now.minute // 15}")
        )


def get_user_or_pro_attributes(user: User) -> Union[UserAttributes, ProAttributes]:
    if user.has_pro_role:
        return get_pro_attributes(user.email)

    return get_user_attributes(user)


def get_pro_attributes(email: str) -> ProAttributes:
    # Offerer name attribute is the list of all offerers either managed by the user account (associated in user_offerer)
    # or the parent offerer of the venue which bookingEmail is the requested email address.
    offerers_names = []

    # All venues which are either managed by offerers associated with user account or linked to the current email as
    # booking email. A venue can be part of both sets.
    all_venues: list[Venue] = []

    attributes = {}

    user = find_pro_user_by_email(email)
    if user:
        offerers = [offerer for offerer in user.offerers if offerer.isActive]

        if offerers:
            offerers_names += [offerer.name for offerer in offerers]

        # A pro user is considered as:
        # - a creator if he is the lowest id of user_offerer association for any offerer,
        # - an attached user otherwise, for any offerer he is attached to.
        # This assumption may be wrong because association with creator may have been removed, but there is no other way
        # to get that information
        user_is_creator = False
        user_is_attached = False
        if user and offerers:
            offerer_ids = [offerer.id for offerer in offerers]
            user_offerers = UserOfferer.query.filter(Offerer.id.in_(offerer_ids)).all()
            all_venues += find_venues_by_offerers(*offerers)
            for offerer_id in offerer_ids:
                if min([(uo.id, uo.userId) for uo in user_offerers if uo.offererId == offerer_id])[1] == user.id:
                    user_is_creator = True
                else:
                    user_is_attached = True

        attributes.update(
            {
                "user_id": user.id,
                "first_name": user.firstName,
                "last_name": user.lastName,
                "user_is_attached": user_is_attached,
                "user_is_creator": user_is_creator,
            }
        )

    venues = find_active_venues_by_booking_email(email)
    if venues:
        offerers_names += [venue.managingOfferer.name for venue in venues if venue.managingOfferer]
        all_venues += venues
        attributes.update(
            {
                "dms_application_submitted": any(venue.demarchesSimplifieesIsDraft for venue in venues),
                "dms_application_approved": all(venue.demarchesSimplifieesIsAccepted for venue in venues),
                "isVirtual": any(venue.isVirtual for venue in venues),
                "isPermanent": any(venue.isPermanent for venue in venues),
                "has_offers": venues_have_offers(*venues),
                "has_bookings": venues_have_bookings(*venues),
            }
        )

    marketing_email_subscription = (
        # Force email subscription to True when email is used only as bookingEmail
        # Force to False when email has been removed from db, maybe replaced with another one in user and/or venue
        user.get_notification_subscriptions().marketing_email
        if user
        else bool(venues)
    )

    return ProAttributes(
        is_pro=True,
        is_user_email=bool(user),
        is_booking_email=bool(venues),
        marketing_email_subscription=marketing_email_subscription,
        offerers_names=set(offerers_names),
        venues_ids={venue.id for venue in all_venues},
        venues_names={venue.publicName or venue.name for venue in all_venues},
        venues_types={venue.venueTypeCode.name for venue in all_venues if venue.venueTypeCode},  # type: ignore [attr-defined]
        venues_labels={venue.venueLabel.label for venue in all_venues if venue.venueLabelId},
        departement_code={venue.departementCode for venue in all_venues if venue.departementCode},
        postal_code={venue.postalCode for venue in all_venues if venue.postalCode},  # type: ignore [has-type]
        **attributes,  # type: ignore [arg-type]
    )


def get_user_attributes(user: User) -> UserAttributes:
    from pcapi.core.fraud import api as fraud_api
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
        city=user.city,
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth,  # type: ignore [arg-type]
        departement_code=user.departementCode,
        deposit_activation_date=user.deposit_activation_date,
        deposit_expiration_date=user.deposit_expiration_date,
        domains_credit=domains_credit,
        eligibility=user.eligibility,
        first_name=user.firstName,
        has_completed_id_check=fraud_api.has_user_performed_identity_check(user),
        user_id=user.id,
        is_active=user.isActive,  # type: ignore [arg-type]
        is_beneficiary=user.is_beneficiary,  # type: ignore [arg-type]
        is_eligible=user.is_eligible,
        is_email_validated=user.isEmailValidated,  # type: ignore [arg-type]
        is_phone_validated=user.is_phone_validated,  # type: ignore [arg-type]
        is_pro=is_pro_user,  # type: ignore [arg-type]
        last_booking_date=user_bookings[0].dateCreated if user_bookings else None,
        last_favorite_creation_date=last_favorite.dateCreated if last_favorite else None,  # type: ignore [attr-defined]
        last_name=user.lastName,
        last_visit_date=user.lastConnectionDate,
        marketing_email_subscription=user.get_notification_subscriptions().marketing_email,
        marketing_push_subscription=user.get_notification_subscriptions().marketing_push,
        phone_number=user.phoneNumber,
        postal_code=user.postalCode,
        products_use_date={
            f"product_{TRACKED_PRODUCT_IDS[booking.stock.offer.productId]}_use": booking.dateUsed
            for booking in user_bookings
            if booking.dateUsed and booking.stock.offer.productId in TRACKED_PRODUCT_IDS
        },
        roles=[role.value for role in user.roles],
        suspension_date=user.suspension_date,
        suspension_reason=user.suspension_reason,
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
