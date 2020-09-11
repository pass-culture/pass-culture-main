from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap, OfferRecap, Venue, Stock
from models import OfferSQLEntity, VenueSQLEntity, StockSQLEntity


def to_domain(offer_sql_entities: [OfferSQLEntity], total_offers: int) -> PaginatedOffersRecap:
    offers_recap = [_offer_recap_to_domain(offer_sql_entity) for offer_sql_entity in offer_sql_entities]

    return PaginatedOffersRecap(offers_recap, total_offers)


def _offer_recap_to_domain(offer_sql_entity: OfferSQLEntity) -> OfferRecap:
    venue = _venue_to_domain(offer_sql_entity.venue)
    stocks = [_stock_to_domain(stock_entity) for stock_entity in offer_sql_entity.activeStocks]

    return OfferRecap(
            offer_sql_entity.id,
            offer_sql_entity.availabilityMessage,
            offer_sql_entity.hasBookingLimitDatetimesPassed,
            offer_sql_entity.isActive,
            offer_sql_entity.isEditable,
            offer_sql_entity.isFullyBooked,
            offer_sql_entity.isEvent,
            offer_sql_entity.isThing,
            offer_sql_entity.name,
            stocks,
            offer_sql_entity.thumbUrl,
            offer_sql_entity.type,
            venue
    )


def _venue_to_domain(venue: VenueSQLEntity) -> Venue:
    return Venue(venue.id, venue.isVirtual, venue.name, venue.publicName)


def _stock_to_domain(stock: StockSQLEntity) -> Stock:
    return Stock(stock.id, stock.isEventExpired, stock.remainingQuantity, stock.offerId)
