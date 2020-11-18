from datetime import datetime
from typing import Callable
from typing import List

from sqlalchemy import func

from pcapi.algolia.usecase.orchestrator import delete_expired_offers
from pcapi.flask_app import app
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models.db import db
from pcapi.repository import repository


def get_offers_with_max_stock_date_between_today_and_end_of_quarantine(
    first_day_after_quarantine: datetime, today: datetime
) -> List[Offer]:
    quarantine_offers_query = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(
        first_day_after_quarantine, today
    )
    return quarantine_offers_query.all()


def build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(first_day_after_quarantine, today):
    stock_with_latest_date_by_offer = (
        db.session.query(Stock.offerId, func.max(Stock.beginningDatetime).label("beginningDatetime"))
        .group_by(Stock.offerId)
        .subquery()
    )
    quarantine_offers_query = (
        Offer.query.join(stock_with_latest_date_by_offer, Offer.id == stock_with_latest_date_by_offer.c.offerId)
        .filter(stock_with_latest_date_by_offer.c.beginningDatetime < first_day_after_quarantine)
        .filter(stock_with_latest_date_by_offer.c.beginningDatetime > today)
    )
    return quarantine_offers_query


def deactivate_offers(offers: List[Offer]):
    for offer in offers:
        offer.isActive = False
    repository.save(*offers)
    offer_ids = [offer.id for offer in offers]
    delete_expired_offers(app.redis_client, offer_ids)


def deactivate_offers_with_max_stock_date_between_today_and_end_of_quarantine(
    first_day_after_quarantine: datetime,
    today: datetime,
    get_offers: Callable = get_offers_with_max_stock_date_between_today_and_end_of_quarantine,
):
    offers = get_offers(first_day_after_quarantine, today)
    deactivate_offers(offers)
