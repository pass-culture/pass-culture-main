from typing import Dict, List

from pcapi.domain.identifier.identifier import Identifier

from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap, OfferRecap
from pcapi.models import OfferSQLEntity, StockSQLEntity


def to_domain(offer_sql_entities: List[OfferSQLEntity], current_page: int, total_pages: int, total_offers: int) -> PaginatedOffersRecap:
    offers_recap = [_offer_recap_to_domain(offer_sql_entity) for offer_sql_entity in offer_sql_entities]

    return PaginatedOffersRecap(offers_recap=offers_recap,
                                current_page=current_page,
                                total_pages=total_pages,
                                total_offers=total_offers)


def _offer_recap_to_domain(offer_sql_entity: OfferSQLEntity) -> OfferRecap:
    stocks = [_stock_serializer(stock_entity) for stock_entity in offer_sql_entity.activeStocks]

    return OfferRecap(
            identifier=Identifier(offer_sql_entity.id),
            has_booking_limit_datetimes_passed=offer_sql_entity.hasBookingLimitDatetimesPassed,
            is_active=offer_sql_entity.isActive,
            is_editable=offer_sql_entity.isEditable,
            is_event=offer_sql_entity.isEvent,
            is_thing=offer_sql_entity.isThing,
            name=offer_sql_entity.name,
            thumb_url=offer_sql_entity.thumbUrl,
            offer_type=offer_sql_entity.type,
            venue_identifier=Identifier(offer_sql_entity.venue.id),
            venue_is_virtual=offer_sql_entity.venue.isVirtual,
            venue_managing_offerer_id=offer_sql_entity.venue.managingOffererId,
            venue_name=offer_sql_entity.venue.name,
            venue_public_name=offer_sql_entity.venue.publicName,
            stocks=stocks
    )


def _stock_serializer(stock: StockSQLEntity) -> Dict:
    return {
        "identifier": Identifier(stock.id),
        "remaining_quantity": stock.remainingQuantity
    }
