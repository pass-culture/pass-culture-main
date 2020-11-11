from typing import Dict
from typing import List

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.paginated_offers_recap import OfferRecap
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.models import Offer
from pcapi.models import StockSQLEntity


def to_domain(offers: List[Offer], current_page: int, total_pages: int, total_offers: int) -> PaginatedOffersRecap:
    offers_recap = [_offer_recap_to_domain(offer) for offer in offers]

    return PaginatedOffersRecap(
        offers_recap=offers_recap, current_page=current_page, total_pages=total_pages, total_offers=total_offers
    )


def _offer_recap_to_domain(offer: Offer) -> OfferRecap:
    stocks = [_stock_serializer(stock_entity) for stock_entity in offer.activeStocks]

    return OfferRecap(
        identifier=Identifier(offer.id),
        has_booking_limit_datetimes_passed=offer.hasBookingLimitDatetimesPassed,
        is_active=offer.isActive,
        is_editable=offer.isEditable,
        is_event=offer.isEvent,
        is_thing=offer.isThing,
        name=offer.name,
        thumb_url=offer.thumbUrl,
        offer_type=offer.type,
        venue_identifier=Identifier(offer.venue.id),
        venue_is_virtual=offer.venue.isVirtual,
        venue_managing_offerer_id=offer.venue.managingOffererId,
        venue_name=offer.venue.name,
        venue_offerer_name=offer.venue.managingOfferer.name,
        venue_public_name=offer.venue.publicName,
        stocks=stocks,
    )


def _stock_serializer(stock: StockSQLEntity) -> Dict:
    return {"identifier": Identifier(stock.id), "remaining_quantity": stock.remainingQuantity}
