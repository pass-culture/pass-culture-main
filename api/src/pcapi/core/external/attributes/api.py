from collections import Counter
from collections import defaultdict
from datetime import datetime
from functools import partial

import sqlalchemy as sa
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.categories import pro_categories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.repository import has_collective_offers_for_program_and_venue_ids
from pcapi.core.external.attributes import models
from pcapi.core.external.batch import update_user_attributes as update_batch_user
from pcapi.core.external.sendinblue import update_contact_attributes as update_sendinblue_user
from pcapi.core.finance import deposit_api
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository.session_management import on_commit


# make sure values are in [a-z0-9_] (no uppercase characters, no '-')
TRACKED_PRODUCT_IDS = {3084625: "brut_x"}


def update_external_user(
    user: users_models.User,
    cultural_survey_answers: dict[str, list[str]] | None = None,
    skip_batch: bool = False,
    skip_sendinblue: bool = False,
    batch_extra_data: dict[str, datetime] | None = None,
) -> None:
    if not user.isActive:
        # suspended users have been removed from Brevo
        return

    if user.has_any_pro_role:
        update_external_pro(user.email)
    else:
        user_attributes = get_user_attributes(user)

        if not skip_batch:
            on_commit(
                partial(
                    update_batch_user,
                    user.id,
                    user_attributes,
                    cultural_survey_answers=cultural_survey_answers,
                    batch_extra_data=batch_extra_data,
                ),
            )
        if not skip_sendinblue:
            on_commit(
                partial(
                    update_sendinblue_user,
                    user.email,
                    user_attributes,
                    cultural_survey_answers=cultural_survey_answers,
                ),
            )


def update_external_pro(email: str | None) -> None:
    # Call this function instead of update_external_user in actions which are only available for pro
    # ex. updating a venue, in which bookingEmail is not a User parameter
    from pcapi.tasks.beamer_tasks import update_beamer_pro_attributes_task
    from pcapi.tasks.sendinblue_tasks import update_sib_pro_attributes_task
    from pcapi.tasks.serialization.external_pro_tasks import UpdateProAttributesRequest

    if email:
        now = datetime.utcnow()
        on_commit(
            partial(
                update_sib_pro_attributes_task.delay,
                payload=UpdateProAttributesRequest(email=email, time_id=f"{now.hour // 12}"),
            ),
        )
        if FeatureToggle.ENABLE_BEAMER.is_active():
            on_commit(
                partial(
                    update_beamer_pro_attributes_task.delay,
                    payload=UpdateProAttributesRequest(email=email, time_id=f"{now.hour // 12}"),
                ),
            )


def get_anonymized_attributes(user: users_models.User) -> models.UserAttributes | models.ProAttributes:
    if user.has_pro_role:
        attributes = get_pro_attributes(user.email)
        attributes.is_user_email = False
        attributes.user_id = 0
        attributes.first_name = ""
        attributes.last_name = ""
        attributes.user_is_creator = False
        return attributes

    return models.UserAttributes(
        booking_categories=[],
        booking_count=0,
        booking_subcategories=[],
        booking_venues_count=0,
        city="",
        date_created=user.dateCreated,
        date_of_birth=user.dateOfBirth.replace(day=1, month=1) if user.dateOfBirth else None,
        departement_code="",
        deposits_count=0,
        first_name="",
        has_completed_id_check=False,
        user_id=user.id,
        is_active=False,
        is_beneficiary=True,
        is_current_beneficiary=False,
        is_former_beneficiary=False,
        is_eligible=False,
        is_phone_validated=False,
        is_pro=False,
        last_name="",
        marketing_email_subscription=False,
        marketing_push_subscription=False,
        phone_number="",
        postal_code="",
        products_use_date={},
        roles=[],
        deposit_activation_date=None,
        deposit_expiration_date=None,
        domains_credit=None,
        eligibility=None,
        is_email_validated=None,
        last_booking_date=None,
        last_favorite_creation_date=None,
        last_recredit_type=None,
        last_visit_date=None,
        most_booked_subcategory=None,
        most_booked_movie_genre=None,
        most_booked_music_type=None,
        most_favorite_offer_subcategories=None,
        subscribed_themes=[],
        suspension_date=None,
        suspension_reason=None,
        achievements=[],
    )


def get_pro_attributes(email: str) -> models.ProAttributes:
    # Offerer name attribute is the list of all offerers either managed by the user account (associated in user_offerer)
    # or the parent offerer of the venue which bookingEmail is the requested email address.
    offerers_names: set[str] = set()
    offerers_tags: set[str] = set()

    # All venues which are either managed by offerers associated with user account or linked to the current email as
    # booking email. A venue can be part of both sets.
    all_venues: list[offerers_models.Venue] = []

    attributes = {}

    user = (
        # Also fetch NON_ATTACHED_PRO so that if user is found, user id first name and last name are filled
        users_repository.find_pro_or_non_attached_pro_user_by_email_query(email)
        .filter(users_models.User.isActive.is_(True))
        .options(
            load_only(
                users_models.User.firstName, users_models.User.lastName, users_models.User.notificationSubscriptions
            ),
            joinedload(users_models.User.UserOfferers)
            .load_only(offerers_models.UserOfferer.offererId, offerers_models.UserOfferer.validationStatus)
            .joinedload(offerers_models.UserOfferer.offerer)
            .options(
                # Fetch information about offerers to which user is attached
                load_only(
                    offerers_models.Offerer.name,
                    offerers_models.Offerer.isActive,
                    offerers_models.Offerer.validationStatus,
                ),
                joinedload(offerers_models.Offerer.tags).load_only(offerers_models.OffererTag.name),
                # Fetch all attachments to these offerers, to check if current user is the "creator" (first user)
                joinedload(offerers_models.Offerer.UserOfferers).load_only(offerers_models.UserOfferer.userId),
                # Fetch useful information on all venues managed by these offerers
                joinedload(offerers_models.Offerer.managedVenues)
                .load_only(
                    offerers_models.Venue.publicName,
                    offerers_models.Venue.name,
                    offerers_models.Venue.venueTypeCode,
                    offerers_models.Venue.venueLabelId,
                    offerers_models.Venue.adageId,
                )
                .options(
                    joinedload(offerers_models.Venue.venueLabel).load_only(offerers_models.VenueLabel.label),
                    joinedload(offerers_models.Venue.offererAddress)
                    .load_only(offerers_models.OffererAddress.id)
                    .joinedload(offerers_models.OffererAddress.address)
                    .load_only(geography_models.Address.departmentCode, geography_models.Address.postalCode),
                ),
            ),
        )
        .one_or_none()
    )

    if user:
        offerers = [
            user_offerer.offerer
            for user_offerer in user.UserOfferers
            if (user_offerer.isValidated and user_offerer.offerer.isActive and user_offerer.offerer.isValidated)
        ]

        # A pro user is considered as:
        # - a creator if he is the lowest id of user_offerer association for any offerer,
        # - an attached user otherwise, for any offerer he is attached to.
        # This assumption may be wrong because association with creator may have been removed, but there is no other way
        # to get that information
        user_is_creator = False
        user_is_attached = False
        # A pro user is flagged EAC when at least one venue of his offerer has an adageId
        is_eac = False

        if offerers:
            for offerer in offerers:
                all_venues += offerer.managedVenues
                offerers_names.add(offerer.name)
                offerers_tags.update(tag.name for tag in offerer.tags)

                if min((uo.id, uo.userId) for uo in offerer.UserOfferers)[1] == user.id:
                    user_is_creator = True
                else:
                    user_is_attached = True

                # Avoid offerers_repository.offerer_has_venue_with_adage_id which makes one extra request for each offerer
                if not is_eac and any(bool(venue.adageId) for venue in offerer.managedVenues):
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

    venues = (
        db.session.query(offerers_models.Venue)
        .filter_by(bookingEmail=email)
        .join(
            offerers_models.Offerer,
            sa.and_(  # type: ignore[type-var]
                offerers_models.Offerer.id == offerers_models.Venue.managingOffererId,
                offerers_models.Offerer.isActive,
                offerers_models.Offerer.isValidated,
            ),
        )
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .options(
            load_only(
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
                offerers_models.Venue.venueTypeCode,
                offerers_models.Venue.venueLabelId,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.isPermanent,
                offerers_models.Venue.isOpenToPublic,
                offerers_models.Venue._bannerUrl,
                offerers_models.Venue.adageId,
            ),
            contains_eager(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.name)
            .joinedload(offerers_models.Offerer.tags)
            .load_only(offerers_models.OffererTag.name),
            contains_eager(offerers_models.Venue.bankAccountLinks)
            .joinedload(offerers_models.VenueBankAccountLink.bankAccount)
            .load_only(finance_models.BankAccount.status),
            joinedload(offerers_models.Venue.venueLabel).load_only(offerers_models.VenueLabel.label),
            joinedload(offerers_models.Venue.offererAddress)
            .load_only(offerers_models.OffererAddress.id)
            .joinedload(offerers_models.OffererAddress.address)
            .load_only(geography_models.Address.departmentCode, geography_models.Address.postalCode),
        )
        .all()
    )

    venue_ids = {venue.id for venue in venues}
    is_eac_meg = (
        has_collective_offers_for_program_and_venue_ids(educational_models.PROGRAM_MARSEILLE_EN_GRAND, venue_ids)
        if venue_ids
        else False
    )

    if venues:
        all_venues += venues
        for venue in venues:
            offerers_names.add(venue.managingOfferer.name)
            offerers_tags.update(tag.name for tag in venue.managingOfferer.tags)

        has_collective_offers = offerers_repository.venues_have_collective_offers(*venues)
        has_individual_offers = offerers_repository.venues_have_individual_offers(*venues)

        has_banner_url = all(venue._bannerUrl for venue in venues if venue.isOpenToPublic)
        attributes.update(
            {
                "dms_application_submitted": any(venue.hasPendingBankAccountApplication for venue in venues),
                "dms_application_approved": all(venue.hasAcceptedBankAccountApplication for venue in venues),
                "isVirtual": any(venue.isVirtual for venue in venues),
                "isPermanent": any(venue.isPermanent for venue in venues),
                "isOpenToPublic": any(venue.isOpenToPublic for venue in venues),
                "has_offers": has_individual_offers or has_collective_offers,
                "has_collective_offers": has_collective_offers,
                "has_individual_offers": has_individual_offers,
                "has_bookings": bookings_repository.venues_have_bookings(*venues),
                "has_banner_url": has_banner_url,
            }
        )

    marketing_email_subscription = (
        # Force email subscription to True when email is used only as bookingEmail
        # Force to False when email has been removed from db, maybe replaced with another one in user and/or venue
        user.get_notification_subscriptions().marketing_email if user else bool(venues)
    )

    venues_types = set()
    # Since `venue.venueTypeCode` is not a MagicEnum
    # we have to access it differently given the state of the venue
    # (committed or flushed within a transaction)
    for venue in all_venues:
        # Not yet committed
        if isinstance(venue.venueTypeCode, offerers_models.VenueTypeCode):
            venues_types.add(venue.venueTypeCode.name)
        # Committed with the session up to date, the `venueTypeCode` is now only a string
        else:
            venues_types.add(venue.venueTypeCode)

    return models.ProAttributes(
        is_pro=True,
        is_active_pro=bool(offerers_names),
        is_user_email=bool(user),
        is_booking_email=bool(venues),
        marketing_email_subscription=marketing_email_subscription,
        offerers_names=offerers_names,
        offerers_tags=offerers_tags,
        venues_ids={venue.id for venue in all_venues},
        venues_names={venue.publicName or venue.name for venue in all_venues},
        venues_types=venues_types,
        venues_labels={venue.venueLabel.label for venue in all_venues if venue.venueLabelId},
        departement_code={
            venue.offererAddress.address.departmentCode
            for venue in all_venues
            if venue.offererAddress and venue.offererAddress.address.departmentCode
        },
        postal_code={
            venue.offererAddress.address.postalCode
            for venue in all_venues
            if venue.offererAddress and venue.offererAddress.address.postalCode
        },
        is_eac_meg=is_eac_meg,
        **attributes,
    )


def get_user_attributes(user: users_models.User) -> models.UserAttributes:
    from pcapi.core.fraud import api as fraud_api
    from pcapi.core.users.api import get_domains_credit

    user_bookings = get_user_bookings(user)
    favorites = (
        db.session.query(users_models.Favorite)
        .filter_by(userId=user.id)
        .options(joinedload(users_models.Favorite.offer).load_only(offers_models.Offer.subcategoryId))
        .order_by(users_models.Favorite.id.desc())
        .all()
    )

    last_favorite = favorites[0] if favorites else None
    most_favorite_offer_subcategories = get_most_favorite_subcategories(favorites)

    domains_credit = get_domains_credit(user, user_bookings)
    bookings_attributes = get_bookings_categories_and_subcategories(user_bookings)
    booking_venues_count = len({booking.venueId for booking in user_bookings})
    last_recredit = deposit_api.get_latest_age_related_user_recredit(user)

    has_remaining_credit = user.has_active_deposit and domains_credit is not None and bool(domains_credit.all.remaining)
    # A user becomes a former beneficiary only after the last credit is expired or spent or can no longer be claimed
    is_former_beneficiary = (user.has_beneficiary_role and not has_remaining_credit) or (
        user.has_underage_beneficiary_role and user.eligibility is None
    )
    is_current_beneficiary = user.is_beneficiary and has_remaining_credit

    user_birth_date = datetime.combine(user.birth_date, datetime.min.time()) if user.birth_date else None

    achievements = [achievement.name.value for achievement in user.achievements]
    return models.UserAttributes(
        achievements=achievements,
        booking_categories=bookings_attributes.booking_categories,
        booking_count=len(user_bookings),
        booking_subcategories=bookings_attributes.booking_subcategories,
        booking_venues_count=booking_venues_count,
        city=user.city,
        date_created=user.dateCreated,
        date_of_birth=user_birth_date,
        departement_code=user.departementCode,
        deposit_activation_date=user.deposit_activation_date,
        deposit_expiration_date=user.deposit_expiration_date,
        deposits_count=len(user.deposits),
        domains_credit=domains_credit,
        eligibility=user.eligibility,
        first_name=user.firstName,
        has_completed_id_check=fraud_api.has_user_performed_identity_check(user),
        is_active=user.isActive,
        is_beneficiary=user.is_beneficiary,
        is_current_beneficiary=is_current_beneficiary,
        is_eligible=user.is_eligible,
        is_email_validated=user.isEmailValidated,
        is_former_beneficiary=is_former_beneficiary,
        is_phone_validated=user.is_phone_validated,
        is_pro=False,
        last_booking_date=user_bookings[0].dateCreated if user_bookings else None,
        last_favorite_creation_date=last_favorite.dateCreated if last_favorite else None,
        last_name=user.lastName,
        last_recredit_type=last_recredit.recreditType if last_recredit else None,
        last_visit_date=user.lastConnectionDate,
        marketing_email_subscription=user.get_notification_subscriptions().marketing_email,
        marketing_push_subscription=user.get_notification_subscriptions().marketing_push,
        most_booked_movie_genre=bookings_attributes.most_booked_movie_genre,
        most_booked_music_type=bookings_attributes.most_booked_music_type,
        most_booked_subcategory=bookings_attributes.most_booked_subcategory,
        most_favorite_offer_subcategories=most_favorite_offer_subcategories,
        phone_number=user.phoneNumber,
        postal_code=user.postalCode,
        products_use_date={
            f"product_{TRACKED_PRODUCT_IDS[booking.stock.offer.productId]}_use": booking.dateUsed
            for booking in user_bookings
            if booking.dateUsed and booking.stock.offer.productId in TRACKED_PRODUCT_IDS
        },
        roles=[role.value for role in user.roles],
        subscribed_themes=user.get_notification_subscriptions().subscribed_themes,
        suspension_date=user.suspension_date,
        suspension_reason=user.suspension_reason,
        user_id=user.id,
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
        key=lambda kv: (len(kv[1]), sum(booking.total_amount for booking in kv[1])),
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
    if most_booked_category == pro_categories.CINEMA.id:
        cinema_bookings_by_genre = defaultdict(list)
        for booking in bookings_by_categories[pro_categories.CINEMA.id]:
            if extra_data := booking.stock.offer.extraData:
                for genre in extra_data.get("genres") or []:
                    cinema_bookings_by_genre[genre].append(booking)
        most_booked_movie_genre = _get_most_booked(cinema_bookings_by_genre)

    most_booked_music_type = None
    music_categories = (pro_categories.MUSIQUE_ENREGISTREE.id, pro_categories.MUSIQUE_LIVE.id)
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


def get_user_bookings(user: users_models.User) -> list[bookings_models.Booking]:
    return (
        db.session.query(bookings_models.Booking)
        .options(joinedload(bookings_models.Booking.venue).load_only(offerers_models.Venue.isVirtual))
        .options(
            joinedload(bookings_models.Booking.stock)
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.url,
                offers_models.Offer.productId,
                offers_models.Offer.subcategoryId,
                offers_models.Offer.name,
                offers_models.Offer._extraData,
            ),
            joinedload(bookings_models.Booking.incidents).joinedload(finance_models.BookingFinanceIncident.incident),
        )
        .filter(
            bookings_models.Booking.userId == user.id,
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
        )
        .order_by(bookings_models.Booking.dateCreated.desc())
        .all()
    )


def get_most_favorite_subcategories(favorites: list[users_models.Favorite]) -> list[str] | None:
    if not favorites:
        return None

    favorites_count = Counter([favorite.offer.subcategoryId for favorite in favorites])
    sorted_by_count = favorites_count.most_common()
    highest_count = sorted_by_count[0][1]
    return [key for (key, value) in sorted_by_count if value == highest_count]
