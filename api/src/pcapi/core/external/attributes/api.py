from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from operator import attrgetter
from typing import List

from sqlalchemy.orm import joinedload

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.categories import categories
from pcapi.core.external.attributes import models
from pcapi.core.external.batch import update_user_attributes as update_batch_user
from pcapi.core.external.sendinblue import update_contact_attributes as update_sendinblue_user
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.models import db


# make sure values are in [a-z0-9_] (no uppercase characters, no '-')
TRACKED_PRODUCT_IDS = {3084625: "brut_x"}


def update_external_user(user: users_models.User, skip_batch: bool = False, skip_sendinblue: bool = False) -> None:
    if user.has_pro_role:
        update_external_pro(user.email)
    else:
        user_attributes = get_user_attributes(user)

        update_batch = user.has_enabled_push_notifications()
        if not skip_batch and update_batch:
            update_batch_user(user.id, user_attributes)

        if not skip_sendinblue:
            update_sendinblue_user(user.email, user_attributes)


def update_external_pro(email: str | None) -> None:
    # Call this function instead of update_external_user in actions which are only available for pro
    # ex. updating a venue, in which bookingEmail is not a User parameter
    from pcapi.tasks.sendinblue_tasks import update_pro_attributes_task
    from pcapi.tasks.serialization.sendinblue_tasks import UpdateProAttributesRequest

    if email:
        now = datetime.utcnow()
        update_pro_attributes_task.delay(
            UpdateProAttributesRequest(email=email, time_id=f"{now.hour}:{now.minute // 15}")
        )


def get_user_or_pro_attributes(user: users_models.User) -> models.UserAttributes | models.ProAttributes:
    if user.has_pro_role:
        return get_pro_attributes(user.email)

    return get_user_attributes(user)


def get_pro_attributes(email: str) -> models.ProAttributes:
    # Offerer name attribute is the list of all offerers either managed by the user account (associated in user_offerer)
    # or the parent offerer of the venue which bookingEmail is the requested email address.
    offerers_names = []

    # All venues which are either managed by offerers associated with user account or linked to the current email as
    # booking email. A venue can be part of both sets.
    all_venues: list[offerers_models.Venue] = []

    attributes = {}

    user = users_repository.find_pro_user_by_email(email)
    if user:
        offerers = [
            user_offerer.offerer
            for user_offerer in user.UserOfferers
            if (user_offerer.isValidated and user_offerer.offerer.isActive)
        ]

        if offerers:
            offerers_names += [offerer.name for offerer in offerers]

        # A pro user is considered as:
        # - a creator if he is the lowest id of user_offerer association for any offerer,
        # - an attached user otherwise, for any offerer he is attached to.
        # This assumption may be wrong because association with creator may have been removed, but there is no other way
        # to get that information
        user_is_creator = False
        user_is_attached = False
        # A pro user is flagged EAC when at least one venue of his offerer has an adageId
        is_eac = False
        if user and offerers:
            offerer_ids = [offerer.id for offerer in offerers]
            user_offerers = offerers_models.UserOfferer.query.filter(
                offerers_models.UserOfferer.offererId.in_(offerer_ids)
            ).all()
            all_venues += offerers_repository.find_venues_by_offerers(*offerers)
            for offerer_id in offerer_ids:
                if min((uo.id, uo.userId) for uo in user_offerers if uo.offererId == offerer_id)[1] == user.id:
                    user_is_creator = True
                else:
                    user_is_attached = True
                if not is_eac and offerers_repository.offerer_has_venue_with_adage_id(offerer_id):
                    is_eac = True

        attributes.update(
            {
                "user_id": user.id,
                "first_name": user.firstName,
                "last_name": user.lastName,
                "user_is_attached": user_is_attached,
                "user_is_creator": user_is_creator,
                "is_eac": is_eac,
            }
        )

    venues = offerers_repository.find_active_venues_by_booking_email(email)
    if venues:
        offerers_names += [venue.managingOfferer.name for venue in venues if venue.managingOfferer]
        all_venues += venues
        attributes.update(
            {
                "dms_application_submitted": any(venue.hasPendingBankInformationApplication for venue in venues),
                "dms_application_approved": all(venue.demarchesSimplifieesIsAccepted for venue in venues),
                "isVirtual": any(venue.isVirtual for venue in venues),
                "isPermanent": any(venue.isPermanent for venue in venues),
                "has_offers": offerers_repository.venues_have_offers(*venues),
                "has_bookings": bookings_repository.venues_have_bookings(*venues),
            }
        )

    marketing_email_subscription = (
        # Force email subscription to True when email is used only as bookingEmail
        # Force to False when email has been removed from db, maybe replaced with another one in user and/or venue
        user.get_notification_subscriptions().marketing_email
        if user
        else bool(venues)
    )

    return models.ProAttributes(
        is_pro=True,
        is_user_email=bool(user),
        is_booking_email=bool(venues),
        marketing_email_subscription=marketing_email_subscription,
        offerers_names=set(offerers_names),
        venues_ids={venue.id for venue in all_venues},
        venues_names={venue.publicName or venue.name for venue in all_venues},
        venues_types={venue.venueTypeCode.name for venue in all_venues if venue.venueTypeCode},
        venues_labels={venue.venueLabel.label for venue in all_venues if venue.venueLabelId},  # type: ignore [misc]
        departement_code={venue.departementCode for venue in all_venues if venue.departementCode},
        postal_code={venue.postalCode for venue in all_venues if venue.postalCode},
        **attributes,  # type: ignore [arg-type]
    )


def get_user_attributes(user: users_models.User) -> models.UserAttributes:
    from pcapi.core.fraud import api as fraud_api
    from pcapi.core.users.api import get_domains_credit

    is_pro_user = (
        user.has_pro_role
        or db.session.query(offerers_models.UserOfferer.query.filter_by(userId=user.id).exists()).scalar()
    )
    user_bookings: List[bookings_models.Booking] = get_user_bookings(user) if not is_pro_user else []
    last_favorite = (
        users_models.Favorite.query.filter_by(userId=user.id).order_by(users_models.Favorite.id.desc()).first()
        if not is_pro_user
        else None
    )
    domains_credit = get_domains_credit(user, user_bookings) if not is_pro_user else None
    bookings_attributes = get_bookings_categories_and_subcategories(user_bookings)
    booking_venues_count = len({booking.venueId for booking in user_bookings})

    amount_spent_2022, first_booked_offer_2022, last_booked_offer_2022 = get_booking_attributes_2022(user_bookings)

    # Call only once to limit to one get_wallet_balance query
    has_remaining_credit = user.has_remaining_credit

    # A user becomes a former beneficiary only after the last credit is expired or spent or can no longer be claimed
    is_former_beneficiary = (user.has_beneficiary_role and not has_remaining_credit) or (
        user.has_underage_beneficiary_role and user.eligibility is None
    )
    user_birth_date = datetime.combine(user.birth_date, datetime.min.time()) if user.birth_date else None

    return models.UserAttributes(
        booking_categories=bookings_attributes.booking_categories,
        booking_count=len(user_bookings),
        booking_subcategories=bookings_attributes.booking_subcategories,
        booking_venues_count=booking_venues_count,
        city=user.city,
        date_created=user.dateCreated,
        date_of_birth=user_birth_date,  # type: ignore [arg-type]
        departement_code=user.departementCode,
        deposit_activation_date=user.deposit_activation_date,
        deposit_expiration_date=user.deposit_expiration_date,
        domains_credit=domains_credit,
        eligibility=user.eligibility,
        first_name=user.firstName,
        has_completed_id_check=fraud_api.has_user_performed_identity_check(user),
        user_id=user.id,
        is_active=user.isActive,
        is_beneficiary=user.is_beneficiary,  # type: ignore [arg-type]
        is_current_beneficiary=user.is_beneficiary and has_remaining_credit,
        is_former_beneficiary=is_former_beneficiary,
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
        most_booked_subcategory=bookings_attributes.most_booked_subcategory,
        most_booked_movie_genre=bookings_attributes.most_booked_movie_genre,
        most_booked_music_type=bookings_attributes.most_booked_music_type,
        phone_number=user.phoneNumber,  # type: ignore [arg-type]
        postal_code=user.postalCode,
        products_use_date={
            f"product_{TRACKED_PRODUCT_IDS[booking.stock.offer.productId]}_use": booking.dateUsed
            for booking in user_bookings
            if booking.dateUsed and booking.stock.offer.productId in TRACKED_PRODUCT_IDS
        },
        roles=[role.value for role in user.roles],
        suspension_date=user.suspension_date,
        suspension_reason=user.suspension_reason,
        amount_spent_2022=amount_spent_2022,
        first_booked_offer_2022=first_booked_offer_2022,
        last_booked_offer_2022=last_booked_offer_2022,
    )


def _get_most_booked(grouped_bookings: defaultdict[str, list[bookings_models.Booking]]) -> str | None:
    """
    Most booked group (category, subcategory, genre, musicType) is:
    - the group in which the user has the highest number of bookings,
    - in case of several most booked groups with the same length, the one with the highest credit spent by the user
    """
    if not grouped_bookings:
        return None

    return sorted(
        grouped_bookings.items(),
        key=lambda kv: (len(kv[1]), sum(booking.amount * booking.quantity for booking in kv[1])),
        reverse=True,
    )[0][0]


def get_bookings_categories_and_subcategories(
    user_bookings: list[bookings_models.Booking],
) -> models.BookingsAttributes:
    """
    Returns a tuple of three values:
    - the list of all distinct categories in user bookings (not canceled)
    - the list of all distinct subcategories in user bookings (not canceled)
    - the single most booked subcategory in user bookings
    - the single most booked movie genre when most booked category is 'CINEMA'
    - the single most booked musicType when most booked category is about music
    """
    bookings_by_categories = defaultdict(list)
    bookings_by_subcategories = defaultdict(list)
    for booking in user_bookings:
        if booking.status != bookings_models.BookingStatus.CANCELLED:
            bookings_by_categories[booking.stock.offer.subcategory.category.id].append(booking)
            bookings_by_subcategories[booking.stock.offer.subcategoryId].append(booking)

    most_booked_category = _get_most_booked(bookings_by_categories)
    most_booked_subcategory = _get_most_booked(bookings_by_subcategories)

    most_booked_movie_genre = None
    if most_booked_category == categories.CINEMA.id:
        cinema_bookings_by_genre = defaultdict(list)
        for booking in bookings_by_categories[categories.CINEMA.id]:
            if extra_data := booking.stock.offer.extraData:
                for genre in extra_data.get("genres") or []:
                    cinema_bookings_by_genre[genre].append(booking)
        most_booked_movie_genre = _get_most_booked(cinema_bookings_by_genre)

    most_booked_music_type = None
    music_categories = (categories.MUSIQUE_ENREGISTREE.id, categories.MUSIQUE_LIVE.id)
    if most_booked_category in music_categories:
        music_bookings_by_type = defaultdict(list)
        for category in music_categories:
            for booking in bookings_by_categories[category]:
                if extra_data := booking.stock.offer.extraData:
                    if music_type := extra_data.get("musicType"):
                        music_bookings_by_type[music_type].append(booking)
        most_booked_music_type = _get_most_booked(music_bookings_by_type)

    return models.BookingsAttributes(
        # sorted alphabetically to be deterministic and avoid useless changes in external data
        booking_categories=sorted(bookings_by_categories.keys()),
        booking_subcategories=sorted(bookings_by_subcategories.keys()),
        most_booked_subcategory=most_booked_subcategory,
        most_booked_movie_genre=most_booked_movie_genre,
        most_booked_music_type=most_booked_music_type,
    )


# Specific for "Retro" campaign in December 2022 - may become deprecated in 2023
def get_booking_attributes_2022(
    user_bookings: list[bookings_models.Booking],
) -> tuple[Decimal, str | None, str | None]:
    bookings_2022 = sorted(
        filter(
            lambda booking: booking.dateCreated.year == 2022 and not booking.is_cancelled,
            user_bookings,
        ),
        key=attrgetter("dateCreated"),
    )

    if not bookings_2022:
        return Decimal("0.00"), None, None

    amount_spent: Decimal = sum(booking.amount for booking in bookings_2022)  # type: ignore [assignment]
    first_booked_offer: str = bookings_2022[0].stock.offer.name
    last_booked_offer: str = bookings_2022[-1].stock.offer.name

    return amount_spent, first_booked_offer, last_booked_offer


def get_user_bookings(user: users_models.User) -> List[bookings_models.Booking]:
    return (
        bookings_models.Booking.query.join(
            bookings_models.IndividualBooking,
            bookings_models.Booking.individualBookingId == bookings_models.IndividualBooking.id,
        )
        .options(joinedload(bookings_models.Booking.individualBooking))
        .options(joinedload(bookings_models.Booking.venue).load_only(offerers_models.Venue.isVirtual))
        .options(
            joinedload(bookings_models.Booking.stock)
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.url,
                offers_models.Offer.productId,
                offers_models.Offer.subcategoryId,
                offers_models.Offer.name,
                offers_models.Offer.extraData,
            )
        )
        .filter(
            bookings_models.IndividualBooking.userId == user.id,
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
        )
        .order_by(db.desc(bookings_models.Booking.dateCreated))
        .all()
    )
