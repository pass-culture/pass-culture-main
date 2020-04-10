from datetime import datetime
from typing import List, Callable

from sqlalchemy import func

from models import Offer, Stock
from models.db import db
from repository import repository


def get_offers_with_max_stock_date_between_today_and_end_of_quarantine(first_day_after_quarantine: datetime,
                                                                       today: datetime) -> List[Offer]:
    stock_with_latest_date_by_offer = db.session.query(
        Stock.offerId,
        func.max(Stock.beginningDatetime).label('beginningDatetime')
    ) \
        .group_by(Stock.offerId).subquery()

    return Offer.query.join(
        stock_with_latest_date_by_offer,
        Offer.id == stock_with_latest_date_by_offer.c.offerId
    ) \
        .filter(stock_with_latest_date_by_offer.c.beginningDatetime < first_day_after_quarantine) \
        .filter(stock_with_latest_date_by_offer.c.beginningDatetime > today) \
        .all()


def deactivate_offers(offers: List[Offer]):
    for offer in offers:
        offer.isActive = False
    repository.save(*offers)


def deactivate_offers_with_max_stock_date_between_today_and_end_of_quarantine(first_day_after_quarantine: datetime,
                                                                              today: datetime,
                                                                              get_offers: Callable = get_offers_with_max_stock_date_between_today_and_end_of_quarantine):
    offers = get_offers(first_day_after_quarantine, today)
    deactivate_offers(offers)
