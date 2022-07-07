import typing

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.domain.pro_offers.offers_recap import OfferRecap
from pcapi.domain.pro_offers.offers_recap import OffersRecap


def to_domain(offers: list[Offer]) -> OffersRecap:
    offers_recap = [_offer_recap_to_domain(offer) for offer in offers]

    return OffersRecap(offers_recap=offers_recap)


def _offer_recap_to_domain(offer: Offer) -> OfferRecap:
    stocks = [_stock_serializer(stock_entity) for stock_entity in offer.activeStocks]

    return OfferRecap(
        id=offer.id,  # type: ignore [arg-type]
        has_booking_limit_datetimes_passed=offer.hasBookingLimitDatetimesPassed,  # type: ignore [arg-type]
        is_active=offer.isActive,  # type: ignore [arg-type]
        is_editable=offer.isEditable,
        is_event=typing.cast(bool, offer.isEvent),
        is_thing=offer.isThing,
        is_educational=offer.isEducational,  # type: ignore [arg-type]
        product_isbn=offer.extraData.get("isbn") if offer.extraData else None,
        name=offer.name,  # type: ignore [arg-type]
        thumb_url=offer.thumbUrl,
        subcategory_id=offer.subcategoryId,
        venue_id=offer.venue.id,
        venue_is_virtual=offer.venue.isVirtual,
        venue_managing_offerer_id=offer.venue.managingOffererId,
        venue_name=offer.venue.name,
        venue_offerer_name=offer.venue.managingOfferer.name,
        venue_public_name=offer.venue.publicName,
        venue_departement_code=offer.venue.departementCode,
        stocks=stocks,
        status=offer.status.name,  # type: ignore [attr-defined]
        is_showcase=offer.extraData.get("isShowcase") if offer.extraData else None,
    )


def _stock_serializer(stock: Stock) -> dict:
    return {
        "id": stock.id,
        "has_booking_limit_datetime_passed": stock.hasBookingLimitDatetimePassed,
        "remaining_quantity": stock.remainingQuantity,
        "beginning_datetime": stock.beginningDatetime,
    }
