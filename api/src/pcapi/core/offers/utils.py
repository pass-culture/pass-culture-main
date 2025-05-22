import dataclasses
from decimal import Decimal

import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.models import Offer
from pcapi.models.feature import FeatureToggle


def offer_app_link(offer: CollectiveOffer | Offer) -> str:
    # This link opens the mobile app if installed, the browser app otherwise
    return f"{settings.WEBAPP_V2_URL}/offre/{offer.id}"


def offer_app_redirect_link(offer: Offer) -> str:
    if FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION.is_active():
        return f"{settings.WEBAPP_V2_REDIRECT_URL}/offre/{offer.id}"
    return offer_app_link(offer)


@dataclasses.dataclass
class CalculatedOfferAddress:
    city: str | None
    departmentCode: str | None
    label: str
    latitude: Decimal | None
    longitude: Decimal | None
    postalCode: str | None
    street: str | None


def get_offer_address(offer: Offer) -> CalculatedOfferAddress:
    offerer_address = offer.offererAddress or offer.venue.offererAddress
    if offerer_address:
        return CalculatedOfferAddress(
            city=offerer_address.address.city,
            departmentCode=offerer_address.address.departmentCode,
            label=offerer_address.label or offer.venue.name,
            latitude=offerer_address.address.latitude,
            longitude=offerer_address.address.longitude,
            postalCode=offerer_address.address.postalCode,
            street=offerer_address.address.street,
        )
    return CalculatedOfferAddress(
        city=None,
        departmentCode=None,
        label=offer.venue.name,
        latitude=None,
        longitude=None,
        postalCode=None,
        street=None,
    )


def retrieve_offer_relations_query(query: sa_orm.Query) -> sa_orm.Query:
    return (
        query.options(sa_orm.selectinload(offers_models.Offer.stocks))
        .options(sa_orm.selectinload(offers_models.Offer.mediations))
        .options(
            sa_orm.joinedload(offers_models.Offer.product)
            .load_only(
                offers_models.Product.id,
                offers_models.Product.thumbCount,
                offers_models.Product.description,
                offers_models.Product.durationMinutes,
                offers_models.Product.extraData,
            )
            .selectinload(offers_models.Product.productMediations)
        )
        .options(
            sa_orm.selectinload(offers_models.Offer.priceCategories).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            )
        )
        .options(sa_orm.joinedload(offers_models.Offer.futureOffer))
    )


def get_filtered_offers_linked_to_provider(
    query_filters: serialization.GetOffersQueryParams,
    is_event: bool,
) -> sa_orm.Query:
    offers_query = (
        db.session.query(offers_models.Offer)
        .outerjoin(offers_models.Offer.futureOffer)
        .join(offerers_models.Venue)
        .join(providers_models.VenueProvider)
        .filter(providers_models.VenueProvider.provider == current_api_key.provider)
        .filter(offers_models.Offer.isEvent == is_event)
        .filter(offers_models.Offer.id >= query_filters.firstIndex)
        .order_by(offers_models.Offer.id)
        .options(sa_orm.contains_eager(offers_models.Offer.futureOffer))
        .options(
            sa_orm.joinedload(offers_models.Offer.venue).load_only(
                offerers_models.Venue.id, offerers_models.Venue.offererAddressId
            )
        )
    )

    if query_filters.venue_id:
        offers_query = offers_query.filter(offers_models.Offer.venueId == query_filters.venue_id)

    if query_filters.ids_at_provider:
        offers_query = offers_query.filter(offers_models.Offer.idAtProvider.in_(query_filters.ids_at_provider))

    if query_filters.address_id:
        offers_query = offers_query.join(
            offerers_models.OffererAddress,
            offerers_models.OffererAddress.id == offers_models.Offer.offererAddressId,
        ).filter(offerers_models.OffererAddress.addressId == query_filters.address_id)

    offers_query = retrieve_offer_relations_query(offers_query).limit(query_filters.limit)

    return offers_query
