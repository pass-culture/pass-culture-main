from typing import Iterable
from typing import Optional

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
from sqlalchemy import orm

from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.users.models import User
from pcapi.domain import ts_vector
from pcapi.models import bank_information
from pcapi.models import db
from pcapi.models import offer_mixin


def get_all_venue_labels() -> list[offerers_models.VenueLabel]:
    return offerers_models.VenueLabel.query.all()


def get_all_offerers_for_user(
    user: User,
    validated: bool = None,
    keywords: str = None,
    include_non_validated_user_offerers: bool = False,
) -> orm.Query:
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
    query = offerers_models.Offerer.query.filter(offerers_models.Offerer.isActive.is_(True))

    if not user.has_admin_role:
        user_offerer_filters = [offerers_models.UserOfferer.userId == user.id]
        if not include_non_validated_user_offerers:
            user_offerer_filters.append(offerers_models.UserOfferer.isValidated)
        query = query.join(offerers_models.Offerer.UserOfferers).filter(*user_offerer_filters)

    if validated is not None:
        if validated:
            query = query.filter(offerers_models.Offerer.isValidated)
        else:
            query = query.filter(
                ~offerers_models.Offerer.isValidated  # type: ignore [operator]  # pylint: disable=invalid-unary-operand-type
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

    offer_query = offers_models.Offer.query.filter(
        offers_models.Offer.validation != offer_mixin.OfferValidationStatus.DRAFT,
        offers_models.Offer.venueId.in_(venue_ids),
    )

    offer_query = offer_query.filter(offers_models.Offer.isEducational.is_(False))

    individual_offers_count = dict(
        offer_query.with_entities(offers_models.Offer.venueId, sa.func.count())
        .group_by(offers_models.Offer.venueId)
        .all()
    )

    collective_offers_count = {}
    collective_offers_template_count = {}

    collective_offers_count = dict(
        educational_models.CollectiveOffer.query.filter(
            educational_models.CollectiveOffer.validation != offer_mixin.OfferValidationStatus.DRAFT,
            educational_models.CollectiveOffer.venueId.in_(venue_ids),
        )
        .with_entities(educational_models.CollectiveOffer.venueId, sa.func.count())
        .group_by(educational_models.CollectiveOffer.venueId)
        .all()
    )

    collective_offers_template_count = dict(
        educational_models.CollectiveOfferTemplate.query.filter(
            educational_models.CollectiveOfferTemplate.validation != offer_mixin.OfferValidationStatus.DRAFT,
            educational_models.CollectiveOfferTemplate.venueId.in_(venue_ids),
        )
        .with_entities(educational_models.CollectiveOfferTemplate.venueId, sa.func.count())
        .group_by(educational_models.CollectiveOfferTemplate.venueId)
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
    active_offerers_only: Optional[bool] = False,
    offerer_id: Optional[int] = None,
    validated_offerer: Optional[bool] = None,
) -> list[offerers_models.Venue]:
    query = (
        offerers_models.Venue.query.join(
            offerers_models.Offerer, offerers_models.Offerer.id == offerers_models.Venue.managingOffererId
        )
        .join(offerers_models.UserOfferer, offerers_models.UserOfferer.offererId == offerers_models.Offerer.id)
        .options(orm.joinedload(offerers_models.Venue.managingOfferer))
        .options(orm.joinedload(offerers_models.Venue.businessUnit))
    )
    if not user_is_admin:
        query = query.filter(
            offerers_models.UserOfferer.userId == pro_user_id,
            offerers_models.UserOfferer.isValidated,
        )

    if validated_offerer is not None:
        if validated_offerer:
            query = query.filter(offerers_models.Offerer.isValidated)
        else:
            query = query.filter(
                ~offerers_models.Offerer.isValidated  # type: ignore [operator]  # pylint: disable=invalid-unary-operand-type
            )

    if active_offerers_only:
        query = query.filter(offerers_models.Offerer.isActive.is_(True))

    if offerer_id:
        query = query.filter(offerers_models.Venue.managingOffererId == offerer_id)

    return query.order_by(offerers_models.Venue.name).all()


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
        for prefix, value in offerers_models.ApiKey.query.filter_by(offererId=offerer_id)
        .with_entities(offerers_models.ApiKey.prefix, offerers_models.ApiKey.value)
        .all()
        if prefix or value
    ]


def find_offerer_by_siren(siren: str) -> Optional[offerers_models.Offerer]:
    return offerers_models.Offerer.query.filter_by(siren=siren).one_or_none()


def find_offerer_by_validation_token(token: str) -> Optional[offerers_models.UserOfferer]:
    return offerers_models.Offerer.query.filter_by(validationToken=token).one_or_none()


def find_user_offerer_by_validation_token(token: str) -> Optional[offerers_models.UserOfferer]:
    return offerers_models.UserOfferer.query.filter_by(validationToken=token).one_or_none()


def find_all_user_offerers_by_offerer_id(offerer_id: int) -> list[offerers_models.UserOfferer]:
    return offerers_models.UserOfferer.query.filter_by(offererId=offerer_id).all()


def filter_query_where_user_is_user_offerer_and_is_validated(query, user):  # type: ignore [no-untyped-def]
    return query.join(offerers_models.UserOfferer).filter_by(user=user).filter(offerers_models.UserOfferer.isValidated)


def find_venue_by_id(venue_id: int) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()


def find_venue_by_siret(siret: str) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(siret=siret).one_or_none()


def find_venue_by_managing_offerer_id(offerer_id: int) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).first()


def find_virtual_venue_by_offerer_id(offerer_id: int) -> Optional[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(managingOffererId=offerer_id, isVirtual=True).first()


def find_active_venues_by_booking_email(email: str) -> list[offerers_models.Venue]:
    return (
        offerers_models.Venue.query.filter_by(bookingEmail=email)
        .join(offerers_models.Offerer)
        .filter(offerers_models.Offerer.isActive == True)
        .all()
    )


def has_physical_venue_without_draft_or_accepted_bank_information(offerer_id: int) -> bool:
    return db.session.query(
        offerers_models.Venue.query.outerjoin(bank_information.BankInformation)
        .filter(offerers_models.Venue.managingOffererId == offerer_id)
        .filter(offerers_models.Venue.isVirtual.is_(False))
        .filter(
            sa.or_(
                bank_information.BankInformation.status.notin_(
                    (bank_information.BankInformationStatus.DRAFT, bank_information.BankInformationStatus.ACCEPTED)
                ),
                offerers_models.Venue.bankInformation == None,
            )
        )
        .exists()
    ).scalar()


def has_digital_venue_with_at_least_one_offer(offerer_id: int) -> bool:
    return db.session.query(
        offerers_models.Venue.query.join(offers_models.Offer, offerers_models.Venue.id == offers_models.Offer.venueId)
        .filter(offerers_models.Venue.managingOffererId == offerer_id)
        .filter(offerers_models.Venue.isVirtual.is_(True))
        .exists()
    ).scalar()


get_filter_matching_ts_query_for_offerer = ts_vector.create_get_filter_matching_ts_query_in_any_model(
    offerers_models.Offerer, offerers_models.Venue
)


def get_by_offer_id(offer_id: int) -> offerers_models.Offerer:
    offerer = (
        offerers_models.Offerer.query.join(offerers_models.Venue)
        .join(offers_models.Offer)
        .filter_by(id=offer_id)
        .one_or_none()
    )
    if not offerer:
        raise offerers_exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_offer_id(collective_offer_id: int) -> offerers_models.Offerer:
    offerer = (
        offerers_models.Offerer.query.join(offerers_models.Venue)
        .join(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.id == collective_offer_id)
        .one_or_none()
    )
    if not offerer:
        raise offerers_exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_offer_template_id(collective_offer_id: int) -> offerers_models.Offerer:
    offerer = (
        offerers_models.Offerer.query.join(offerers_models.Venue)
        .join(educational_models.CollectiveOfferTemplate)
        .filter(educational_models.CollectiveOfferTemplate.id == collective_offer_id)
        .one_or_none()
    )
    if not offerer:
        raise offerers_exceptions.CannotFindOffererForOfferId()
    return offerer


def get_by_collective_stock_id(collective_stock_id: int) -> offerers_models.Offerer:
    offerer = (
        offerers_models.Offerer.query.join(offerers_models.Venue)
        .join(educational_models.CollectiveOffer)
        .join(educational_models.CollectiveStock)
        .filter(educational_models.CollectiveStock.id == collective_stock_id)
        .one_or_none()
    )
    if not offerer:
        raise offerers_exceptions.CannotFindOffererForOfferId()
    return offerer


def find_new_offerer_user_email(offerer_id: int) -> str:
    result_tuple = (
        offerers_models.UserOfferer.query.filter_by(offererId=offerer_id).join(User).with_entities(User.email).first()
    )
    if result_tuple:
        return result_tuple[0]
    raise offerers_exceptions.CannotFindOffererUserEmail()


def filter_offerers_with_keywords_string(query: BaseQuery, keywords_string: str) -> BaseQuery:
    keywords_filter = ts_vector.create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_for_offerer, keywords_string
    )
    subquery = (
        offerers_models.Offerer.query.outerjoin(offerers_models.Offerer.managedVenues)
        .filter(keywords_filter)
        .with_entities(offerers_models.Offerer.id)
        .subquery()
    )
    query = query.filter(offerers_models.Offerer.id.in_(subquery))
    return query


def check_if_siren_already_exists(siren: str) -> bool:
    return db.session.query(
        db.session.query(offerers_models.Offerer.id).filter(offerers_models.Offerer.siren == siren).exists()
    )


def find_siren_by_offerer_id(offerer_id: int) -> str:
    siren = offerers_models.Offerer.query.filter_by(id=offerer_id).with_entities(offerers_models.Offerer.siren).scalar()

    if siren:
        return siren

    raise offerers_exceptions.CannotFindOffererSiren


def venues_have_offers(*venues: offerers_models.Venue) -> bool:
    """At least one venue which has email as bookingEmail has at least one active offer"""
    return db.session.query(
        offers_models.Offer.query.filter(
            offers_models.Offer.venueId.in_([venue.id for venue in venues]),
            offers_models.Offer.status == offer_mixin.OfferStatus.ACTIVE.name,
        ).exists()
    ).scalar()


def find_venues_by_managing_offerer_id(offerer_id: int) -> list[offerers_models.Venue]:
    return offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).all()


def find_venues_by_offerers(*offerers: offerers_models.Offerer) -> list[offerers_models.Venue]:
    """Get all venues managed by any offerer given in arguments"""
    return offerers_models.Venue.query.filter(
        offerers_models.Venue.managingOffererId.in_([offerer.id for offerer in offerers])
    ).all()


def offerer_has_venue_with_adage_id(offerer_id: int) -> bool:
    query = db.session.query(offerers_models.Venue.id)
    query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
    query = query.filter(
        offerers_models.Venue.adageId != None,
        offerers_models.Offerer.id == offerer_id,
    )
    return bool(query.count())


def dms_token_exists(dms_token: str) -> bool:
    return db.session.query(offerers_models.Venue.query.filter_by(dmsToken=dms_token).exists()).scalar()
