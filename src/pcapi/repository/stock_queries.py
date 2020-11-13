from typing import List

from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import StockSQLEntity
from pcapi.models import ThingType
from pcapi.models import VenueSQLEntity


def find_stock_by_id(id: int) -> StockSQLEntity:
    return StockSQLEntity.query.get(id)


def find_online_activation_stock():
    return (
        StockSQLEntity.query.join(Offer)
        .join(VenueSQLEntity)
        .filter_by(isVirtual=True)
        .join(Product, Offer.productId == Product.id)
        .filter_by(type=str(ThingType.ACTIVATION))
        .first()
    )


def get_stocks_for_offers(offer_ids: List[int]) -> List[StockSQLEntity]:
    return StockSQLEntity.query.filter(StockSQLEntity.offerId.in_(offer_ids)).all()
