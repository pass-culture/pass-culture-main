from datetime import date
from datetime import timedelta
from typing import Iterable

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import pcapi.core.bookings.repository as bookings_repository
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.finance.models import BankInformation
from pcapi.core.finance.models import BankInformationStatus
from pcapi.core.offers.models import Offer
import pcapi.core.offers.repository as offers_repository
from pcapi.core.users.models import User
from pcapi.domain.ts_vector import create_filter_matching_all_keywords_in_any_model
from pcapi.domain.ts_vector import create_get_filter_matching_ts_query_in_any_model
from pcapi.models import db
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus

from . import exceptions
from . import models


def get_all_venue_labels() -> list[models.VenueLabel]:
    return models.VenueLabel.query.all()


def get_all_offerers_for_user(
    user: User,
    validated: bool = None,
    keywords: str = None,
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
        user_offerer_filters = [models.UserOfferer.userId == user.id]
        if not include_non_validated_user_offerers:
            user_offerer_filters.append(models.UserOfferer.isValidated)
        query = query.join(models.Offerer.UserOfferers).filter(*user_offerer_filters)

    if validated is not None:
        if validated:
            query = query.filter(models.Offerer.isValidated)
        else:
            query = query.filter(
                ~models.Offerer.isValidated  # type: ignore [operator]  # pylint: disable=invalid-unary-operand-type
            )

    if keywords:
        query = filter_offerers_with_keywords_string(query, keywords)

    return query


def get_offer_counts_by_venue(venue_ids: Iterable[int]) -> dict[int, int]:
    """Return a dictionary with the number of non-draft offers for each
    requested venue.

    Venues that do not have any offers are not included in the
    returned dictionary.
    """
    individual_offers_count_subquery = (
        Offer.query.filter(
            Offer.validation != OfferValidationStatus.DRAFT,
            Offer.venueId.in_(venue_ids),
        )
        .with_entities(Offer.id)
        .limit(100)
    )

    individual_offers_count = dict(
        Offer.query.filter(Offer.id.in_(individual_offers_count_subquery))
        .with_entities(Offer.venueId, sqla.func.count())
        .group_by(Offer.venueId)
        .all()
    )

    collective_offers_count = {}
    collective_offers_template_count = {}

    collective_offers_count_subquery = (
        CollectiveOffer.query.filter(
            CollectiveOffer.validation != OfferValidationStatus.DRAFT,
            CollectiveOffer.venueId.in_(venue_ids),
        )
        .with_entities(CollectiveOffer.id)
        .limit(100)
    )

    collective_offers_count = dict(
        CollectiveOffer.query.filter(CollectiveOffer.id.in_(collective_offers_count_subquery))
        .with_entities(CollectiveOffer.venueId, sqla.func.count())
        .group_by(CollectiveOffer.venueId)
        .all()
    )

    collective_offers_template_count_subquery = (
        CollectiveOfferTemplate.query.filter(
            CollectiveOfferTemplate.validation != OfferValidationStatus.DRAFT,
            CollectiveOfferTemplate.venueId.in_(venue_ids),
        )
        .with_entities(CollectiveOfferTemplate.id)
        .limit(100)
    )

    collective_offers_template_count = dict(
        CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.id.in_(collective_offers_template_count_subquery))
        .with_entities(CollectiveOfferTemplate.venueId, sqla.func.count())
        .group_by(CollectiveOfferTemplate.venueId)
        .all()
    )

    offers_count_by_venue_id = {}
    for venue_id in venue_ids:
        n_individual_offers = individual_offers_count.get(venue_id, 0)
        n_collective_offers = collective_offers_count.get(venue_id, 0)
        n_collective_offers_template = collective_offers_template_count.get(venue_id, 0)
        offers_count_by_venue_id[venue_id] = n_individual_offers + n_collective_offers + n_collective_offers_template

    return offers_count_by_venue_id


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
        .options(sqla_orm.joinedload(models.Venue.businessUnit))
        .options(sqla_orm.joinedload(models.Venue.collectiveDomains))
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
            query = query.filter(~models.Offerer.isValidated)  # type: ignore [operator] # pylint: disable=invalid-unary-operand-type

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
        prefix or value[:8]
        for prefix, value in models.ApiKey.query.filter_by(offererId=offerer_id)
        .with_entities(models.ApiKey.prefix, models.ApiKey.value)
        .all()
        if prefix or value
    ]


def find_offerer_by_siren(siren: str) -> models.Offerer | None:
    return models.Offerer.query.filter_by(siren=siren).one_or_none()


def find_offerer_by_id(offererId: int) -> models.Offerer | None:
    return models.Offerer.query.filter_by(id=offererId).one_or_none()


def find_offerer_by_validation_token(token: str) -> models.UserOfferer | None:
    return models.Offerer.query.filter_by(validationToken=token).one_or_none()


def find_user_offerer_by_validation_token(token: str) -> models.UserOfferer | None:
    return models.UserOfferer.query.filter_by(validationToken=token).one_or_none()


def find_all_user_offerers_by_offerer_id(offerer_id: int) -> list[models.UserOfferer]:
    return models.UserOfferer.query.filter_by(offererId=offerer_id).all()


def filter_query_where_user_is_user_offerer_and_is_validated(query, user):  # type: ignore [no-untyped-def]
    return query.join(models.UserOfferer).filter_by(user=user).filter(models.UserOfferer.isValidated)


def find_venue_by_id(venue_id: int) -> models.Venue | None:
    return models.Venue.query.filter_by(id=venue_id).one_or_none()


def find_venue_by_siret(siret: str) -> models.Venue | None:
    return models.Venue.query.filter_by(siret=siret).one_or_none()


def get_all_venues_by_offerer_id(offerer_id: int) -> list[models.Venue]:
    return models.Venue.query.filter_by(managingOffererId=offerer_id).all()


def find_venue_by_managing_offerer_id(offerer_id: int) -> models.Venue | None:
    return models.Venue.query.filter_by(managingOffererId=offerer_id).first()


def find_virtual_venue_by_offerer_id(offerer_id: int) -> models.Venue | None:
    return models.Venue.query.filter_by(managingOffererId=offerer_id, isVirtual=True).first()


def find_active_venues_by_booking_email(email: str) -> list[models.Venue]:
    return (
        models.Venue.query.filter_by(bookingEmail=email)
        .join(models.Offerer)
        .filter(models.Offerer.isActive == True)
        .all()
    )


def has_physical_venue_without_draft_or_accepted_bank_information(offerer_id: int) -> bool:
    return db.session.query(
        models.Venue.query.outerjoin(BankInformation)
        .filter(models.Venue.managingOffererId == offerer_id)
        .filter(models.Venue.isVirtual.is_(False))
        .filter(
            sqla.or_(
                BankInformation.status.notin_((BankInformationStatus.DRAFT, BankInformationStatus.ACCEPTED)),
                models.Venue.bankInformation == None,
            )
        )
        .exists()
    ).scalar()


def has_digital_venue_with_at_least_one_offer(offerer_id: int) -> bool:
    return db.session.query(
        models.Venue.query.join(Offer, models.Venue.id == Offer.venueId)
        .filter(models.Venue.managingOffererId == offerer_id)
        .filter(models.Venue.isVirtual.is_(True))
        .filter(Offer.status != OfferValidationStatus.DRAFT.name)
        .exists()
    ).scalar()


get_filter_matching_ts_query_for_offerer = create_get_filter_matching_ts_query_in_any_model(
    models.Offerer, models.Venue
)


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
    result_tuple = models.UserOfferer.query.filter_by(offererId=offerer_id).join(User).with_entities(User.email).first()
    if result_tuple:
        return result_tuple[0]
    raise exceptions.CannotFindOffererUserEmail()


def filter_offerers_with_keywords_string(query: BaseQuery, keywords_string: str) -> BaseQuery:
    keywords_filter = create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_offerer, keywords_string
    )
    subquery = (
        models.Offerer.query.outerjoin(models.Offerer.managedVenues)
        .filter(keywords_filter)
        .with_entities(models.Offerer.id)
        .subquery()
    )
    query = query.filter(models.Offerer.id.in_(subquery))
    return query


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


def find_venues_by_managing_offerer_id(offerer_id: int) -> list[models.Venue]:
    return models.Venue.query.filter_by(managingOffererId=offerer_id).all()


def find_venues_by_offerers(*offerers: models.Offerer) -> list[models.Venue]:
    """Get all venues managed by any offerer given in arguments"""
    return models.Venue.query.filter(models.Venue.managingOffererId.in_([offerer.id for offerer in offerers])).all()


def offerer_has_venue_with_adage_id(offerer_id: int) -> bool:
    query = db.session.query(models.Venue.id)
    query = query.join(models.Offerer, models.Venue.managingOfferer)
    query = query.filter(
        models.Venue.adageId != None,
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
    ordered by `publicName` or name if `publicName` is null
    """
    return (
        models.Venue.query.join(BankInformation)
        .filter(
            BankInformation.status == BankInformationStatus.ACCEPTED,
            models.Venue.managingOffererId == offerer_id,
        )
        .options(sqla_orm.joinedload(models.Venue.bankInformation))
        .order_by(sqla.func.coalesce(models.Venue.publicName, models.Venue.name))
        .all()
    )


def get_venue_by_id(venue_id: int) -> models.Venue:
    return models.Venue.query.get(venue_id)


def find_offerers_validated_3_days_ago_with_no_venues() -> list[models.Offerer]:
    subquery_get_physical_venues = db.session.query(models.Venue.managingOffererId).where((~models.Venue.isVirtual))

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
    users_offerer = find_all_user_offerers_by_offerer_id(venue.managingOffererId)
    emails = {user_offerer.user.email for user_offerer in users_offerer}
    emails.add(venue.bookingEmail)
    return emails
