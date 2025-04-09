import datetime
import logging
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models import offer_mixin

from . import exceptions
from . import models


logger = logging.getLogger(__name__)

MAX_OFFERS_PER_OFFERER_FOR_COUNT = 500


def get_all_venue_labels() -> list[models.VenueLabel]:
    return models.VenueLabel.query.all()


def get_all_offerers_for_user(
    user: users_models.User,
    validated: bool | None = None,
    include_non_validated_user_offerers: bool = False,
) -> sa_orm.Query:
    """Return a query of matching, accessible offerers.

    **WARNING:** this function may return more than one row per
    offerer (for offerers that have multiple user offerers and/or
    multiple venues). Deduplication should be done by the caller (with
    `distinct()`). This function cannot call `distinct()` itself
    because it does not know how the caller wants to sort results (and
    `distinct` and `order by` clauses must match).

    **WARNING:** ``include_non_validated_user_offerers`` should only
    be used to return very restrictive information (that the
    requesting user already knows), such as the name of the offerer.
    """
    query = models.Offerer.query.filter(models.Offerer.isActive.is_(True))

    if not user.has_admin_role:
        user_offerer_filters = [
            models.UserOfferer.userId == user.id,
            sa.not_(models.UserOfferer.isRejected) & sa.not_(models.UserOfferer.isDeleted),
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
        query = query.filter(sa.not_(models.Offerer.isRejected))

    return query


def get_ids_of_venues_with_offers(offererIds: list[int]) -> typing.Iterable[int]:
    """Return a list with ids of venues with non-draft offers.

    Venues that do not have any offers are not included.
    """
    venues = (
        db.session.query(models.Venue).filter(
            models.Venue.managingOffererId.in_(offererIds),
            sa.or_(
                # Does the venue has Offers
                sa.select(1)
                .select_from(offers_models.Offer)
                .where(
                    sa.and_(
                        offers_models.Offer.venueId == models.Venue.id,
                        offers_models.Offer.validation != offer_mixin.OfferValidationStatus.DRAFT,
                    )
                )
                .exists(),
                # Does the venue has CollectiveOffers
                sa.select(1)
                .select_from(educational_models.CollectiveOffer)
                .where(
                    sa.and_(
                        educational_models.CollectiveOffer.venueId == models.Venue.id,
                        educational_models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.DRAFT,
                    )
                )
                .exists(),
                # Does the venue has CollectiveOfferTemplates
                sa.select(1)
                .select_from(educational_models.CollectiveOfferTemplate)
                .where(
                    sa.and_(
                        educational_models.CollectiveOfferTemplate.venueId == models.Venue.id,
                        educational_models.CollectiveOfferTemplate.validation
                        != offer_mixin.OfferValidationStatus.DRAFT,
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
        .options(sa_orm.joinedload(models.Venue.managingOfferer))
        .options(sa_orm.joinedload(models.Venue.collectiveDomains))
        .options(sa_orm.joinedload(models.Venue.accessibilityProvider))
        .options(sa_orm.joinedload(models.Venue.offererAddress).joinedload(models.OffererAddress.address))
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
        query = query.filter(sa.not_(models.Offerer.isRejected))

    if active_offerers_only:
        query = query.filter(models.Offerer.isActive.is_(True))

    if offerer_id:
        query = query.filter(models.Venue.managingOffererId == offerer_id)

    return query.order_by(models.Venue.name).all()


def get_api_key_prefixes(offerer_id: int) -> list[str]:
    return [
        prefix for prefix, in models.ApiKey.query.filter_by(offererId=offerer_id).with_entities(models.ApiKey.prefix)
    ]


def find_offerer_by_siren(siren: str) -> models.Offerer | None:
    return models.Offerer.query.filter_by(siren=siren).one_or_none()


def find_offerer_by_id(offerer_id: int) -> models.Offerer | None:
    return models.Offerer.query.filter_by(id=offerer_id).one_or_none()


def find_venue_by_id(venue_id: int, load_address: bool = False) -> models.Venue | None:
    query = (
        models.Venue.query.filter_by(id=venue_id)
        .options(sa_orm.joinedload(models.Venue.venueLabel))
        .options(sa_orm.joinedload(models.Venue.managingOfferer))
    )

    if load_address:
        query = query.options(sa_orm.joinedload(models.Venue.offererAddress).joinedload(models.OffererAddress.address))

    return query.one_or_none()


def find_venue_and_provider_by_id(venue_id: int) -> models.Venue | None:
    return (
        models.Venue.query.filter_by(id=venue_id)
        .options(sa_orm.joinedload(models.Venue.venueLabel))
        .options(sa_orm.joinedload(models.Venue.managingOfferer))
        .options(sa_orm.joinedload(models.Venue.venueProviders))
        .one_or_none()
    )


def find_relative_venue_by_id(venue_id: int) -> list[models.Venue]:
    aliased_venue = sa_orm.aliased(models.Venue)

    query = db.session.query(models.Venue)
    query = query.join(models.Offerer, models.Venue.managingOfferer)
    query = query.join(aliased_venue, models.Offerer.managedVenues)
    query = query.filter(
        # constraint on retrieved venues
        sa.not_(models.Venue.isVirtual),
        # constraint on searched venue
        sa.not_(aliased_venue.isVirtual),
        aliased_venue.id == venue_id,
    )
    query = query.options(sa_orm.joinedload(models.Venue.contact))
    query = query.options(sa_orm.joinedload(models.Venue.venueLabel))
    query = query.options(sa_orm.joinedload(models.Venue.managingOfferer))
    query = query.options(sa_orm.joinedload(models.Venue.offererAddress).joinedload(models.OffererAddress.address))
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
        sa.select(models.Offerer.id)
        .join(models.Venue, models.Offerer.id == models.Venue.managingOffererId)
        .filter(models.Offerer.isValidated)
        .filter(
            sa.cast(models.Offerer.dateValidated, sa.Date) == (datetime.date.today() - datetime.timedelta(days=days))
        )
        .filter(sa.not_(models.Venue.isVirtual))
        .distinct()
    )

    offerers_ids_with_no_offers_subquery = (
        sa.select(models.Venue.managingOffererId)
        .filter(models.Venue.managingOffererId.in_(validated_x_days_ago_with_physical_venue_offerers_ids_subquery))
        .outerjoin(offers_models.Offer, models.Venue.id == offers_models.Offer.venueId)
        .outerjoin(educational_models.CollectiveOffer, models.Venue.id == educational_models.CollectiveOffer.venueId)
        .outerjoin(
            educational_models.CollectiveOfferTemplate,
            models.Venue.id == educational_models.CollectiveOfferTemplate.venueId,
        )
        .group_by(models.Venue.managingOffererId)
        .having(sa.func.count(offers_models.Offer.id) == 0)
        .having(sa.func.count(educational_models.CollectiveOffer.id) == 0)
        .having(sa.func.count(educational_models.CollectiveOfferTemplate.id) == 0)
    )

    return models.Venue.query.with_entities(models.Venue.id, models.Venue.bookingEmail).filter(
        models.Venue.managingOffererId.in_(offerers_ids_with_no_offers_subquery)
    )


def has_digital_venue_with_at_least_one_offer(offerer_id: int) -> bool:
    return db.session.query(
        models.Venue.query.join(offers_models.Offer, models.Venue.id == offers_models.Offer.venueId)
        .filter(models.Venue.managingOffererId == offerer_id)
        .filter(models.Venue.isVirtual.is_(True))
        .filter(offers_models.Offer.status != offer_mixin.OfferValidationStatus.DRAFT.name)
        .exists()
    ).scalar()


def get_by_offer_id(offer_id: int) -> models.Offerer:
    offerer = models.Offerer.query.join(models.Venue).join(offers_models.Offer).filter_by(id=offer_id).one_or_none()
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_offer_id(collective_offer_id: int) -> models.Offerer:
    offerer = (
        models.Offerer.query.join(models.Venue)
        .join(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.id == collective_offer_id)
        .one_or_none()
    )
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_offer_template_id(collective_offer_id: int) -> models.Offerer:
    offerer = (
        models.Offerer.query.join(models.Venue)
        .join(educational_models.CollectiveOfferTemplate)
        .filter(educational_models.CollectiveOfferTemplate.id == collective_offer_id)
        .one_or_none()
    )
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_stock_id(collective_stock_id: int) -> models.Offerer:
    offerer = (
        models.Offerer.query.join(models.Venue)
        .join(educational_models.CollectiveOffer)
        .join(educational_models.CollectiveStock)
        .filter(educational_models.CollectiveStock.id == collective_stock_id)
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
        offers_models.Offer.query.filter(
            offers_models.Offer.venueId.in_([venue.id for venue in venues]),
            offers_models.Offer.status == offer_mixin.OfferStatus.ACTIVE.name,
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


def get_venue_by_id(venue_id: int) -> models.Venue:
    return models.Venue.query.get(venue_id)


def get_venues_by_ids(ids: typing.Collection[int]) -> typing.Collection[models.Venue]:
    return models.Venue.query.filter(models.Venue.id.in_(ids)).options(sa_orm.joinedload(models.Venue.googlePlacesInfo))


def get_venue_ids_by_offerer_ids(ids: typing.Collection[int]) -> typing.Collection[int]:
    query = models.Venue.query.filter(models.Venue.managingOffererId.in_(ids)).with_entities(models.Venue.id)
    return [v.id for v in query]


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
        - hasBankAccountWithPendingCorrections
        - isOnboarded
        - hasHeadlineOffer
    """
    has_non_free_offers_subquery = (
        sa.select(1)
        .select_from(offers_models.Stock)
        .join(models.Venue, models.Venue.managingOffererId == models.Offerer.id)
        .join(
            offers_models.Offer,
            sa.and_(
                offers_models.Stock.offerId == offers_models.Offer.id,
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
        sa.select(1)
        .select_from(educational_models.CollectiveStock)
        .join(models.Venue, models.Venue.managingOffererId == models.Offerer.id)
        .join(
            educational_models.CollectiveOffer,
            sa.and_(
                educational_models.CollectiveStock.collectiveOfferId == educational_models.CollectiveOffer.id,
                educational_models.CollectiveStock.price > 0,
                educational_models.CollectiveOffer.isActive.is_(True),
                educational_models.CollectiveOffer.venueId == models.Venue.id,
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_valid_bank_account_subquery = (
        sa.select(1)
        .select_from(finance_models.BankAccount)
        .where(
            sa.and_(
                finance_models.BankAccount.offererId == models.Offerer.id,
                finance_models.BankAccount.isActive.is_(True),
                finance_models.BankAccount.status == finance_models.BankAccountApplicationStatus.ACCEPTED,
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_active_offers_subquery = (
        sa.select(1)
        .select_from(offers_models.Stock)
        .join(models.Venue, models.Venue.managingOffererId == models.Offerer.id)
        .join(
            offers_models.Offer,
            sa.and_(
                offers_models.Stock.offerId == offers_models.Offer.id,
                offers_models.Stock.isSoftDeleted.is_(False),
                offers_models.Offer.isActive.is_(True),
                offers_models.Offer.venueId == models.Venue.id,
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_pending_bank_account_subquery = (
        sa.select(1)
        .select_from(finance_models.BankAccount)
        .where(
            sa.and_(
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

    has_bank_account_with_pending_corrections_subquery = (
        sa.select(1)
        .select_from(finance_models.BankAccount)
        .where(
            sa.and_(
                finance_models.BankAccount.offererId == models.Offerer.id,
                finance_models.BankAccount.isActive.is_(True),
                finance_models.BankAccount.status
                == finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS,
            ),
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_non_draft_offers = (
        sa.select(1)
        .select_from(offers_models.Offer)
        .join(models.Venue, models.Venue.managingOffererId == models.Offerer.id)
        .where(
            sa.and_(
                offers_models.Offer.venueId == models.Venue.id,
                offers_models.Offer.validation != offer_mixin.OfferValidationStatus.DRAFT,
            )
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_adage_id = (
        sa.select(1)
        .select_from(models.Venue)
        .where(sa.and_(models.Venue.managingOffererId == models.Offerer.id, sa.not_(models.Venue.adageId.is_(None))))
        .correlate(models.Offerer)
        .exists()
    )

    has_collective_application = (
        sa.select(1)
        .select_from(models.Venue)
        .join(
            educational_models.CollectiveDmsApplication,
            models.Venue.siret == educational_models.CollectiveDmsApplication.siret,
        )
        .where(
            models.Venue.managingOffererId == models.Offerer.id,
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_headline_offer = (
        sa.select(1)
        .select_from(offers_models.Offer)
        .join(models.Venue, offers_models.Offer.venueId == models.Venue.id)
        .join(models.Offerer, models.Venue.managingOffererId == models.Offerer.id)
        .join(offers_models.HeadlineOffer, offers_models.HeadlineOffer.offerId == offers_models.Offer.id)
        .where(
            sa.and_(
                models.Offerer.id == offerer_id,
                offers_models.HeadlineOffer.isActive == True,
            )
        )
        .correlate(models.Offerer)
        .exists()
    )

    has_partner_page = (
        sa.select(1)
        .select_from(offers_models.Offer)
        .join(models.Venue, offers_models.Offer.venueId == models.Venue.id)
        .where(
            models.Offerer.isActive.is_(True),
            models.Venue.isPermanent.is_(True),
            models.Venue.isVirtual.is_(False),
            models.Offerer.id == models.Venue.managingOffererId,
        )
        .correlate(models.Offerer)
        .exists()
    )

    return (
        db.session.query(
            models.Offerer,
            sa.or_(has_non_free_offers_subquery, has_non_free_collective_offers_subquery).label("hasNonFreeOffer"),
            has_valid_bank_account_subquery.label("hasValidBankAccount"),
            has_pending_bank_account_subquery.label("hasPendingBankAccount"),
            has_active_offers_subquery.label("hasActiveOffer"),
            has_bank_account_with_pending_corrections_subquery.label("hasBankAccountWithPendingCorrections"),
            sa.or_(has_adage_id, has_collective_application, has_non_draft_offers).label("isOnboarded"),
            has_headline_offer.label("hasHeadlineOffer"),
            has_partner_page.label("hasPartnerPage"),
        )
        .filter(models.Offerer.id == offerer_id)
        .options(
            sa_orm.load_only(models.Offerer.id, models.Offerer.name),
            sa_orm.selectinload(models.Offerer.managedVenues).with_expression(
                models.Venue._has_partner_page, models.Venue.has_partner_page
            ),
        )
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
        sa.select(1)
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
            sa.and_(
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
            sa.and_(
                models.Offerer.id == models.Venue.managingOffererId,
                sa.or_(
                    models.Venue.isVirtual.is_(False),
                    sa.and_(
                        models.Venue.isVirtual.is_(True),
                        venue_has_offers_subquery,
                    ),
                ),
            ),
        )
        .outerjoin(
            models.VenuePricingPointLink,
            sa.and_(
                models.VenuePricingPointLink.venueId == models.Venue.id,
                models.VenuePricingPointLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .outerjoin(
            models.VenueBankAccountLink,
            sa.and_(
                finance_models.BankAccount.id == models.VenueBankAccountLink.bankAccountId,
                models.Venue.id == models.VenueBankAccountLink.venueId,
                models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .options(
            sa_orm.contains_eager(models.Offerer.bankAccounts).contains_eager(finance_models.BankAccount.venueLinks)
        )
        .options(
            sa_orm.contains_eager(models.Offerer.managedVenues)
            .load_only(models.Venue.id, models.Venue.siret, models.Venue.publicName, models.Venue.name)
            .contains_eager(models.Venue.bankAccountLinks)
        )
        .options(
            sa_orm.contains_eager(models.Offerer.managedVenues)
            .contains_eager(models.Venue.pricing_point_links)
            .load_only(models.VenuePricingPointLink.id)
        )
        .options(sa_orm.load_only(models.Offerer.id, models.Offerer.name))
        .order_by(finance_models.BankAccount.dateCreated.desc())
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
            == None,  # Because as we LEFT OUTER JOIN on VenueBankAccountLink, timespan column can be NULL
            # i.e. only Venue without any VenueBankAccountLink or only deprecated ones.
            sa.or_(
                offers_models.Stock.query.join(
                    offers_models.Offer,
                    sa.and_(
                        offers_models.Stock.offerId == offers_models.Offer.id,
                        offers_models.Offer.venueId == models.Venue.id,
                        offers_models.Stock.price > 0,
                        offers_models.Stock.isSoftDeleted.is_(False),
                        offers_models.Offer.isActive.is_(True),
                    ),
                ).exists(),
                educational_models.CollectiveStock.query.join(
                    educational_models.CollectiveOffer,
                    sa.and_(
                        educational_models.CollectiveStock.collectiveOfferId == educational_models.CollectiveOffer.id,
                        educational_models.CollectiveOffer.venueId == models.Venue.id,
                        educational_models.CollectiveStock.price > 0,
                        educational_models.CollectiveOffer.isActive.is_(True),
                    ),
                ).exists(),
            ),
        )
        .join(models.Offerer)
        .outerjoin(
            models.VenueBankAccountLink,
            sa.and_(
                models.VenueBankAccountLink.venueId == models.Venue.id,
                models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        )
        .with_entities(models.Venue.id)
    )
    return [venue.id for venue in venue_with_non_free_offers]


def get_offerers_venues_with_pricing_point(
    venue: models.Venue,
    include_without_pricing_points: bool = False,
    only_similar_pricing_points: bool = False,
    filter_same_bank_account: bool = False,
) -> list[models.Venue]:
    """
    Returns the venues of an offerer - excluding provided venue - and their associated active pricing points.
    By default, returns only the venues with pricing points.
    `include_without_pricing_points` includes venues without active pricing points.
    `only_similar_pricing_points` includes only venues with the same pricing points as the provided venue.
    `filter_same_bank_account` exclude venues with a different bank account.
    """
    venues_choices_query = (
        models.Venue.query.join(
            models.VenuePricingPointLink,
            sa.and_(
                models.VenuePricingPointLink.venueId == models.Venue.id,
                models.VenuePricingPointLink.timespan.contains(datetime.datetime.utcnow()),
            ),
            isouter=include_without_pricing_points,
        )
        .filter(
            models.Venue.managingOffererId == venue.managingOffererId,
            models.Venue.id != venue.id,
        )
        .options(
            sa_orm.load_only(
                models.Venue.id,
                models.Venue.name,
                models.Venue.publicName,
                models.Venue.siret,
            ),
            sa_orm.contains_eager(models.Venue.pricing_point_links).load_only(
                models.VenuePricingPointLink.pricingPointId, models.VenuePricingPointLink.timespan
            ),
        )
        .order_by(models.Venue.common_name)
    )
    if only_similar_pricing_points and venue.current_pricing_point_link:
        venues_choices_query = venues_choices_query.filter(
            models.VenuePricingPointLink.pricingPointId == venue.current_pricing_point_link.pricingPointId
        )

    if filter_same_bank_account:
        venues_choices_query = venues_choices_query.outerjoin(
            models.VenueBankAccountLink,
            sa.and_(
                models.VenueBankAccountLink.venueId == models.Venue.id,
                models.VenueBankAccountLink.timespan.contains(datetime.datetime.utcnow()),
            ),
        ).options(
            sa_orm.contains_eager(models.Venue.bankAccountLinks).load_only(
                models.VenueBankAccountLink.bankAccountId, models.VenueBankAccountLink.timespan
            )
        )
        if venue.current_bank_account_link:
            venues_choices_query = venues_choices_query.filter(
                models.VenueBankAccountLink.bankAccountId == venue.current_bank_account_link.bankAccountId
            )
    venues_choices = venues_choices_query.all()
    return venues_choices


def get_number_of_bookable_offers_for_offerer(offerer_id: int) -> int:
    return (
        offers_models.Offer.query.with_entities(offers_models.Offer.id)
        .join(models.Venue)
        .filter(
            models.Venue.managingOffererId == offerer_id,
            offers_models.Offer.is_offer_released_with_bookable_stock,
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
            offers_models.Offer.validation == offer_mixin.OfferValidationStatus.PENDING,
        )
        .limit(MAX_OFFERS_PER_OFFERER_FOR_COUNT)
        .count()
    )


def get_number_of_bookable_collective_offers_for_offerer(offerer_id: int) -> int:
    return (
        educational_models.CollectiveOffer.query.join(models.Venue)
        .filter(
            models.Venue.managingOffererId == offerer_id,
            educational_models.CollectiveOffer.isActive,
            educational_models.CollectiveOffer.status == offer_mixin.CollectiveOfferStatus.ACTIVE,
        )
        .with_entities(educational_models.CollectiveOffer.id)
        .union_all(
            educational_models.CollectiveOfferTemplate.query.join(models.Venue)
            .filter(
                models.Venue.managingOffererId == offerer_id,
                educational_models.CollectiveOfferTemplate.isActive,
                educational_models.CollectiveOfferTemplate.status == offer_mixin.CollectiveOfferStatus.ACTIVE,
            )
            .with_entities(educational_models.CollectiveOfferTemplate.id)
        )
        .limit(MAX_OFFERS_PER_OFFERER_FOR_COUNT)
        .count()
    )


def get_number_of_pending_collective_offers_for_offerer(offerer_id: int) -> int:
    return (
        educational_models.CollectiveOffer.query.join(models.Venue)
        .filter(
            models.Venue.managingOffererId == offerer_id,
            educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
        )
        .with_entities(educational_models.CollectiveOffer.id)
        .union_all(
            educational_models.CollectiveOfferTemplate.query.join(models.Venue)
            .filter(
                models.Venue.managingOffererId == offerer_id,
                educational_models.CollectiveOfferTemplate.validation == offer_mixin.OfferValidationStatus.PENDING,
            )
            .with_entities(educational_models.CollectiveOfferTemplate.id)
        )
        .limit(MAX_OFFERS_PER_OFFERER_FOR_COUNT)
        .count()
    )


def get_revenues_per_year(
    **query_params: int,
) -> dict[str, dict[str, float]]:
    individual_totals_query = sa.select(sa.func.jsonb_object_agg(sa.text("year"), sa.text("sum_amount"))).select_from(
        sa.select(
            sa.func.coalesce(
                sa.extract("year", bookings_models.Booking.dateUsed),
                0,
            ).label("year"),
            sa.func.sum(bookings_models.Booking.total_amount).label("sum_amount"),
        )
        .filter(
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED.value,
        )
        .filter_by(**query_params)
        .group_by("year")
        .subquery()
    )
    individual_totals: dict[str, float] = db.session.execute(individual_totals_query).scalar() or {}

    collective_booking_queries = []
    for field_name, value in query_params.items():
        collective_booking_queries.append(getattr(educational_models.CollectiveBooking, field_name) == value)

    collective_totals_query = sa.select(sa.func.jsonb_object_agg(sa.text("year"), sa.text("sum_amount"))).select_from(
        sa.select(
            sa.func.coalesce(
                sa.extract("year", educational_models.CollectiveBooking.dateUsed),
                0,
            ).label("year"),
            sa.func.sum(educational_models.CollectiveStock.price).label("sum_amount"),
        )
        .select_from(
            educational_models.CollectiveBooking,
        )
        .join(
            educational_models.CollectiveStock,
            onclause=educational_models.CollectiveStock.id == educational_models.CollectiveBooking.collectiveStockId,
        )
        .filter(
            educational_models.CollectiveBooking.status != bookings_models.BookingStatus.CANCELLED.value,
            *collective_booking_queries,
        )
        .group_by("year")
        .subquery()
    )
    collective_totals: dict[str, float] = db.session.execute(collective_totals_query).scalar() or {}

    years = set(individual_totals) | set(collective_totals)

    return {
        ("En cours" if year == "0" else year): {
            "individual": individual_totals.get(year, 0.0),
            "collective": collective_totals.get(year, 0.0),
        }
        for year in years
    }


def get_offerer_addresses(offerer_id: int, only_with_offers: bool = False) -> BaseQuery:
    query = (
        models.OffererAddress.query.filter(models.OffererAddress.offererId == offerer_id)
        .join(geography_models.Address, models.OffererAddress.addressId == geography_models.Address.id)
        .outerjoin(models.Venue, models.Venue.offererAddressId == models.OffererAddress.id)
    )
    if only_with_offers:
        subquery = db.session.query(
            sa.select(offers_models.Offer.id, offers_models.Offer.offererAddressId)
            .select_from(offers_models.Offer)
            .subquery()
        )
        query = query.where(subquery.filter(offers_models.Offer.offererAddressId == models.OffererAddress.id).exists())

    query = query.with_entities(
        models.OffererAddress.id,
        geography_models.Address.id.label("addressId"),
        models.OffererAddress.label,
        models.Venue.common_name,
        models.Venue.id.label("venueId"),
        geography_models.Address.street,
        geography_models.Address.postalCode,
        geography_models.Address.city,
        geography_models.Address.departmentCode,
    )
    query = query.order_by(models.OffererAddress.label)
    return query


def get_offerer_address_of_offerer(offerer_id: int, offerer_address_id: int) -> models.OffererAddress:
    return (
        models.OffererAddress.query.where(
            models.OffererAddress.offererId == offerer_id, models.OffererAddress.id == offerer_address_id
        )
        .options(
            sa_orm.with_expression(models.OffererAddress._isLinkedToVenue, models.OffererAddress.isLinkedToVenue.expression)  # type: ignore[attr-defined]
        )
        .one_or_none()
    )


def get_offerer_headline_offer(offerer_id: int) -> offers_models.Offer | None:
    try:
        offer = (
            offers_models.Offer.query.join(models.Venue, offers_models.Offer.venueId == models.Venue.id)
            .join(models.Offerer, models.Venue.managingOffererId == models.Offerer.id)
            .join(offers_models.HeadlineOffer, offers_models.HeadlineOffer.offerId == offers_models.Offer.id)
            .options(
                sa_orm.contains_eager(offers_models.Offer.headlineOffers),
                sa_orm.joinedload(offers_models.Offer.mediations),
                sa_orm.joinedload(offers_models.Offer.product).joinedload(offers_models.Product.productMediations),
            )
            .filter(models.Offerer.id == offerer_id, offers_models.HeadlineOffer.isActive == True)
            .one_or_none()
        )

    except sa_orm.exc.MultipleResultsFound:
        raise exceptions.TooManyHeadlineOffersForOfferer
    return offer
