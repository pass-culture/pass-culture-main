from argparse import ArgumentParser

from pcapi.core.offers import models as offers_models
from pcapi.flask_app import app
from pcapi.models import db


def main(ids: list[int]) -> None:
    stocks = offers_models.Stock.query.filter(
        offers_models.Stock.offerId.in_(ids),
        offers_models.Stock.isSoftDeleted == False,
    )
    for stock in stocks:
        print(f"updating offer {stock.offerId}")
        offers_models.Stock.query.filter(
            offers_models.Stock.offerId == stock.offerId,
            offers_models.Stock.isSoftDeleted == True,
            offers_models.Stock.priceCategoryId == stock.priceCategoryId,
        ).update({"price": stock.price})
        stock.priceCategory.price = stock.price
        db.session.flush()
    db.session.commit()


with app.app_context():
    parser = ArgumentParser()
    parser.add_argument("--ids", nargs="+", type=int, required=True)
    main(parser.parse_args().ids)
