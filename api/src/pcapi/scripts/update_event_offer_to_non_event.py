from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.models import db
from pcapi.scripts.stock.soft_delete_stock import soft_delete_stock


def update_event_offer_to_non_event(offer_id, new_subcategory_id):
    delete_obsolete_stock_and_update_current(offer_id)
    update_offer_subcategory(offer_id, new_subcategory_id)
    db.session.commit()


def delete_obsolete_stock_and_update_current(offer_id):
    stocks = Stock.query.filter(Stock.offerId == offer_id).order_by(Stock.beginningDatetime.desc()).all()
    stock_to_keep = stocks[0]
    stocks_to_delete = stocks[1:]
    for stock in stocks_to_delete:
        soft_delete_stock(stock.id)
    Stock.query.filter(Stock.id == stock_to_keep.id).update(
        {"beginningDatetime": None, "bookingLimitDatetime": None}, synchronize_session=False
    )


def update_offer_subcategory(offer_id, new_subcategory_id):
    offer_to_update = Offer.query.filter(Offer.id == offer_id)
    offer_to_update.update({"subcategoryId": new_subcategory_id}, synchronize_session=False)
