from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
from typing import Iterable

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.models import BankInformation
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import Offer
import pcapi.core.offers.repository as offers_repository
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus

from . import exceptions
from . import models


logger = logging.getLogger(__name__)

MAX_OFFERS_PER_OFFERER_FOR_COUNT = 9999


def get_all_venue_labels() -> list[models.VenueLabel]:
    return models.VenueLabel.query.all()


def get_all_offerers_for_user(
    user: users_models.User,
    validated: bool | None = None,
    include_non_validated_user_offerers: bool = False,
) -> sqla_orm.Query:
    """Return a query of matching, accessible offerers.

    **WARNING:** this function may return more than one row per
    offerer (for offerers that have multiple user offerers and/or
    multiple venues). Deduplication should be done by the caller (with
    `distinct()`). This function cannot call `distinct()` itself
    because it does not know how the caller wants to sort results (and
    `distinct` and `order by` clauses must match).

    **WARNING:** ``include_non_validated_user_offerers`` should only
    be used to return very restrictive informations (that the
    requesting user already knows), such as the name of the offerer.
    """
    query = models.Offerer.query.filter(models.Offerer.isActive.is_(True))

    if not user.has_admin_role:
        user_offerer_filters = [
            models.UserOfferer.userId == user.id,
            sqla.not_(models.UserOfferer.isRejected) & sqla.not_(models.UserOfferer.isDeleted),
        ]
        if not include_non_validated_user_offerers:
            user_offerer_filters.append(models.UserOfferer.isValidated)
        query = query.join(models.Offerer.UserOfferers).filter(*user_offerer_filters)

    if validated is not None:
        if validated:
            query = query.filter(models.Offerer.isValidated)
        else:
            query = query.filter(models.Offerer.isWaitingForValidation)
    else:
        query = query.filter(sqla.not_(models.Offerer.isRejected))

    return query


def get_ids_of_venues_with_offers(offererIds: list[int]) -> Iterable[int]:
    """Return a list with ids of venues with non-draft offers.

    Venues that do not have any offers are not included.
    """
    venues = (
        db.session.query(models.Venue).filter(
            models.Venue.managingOffererId.in_(offererIds),
            sqla.or_(
                # Does the venue has Offers
                sqla.select(1)
                .select_from(Offer)
                .where(sqla.and_(Offer.venueId == models.Venue.id, Offer.validation != OfferValidationStatus.DRAFT))
                .exists(),
                # Does the venue has CollectiveOffers
                sqla.select(1)
                .select_from(CollectiveOffer)
                .where(
                    sqla.and_(
                        CollectiveOffer.venueId == models.Venue.id,
                        CollectiveOffer.validation != OfferValidationStatus.DRAFT,
                    )
                )
                .exists(),
                # Does the venue has CollectiveOfferTemplates
                sqla.select(1)
                .select_from(CollectiveOfferTemplate)
                .where(
                    sqla.and_(
                        CollectiveOfferTemplate.venueId == models.Venue.id,
                        CollectiveOfferTemplate.validation != OfferValidationStatus.DRAFT,
                    )
                )
                .exists(),
            ),
        )
    ).with_entities(models.Venue.id)
    return [venue_id for venue_id, in venues]


def get_filtered_venues(
    pro_user_id: int,
    user_is_admin: bool,
    active_offerers_only: bool | None = False,
    offerer_id: int | None = None,
    validated_offerer: bool | None = None,
) -> list[models.Venue]:
    query = (
        models.Venue.query.join(models.Offerer, models.Offerer.id == models.Venue.managingOffererId)
        .join(models.UserOfferer, models.UserOfferer.offererId == models.Offerer.id)
        .options(sqla_orm.joinedload(models.Venue.managingOfferer))
        .options(sqla_orm.joinedload(models.Venue.collectiveDomains))
        .options(sqla_orm.joinedload(models.Venue.reimbursement_point_links))
        .options(sqla_orm.joinedload(models.Venue.bankInformation))
    )
    if not user_is_admin:
        query = query.filter(
            models.UserOfferer.userId == pro_user_id,
            models.UserOfferer.isValidated,
        )

    if validated_offerer is not None:
        if validated_offerer:
            query = query.filter(models.Offerer.isValidated)
        else:
            query = query.filter(models.Offerer.isWaitingForValidation)
    else:
        query = query.filter(sqla.not_(models.Offerer.isRejected))

    if active_offerers_only:
        query = query.filter(models.Offerer.isActive.is_(True))

    if offerer_id:
        query = query.filter(models.Venue.managingOffererId == offerer_id)

    return query.order_by(models.Venue.name).all()


def get_venue_stats(venue_id: int) -> tuple[int, int, int, int]:
    active_bookings_quantity = bookings_repository.get_active_bookings_quantity_for_venue(venue_id)
    validated_bookings_count = bookings_repository.get_validated_bookings_quantity_for_venue(venue_id)
    active_offers_count = offers_repository.get_active_offers_count_for_venue(venue_id)
    sold_out_offers_count = offers_repository.get_sold_out_offers_count_for_venue(venue_id)

    return (
        active_bookings_quantity,
        validated_bookings_count,
        active_offers_count,
        sold_out_offers_count,
    )


def get_api_key_prefixes(offerer_id: int) -> list[str]:
    return [
        prefix for prefix, in models.ApiKey.query.filter_by(offererId=offerer_id).with_entities(models.ApiKey.prefix)
    ]


def find_offerer_by_siren(siren: str) -> models.Offerer | None:
    return models.Offerer.query.filter_by(siren=siren).one_or_none()


def find_offerer_by_id(offerer_id: int) -> models.Offerer | None:
    return models.Offerer.query.filter_by(id=offerer_id).one_or_none()


def filter_query_where_user_is_user_offerer_and_is_validated(query: BaseQuery, user: users_models.User) -> BaseQuery:
    return query.join(models.UserOfferer).filter_by(user=user).filter(models.UserOfferer.isValidated)


def find_venue_by_id(venue_id: int) -> models.Venue | None:
    return (
        models.Venue.query.filter_by(id=venue_id)
        .options(sqla.orm.joinedload(models.Venue.venueLabel))
        .options(sqla.orm.joinedload(models.Venue.managingOfferer))
        .one_or_none()
    )


def find_venue_and_provider_by_id(venue_id: int) -> models.Venue | None:
    return (
        models.Venue.query.filter_by(id=venue_id)
        .options(sqla.orm.joinedload(models.Venue.venueLabel))
        .options(sqla.orm.joinedload(models.Venue.managingOfferer))
        .options(sqla.orm.joinedload(models.Venue.venueProviders))
        .one_or_none()
    )


def find_relative_venue_by_id(venue_id: int, permanent_only: bool = False) -> list[models.Venue]:
    aliased_venue = sqla.orm.aliased(models.Venue)

    query = db.session.query(models.Venue)
    query = query.join(models.Offerer, models.Venue.managingOfferer)
    query = query.join(aliased_venue, models.Offerer.managedVenues)
    query = query.filter(
        # constraint on retrieved venues
        sqla.not_(models.Venue.isVirtual),
        # constraint on seached venue
        sqla.not_(aliased_venue.isVirtual),
        aliased_venue.id == venue_id,
    )
    if permanent_only:
        query = query.filter(models.Venue.isPermanent, aliased_venue.isPermanent)
    query = query.options(sqla.orm.joinedload(models.Venue.contact))
    query = query.options(sqla.orm.joinedload(models.Venue.venueLabel))
    query = query.options(sqla.orm.joinedload(models.Venue.managingOfferer))
    # group venues by offerer
    query = query.order_by(models.Venue.managingOffererId, models.Venue.name)
    return query.all()


def find_venue_by_siret(siret: str) -> models.Venue | None:
    return models.Venue.query.filter_by(siret=siret).one_or_none()


def find_virtual_venue_by_offerer_id(offerer_id: int) -> models.Venue | None:
    return models.Venue.query.filter_by(managingOffererId=offerer_id, isVirtual=True).first()


def find_venues_of_offerers_with_no_offer_and_at_least_one_physical_venue_and_validated_x_days_ago(
    days: int,
) -> BaseQuery:
    validated_x_days_ago_with_physical_venue_offerers_ids_subquery = (
        sqla.select(models.Offerer.id)
        .join(models.Venue, models.Offerer.id == models.Venue.managingOffererId)
        .filter(models.Offerer.isValidated)
        .filter(sqla.cast(models.Offerer.dateValidated, sqla.Date) == (date.today() - timedelta(days=days)))
        .filter(sqla.not_(models.Venue.isVirtual))
        .distinct()
    )

    offerers_ids_with_no_offers_subquery = (
        sqla.select(models.Venue.managingOffererId)
        .filter(models.Venue.managingOffererId.in_(validated_x_days_ago_with_physical_venue_offerers_ids_subquery))
        .outerjoin(Offer, models.Venue.id == Offer.venueId)
        .outerjoin(CollectiveOffer, models.Venue.id == CollectiveOffer.venueId)
        .outerjoin(CollectiveOfferTemplate, models.Venue.id == CollectiveOfferTemplate.venueId)
        .group_by(models.Venue.managingOffererId)
        .having(sqla.func.count(Offer.id) == 0)
        .having(sqla.func.count(CollectiveOffer.id) == 0)
        .having(sqla.func.count(CollectiveOfferTemplate.id) == 0)
    )

    return models.Venue.query.with_entities(models.Venue.id, models.Venue.bookingEmail).filter(
        models.Venue.managingOffererId.in_(offerers_ids_with_no_offers_subquery)
    )


def has_digital_venue_with_at_least_one_offer(offerer_id: int) -> bool:
    return db.session.query(
        models.Venue.query.join(Offer, models.Venue.id == Offer.venueId)
        .filter(models.Venue.managingOffererId == offerer_id)
        .filter(models.Venue.isVirtual.is_(True))
        .filter(Offer.status != OfferValidationStatus.DRAFT.name)
        .exists()
    ).scalar()


def get_by_offer_id(offer_id: int) -> models.Offerer:
    offerer = models.Offerer.query.join(models.Venue).join(Offer).filter_by(id=offer_id).one_or_none()
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_offer_id(collective_offer_id: int) -> models.Offerer:
    offerer = (
        models.Offerer.query.join(models.Venue)
        .join(CollectiveOffer)
        .filter(CollectiveOffer.id == collective_offer_id)
        .one_or_none()
    )
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_offer_template_id(collective_offer_id: int) -> models.Offerer:
    offerer = (
        models.Offerer.query.join(models.Venue)
        .join(CollectiveOfferTemplate)
        .filter(CollectiveOfferTemplate.id == collective_offer_id)
        .one_or_none()
    )
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_stock_id(collective_stock_id: int) -> models.Offerer:
    offerer = (
        models.Offerer.query.join(models.Venue)
        .join(CollectiveOffer)
        .join(CollectiveStock)
        .filter(CollectiveStock.id == collective_stock_id)
        .one_or_none()
    )
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return offerer


def find_new_offerer_user_email(offerer_id: int) -> str:
    result_tuple = (
        models.UserOfferer.query.filter_by(offererId=offerer_id)
        .join(users_models.User)
        .with_entities(users_models.User.email)
        .first()
    )
    if result_tuple:
        return result_tuple[0]
    raise exceptions.CannotFindOffererUserEmail()


def check_if_siren_already_exists(siren: str) -> bool:
    return db.session.query(db.session.query(models.Offerer.id).filter(models.Offerer.siren == siren).exists())


def find_siren_by_offerer_id(offerer_id: int) -> str:
    siren = models.Offerer.query.filter_by(id=offerer_id).with_entities(models.Offerer.siren).scalar()

    if siren:
        return siren

    raise exceptions.CannotFindOffererSiren


def venues_have_offers(*venues: models.Venue) -> bool:
    """At least one venue which has email as bookingEmail has at least one active offer"""
    return db.session.query(
        Offer.query.filter(
            Offer.venueId.in_([venue.id for venue in venues]), Offer.status == OfferStatus.ACTIVE.name
        ).exists()
    ).scalar()


def offerer_has_venue_with_adage_id(offerer_id: int) -> bool:
    query = db.session.query(models.Venue.id)
    query = query.join(models.Offerer, models.Venue.managingOfferer)
    query = query.filter(
        models.Venue.adageId.is_not(None),
        models.Venue.adageId != "",
        models.Offerer.id == offerer_id,
    )
    return bool(query.count())


def dms_token_exists(dms_token: str) -> bool:
    return db.session.query(models.Venue.query.filter_by(dmsToken=dms_token).exists()).scalar()


def get_venues_educational_statuses() -> list[models.VenueEducationalStatus]:
    return db.session.query(models.VenueEducationalStatus).order_by(models.VenueEducationalStatus.name).all()


def find_available_reimbursement_points_for_offerer(offerer_id: int) -> list[models.Venue]:
    """
    Returns a list of Venues whose SIRETs can be used to reimburse bookings, and their bank info,
    ordered by common_name
    """
    return (
        models.Venue.query.join(BankInformation)
        .filter(
            BankInformation.status == BankInformationStatus.ACCEPTED,
            models.Venue.managingOffererId == offerer_id,
        )
        .options(sqla_orm.joinedload(models.Venue.bankInformation))
        .order_by(models.Venue.common_name)
        .all()
    )


def get_venue_by_id(venue_id: int) -> models.Venue:
    return models.Venue.query.get(venue_id)


def find_offerers_validated_3_days_ago_with_no_venues() -> list[models.Offerer]:
    subquery_get_physical_venues = db.session.query(models.Venue.managingOffererId).where(
        sqla.not_(models.Venue.isVirtual)
    )

    subquery_get_digital_venues_with_offers = (
        db.session.query(models.Venue.managingOffererId)
        .join(Offer)
        .where(models.Venue.isVirtual, Offer.venueId == models.Venue.id)
    )
    # when offerer is created, a digital venue is created by default
    # query should return all offerers validated 3 days ago with only digital venue without offers

    return (
        db.session.query(models.Offerer)
        .filter(models.Offerer.id.not_in(subquery_get_physical_venues))
        .filter(models.Offerer.id.not_in(subquery_get_digital_venues_with_offers))
        .filter(
            models.Offerer.isActive.is_(True),
            sqla.cast(models.Offerer.dateValidated, sqla.Date) == (date.today() - timedelta(days=3)),
        )
        .all()
    )


def get_emails_by_venue(venue: models.Venue) -> set[str]:
    """
    Get all emails for which pro attributes may be modified when the venue is updated or deleted.
    Be careful: venue attributes are no longer available after venue object is deleted, call this function before.
    """
    emails = {
        email
        for email, in users_models.User.query.join(users_models.User.UserOfferers)
        .filter_by(offererId=venue.managingOffererId)
        .with_entities(users_models.User.email)
    }
    if venue.bookingEmail:
        emails.add(venue.bookingEmail)
    return emails


def get_emails_by_offerer(offerer: models.Offerer) -> set[str]:
    """
    Get all emails for which pro attributes may be modified when the offerer is updated or deleted.
    Any bookingEmail in a venue should be updated in sendinblue when offerer is disabled, deleted or its name changed
    """
    emails = {
        email
        for email, in users_models.User.query.join(users_models.User.UserOfferers)
        .filter_by(offererId=offerer.id)
        .with_entities(users_models.User.email)
    }
    emails |= {
        email
        for email, in models.Venue.query.filter_by(managingOffererId=offerer.id).with_entities(
            models.Venue.bookingEmail
        )
    }
    emails.discard(None)
    return emails


def find_venues_of_offerer_from_siret(siret: str) -> tuple[models.Offerer | None, list[models.Venue]]:
    siren = siret[:9]
    offerer = models.Offerer.query.filter(models.Offerer.siren == siren).one_or_none()
    if not offerer:
        return None, []
    venues = (
        models.Venue.query.join(models.Offerer)
        .filter(models.Offerer.siren == siren)
        .order_by(models.Venue.common_name)
        .all()
    )
    return offerer, venues


def get_offerer_and_extradata(offerer_id: int) -> models.Offerer | None:
    """
    Return and offerer and some extra data regarding it.
        - hasValidBankAccount
        - hasPendingBankAccount
        - hasNonFreeOffers
    """
    has_non_free_offers_subquery = (
        sqla.select(1)
        .select_from(offers_models.Stock)
        .join(models.Venue, models.Venue.managingOffererId == models.Offerer.id)
        .join(
            offers_models.Offer,
            sqla.and_(
                offers_models.Stock.offerId == Offer.id,
                offers_models.Stock.price > 0,
                offers_models.Stock.isSoftDeleted.is_(False),
                offers_models.Offer.isActive.is_(True),
                offers_models.Offer.venueId == models.Venue.id,
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_non_free_collective_offers_subquery = (
        sqla.select(1)
        .select_from(CollectiveStock)
        .join(models.Venue, models.Venue.managingOffererId == models.Offerer.id)
        .join(
            CollectiveOffer,
            sqla.and_(
                CollectiveStock.collectiveOfferId == CollectiveOffer.id,
                CollectiveStock.price > 0,
                CollectiveOffer.isActive.is_(True),
                CollectiveOffer.venueId == models.Venue.id,
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_valid_bank_account_subquery = (
        sqla.select(1)
        .select_from(finance_models.BankAccount)
        .where(
            sqla.and_(
                finance_models.BankAccount.offererId == models.Offerer.id,
                finance_models.BankAccount.isActive.is_(True),
                finance_models.BankAccount.status == finance_models.BankAccountApplicationStatus.ACCEPTED,
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_pending_bank_account_subquery = (
        sqla.select(1)
        .select_from(finance_models.BankAccount)
        .where(
            sqla.and_(
                finance_models.BankAccount.offererId == models.Offerer.id,
                finance_models.BankAccount.isActive.is_(True),
                finance_models.BankAccount.status.in_(
                    [
                        finance_models.BankAccountApplicationStatus.DRAFT,
                        finance_models.BankAccountApplicationStatus.ON_GOING,
                    ]
                ),
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    return (
        db.session.query(
            models.Offerer,
            sqla.or_(has_non_free_offers_subquery, has_non_free_collective_offers_subquery).label("hasNonFreeOffer"),
            has_valid_bank_account_subquery.label("hasValidBankAccount"),
            has_pending_bank_account_subquery.label("hasPendingBankAccount"),
        )
        .filter(models.Offerer.id == offerer_id)
        .outerjoin(models.Venue, models.Venue.managingOffererId == models.Offerer.id)
        .options(
            sqla_orm.contains_eager(models.Offerer.managedVenues).load_only(
                models.Venue.id, models.Venue.siret, models.Venue.publicName, models.Venue.name
            )
        )
        .options(sqla_orm.load_only(models.Offerer.id, models.Offerer.name))
        .one_or_none()
    )


def get_offerer_bank_accounts(offerer_id: int) -> models.Offerer | None:
    """
    Return an Offerer with its accounting data and related venues:

    - Existing bank accounts (possibly none and only active & not (refused or without confirmation) ones)
    - Linked venues to its bank accounts (possibly none and only current ones)
    - Managed venues by the offerer (possibly none)
    """
    venue_has_offers_subquery = db.session.query(
        sqla.select(1)
        .select_from(offers_models.Offer)
        .where(
            offers_models.Offer.venueId == models.Venue.id,
            offers_models.Offer.isActive.is_(True),
        )
        .correlate(models.Venue)
        .exists()
    ).scalar_subquery()

    return (
        models.Offerer.query.filter_by(id=offerer_id)
        .outerjoin(
            finance_models.BankAccount,
            sqla.and_(
                finance_models.BankAccount.offererId == models.Offerer.id,
                finance_models.BankAccount.isActive.is_(True),
                finance_models.BankAccount.status.not_in(
                    (
                        finance_models.BankAccountApplicationStatus.WITHOUT_CONTINUATION,
                        finance_models.BankAccountApplicationStatus.REFUSED,
                    )
                ),
            ),
        )
        .outerjoin(
            models.Venue,
            sqla.and_(
                models.Offerer.id == models.Venue.managingOffererId,
                sqla.or_(
                    models.Venue.isVirtual.is_(False),
                    sqla.and_(
                        models.Venue.isVirtual.is_(True),
                        venue_has_offers_subquery,
                    ),
                ),
            ),
        )
        .outerjoin(
            models.VenuePricingPointLink,
            sqla.and_(
                models.VenuePricingPointLink.venueId == models.Venue.id,
                models.VenuePricingPointLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .outerjoin(
            models.VenueBankAccountLink,
            sqla.and_(
                finance_models.BankAccount.id == models.VenueBankAccountLink.bankAccountId,
                models.Venue.id == models.VenueBankAccountLink.venueId,
                models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .options(
            sqla_orm.contains_eager(models.Offerer.bankAccounts).contains_eager(finance_models.BankAccount.venueLinks)
        )
        .options(
            sqla_orm.contains_eager(models.Offerer.managedVenues)
            .load_only(models.Venue.id, models.Venue.siret, models.Venue.publicName, models.Venue.name)
            .contains_eager(models.Venue.bankAccountLinks)
        )
        .options(
            sqla_orm.contains_eager(models.Offerer.managedVenues)
            .contains_eager(models.Venue.pricing_point_links)
            .load_only(models.VenuePricingPointLink.id)
        )
        .options(sqla_orm.load_only(models.Offerer.id, models.Offerer.name))
        .order_by(finance_models.BankAccount.dateCreated)
        .populate_existing()
        .one_or_none()
    )


def get_venues_with_non_free_offers_without_bank_accounts(offerer_id: int) -> list[int]:
    """
    Venue without a bank account is either a venue without any VenueBankAccountLink at all
    or without up to date VenueBankAccountLink (timespan.upper is None)
    """
    venue_with_non_free_offers = (
        models.Venue.query.filter(
            models.Venue.managingOffererId == offerer_id,
            models.VenueBankAccountLink.timespan
            == None,  # Because as we LEFT OUTER JOIN on VenueReimbursementPointLink, timespan column can be NULL
            # i.e. only Venue without any VenueBankAccountLink or only deprecated ones.
            sqla.or_(
                offers_models.Stock.query.join(
                    offers_models.Offer,
                    sqla.and_(
                        offers_models.Stock.offerId == offers_models.Offer.id,
                        offers_models.Offer.venueId == models.Venue.id,
                        offers_models.Stock.price > 0,
                    ),
                ).exists(),
                CollectiveStock.query.join(
                    CollectiveOffer,
                    sqla.and_(
                        CollectiveStock.collectiveOfferId == CollectiveOffer.id,
                        CollectiveOffer.venueId == models.Venue.id,
                        CollectiveStock.price > 0,
                    ),
                ).exists(),
            ),
        )
        .join(models.Offerer)
        .outerjoin(
            models.VenueBankAccountLink,
            sqla.and_(
                models.VenueBankAccountLink.venueId == models.Venue.id,
                models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .with_entities(models.Venue.id)
    )
    return [venue.id for venue in venue_with_non_free_offers]


def get_number_of_bookable_offers_for_offerer(offerer_id: int) -> int:
    return (
        offers_models.Offer.query.with_entities(offers_models.Offer.id)
        .distinct()
        .join(models.Venue)
        .join(offers_models.Stock)
        .filter(
            models.Venue.managingOffererId == offerer_id,
            offers_models.Offer.validation == OfferValidationStatus.APPROVED,
            offers_models.Offer.is_eligible_for_search,
        )
        .limit(MAX_OFFERS_PER_OFFERER_FOR_COUNT)
        .count()
    )


def get_number_of_pending_offers_for_offerer(offerer_id: int) -> int:
    return (
        offers_models.Offer.query.with_entities(offers_models.Offer.id)
        .join(models.Venue)
        .filter(
            models.Venue.managingOffererId == offerer_id,
            offers_models.Offer.validation == OfferValidationStatus.PENDING,
        )
        .limit(MAX_OFFERS_PER_OFFERER_FOR_COUNT)
        .count()
    )


def get_number_of_bookable_collective_offers_for_offerer(offerer_id: int) -> int:
    return (
        CollectiveOffer.query.join(models.Venue)
        .filter(
            models.Venue.managingOffererId == offerer_id,
            CollectiveOffer.isActive,
            CollectiveOffer.validation == OfferValidationStatus.APPROVED,
        )
        .with_entities(CollectiveOffer.id)
        .union_all(
            CollectiveOfferTemplate.query.join(models.Venue)
            .filter(
                models.Venue.managingOffererId == offerer_id,
                CollectiveOfferTemplate.isActive,
                CollectiveOfferTemplate.validation == OfferValidationStatus.APPROVED,
            )
            .with_entities(CollectiveOfferTemplate.id)
        )
        .limit(MAX_OFFERS_PER_OFFERER_FOR_COUNT)
        .count()
    )


def get_number_of_pending_collective_offers_for_offerer(offerer_id: int) -> int:
    return (
        CollectiveOffer.query.join(models.Venue)
        .filter(
            models.Venue.managingOffererId == offerer_id, CollectiveOffer.validation == OfferValidationStatus.PENDING
        )
        .with_entities(CollectiveOffer.id)
        .union_all(
            CollectiveOfferTemplate.query.join(models.Venue)
            .filter(
                models.Venue.managingOffererId == offerer_id,
                CollectiveOfferTemplate.validation == OfferValidationStatus.PENDING,
            )
            .with_entities(CollectiveOfferTemplate.id)
        )
        .limit(MAX_OFFERS_PER_OFFERER_FOR_COUNT)
        .count()
    )
