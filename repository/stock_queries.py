from typing import List

from models import StockSQLEntity, Offerer, UserSQLEntity, OfferSQLEntity, ThingType, VenueSQLEntity, Product
from utils.human_ids import dehumanize


def find_stock_by_id(id: int) -> StockSQLEntity:
    return StockSQLEntity.query.get(id)


def find_stocks_with_possible_filters(filters, user):
    query = StockSQLEntity.queryNotSoftDeleted()
    if 'offererId' in filters:
        query = query.filter(StockSQLEntity.offererId == dehumanize(filters['offererId']))
        _check_offerer_user(query.first_or_404().offerer.query, user)
    if 'hasPrice' in filters and filters['hasPrice'].lower() == 'true':
        query = query.filter(StockSQLEntity.price != None)
    return query


def find_online_activation_stock():
    return StockSQLEntity.query \
        .join(OfferSQLEntity) \
        .join(VenueSQLEntity) \
        .filter_by(isVirtual=True) \
        .join(Product, OfferSQLEntity.productId == Product.id) \
        .filter_by(type=str(ThingType.ACTIVATION)) \
        .first()


def _check_offerer_user(query, user):
    return query.filter(
        Offerer.users.any(UserSQLEntity.id == user.id)
    ).first_or_404()


def get_stocks_for_offers(offer_ids: List[int]) -> List[StockSQLEntity]:
    return StockSQLEntity.query \
        .filter(StockSQLEntity.offerId.in_(offer_ids)) \
        .all()
