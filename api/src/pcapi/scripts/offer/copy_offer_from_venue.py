import argparse
import csv
import datetime
import os

from pcapi.core.offers import models as offer_models
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.models import offer_mixin
import sqlalchemy as sa
from pcapi.flask_app import app
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.routes.backoffice.filters import format_date
from pcapi.repository import transaction
from pcapi.models import db

OFFERS_TO_COPY_BEFORE_CSV = "offers_to_copy_before.csv"
OFFERS_TO_COPY_AFTER_CSV = "offers_to_copy_after.csv"

OFFERS_COPIED_CSV = "offers_copied.csv"

STOCKS_TO_COPY_CSV = "stocks_to_copy.csv"
STOCKS_COPIED_CSV = "stocks_copied.csv"

# local
FROM_VENUE_ID = 4
TO_VENUE_ID = 2

# testing
# FROM_VENUE_ID = 10947
# TO_VENUE_ID = 10948

# staging and prod
# FROM_VENUE_ID=2525
# TO_VENUE_ID=92072

EXTRACT_FOLDER = "/tmp/"


def delete_files_csv(list_filenames: list[str]):
    for filename in list_filenames:
        file = EXTRACT_FOLDER + filename
        # If file exists, delete it.
        if os.path.isfile(file):
            os.remove(file)


def _copy_offers(dryrun: bool):
    offers_to_copy = (
        offer_models.Offer.query.join(offer_models.Stock)
        .filter(offer_models.Offer.venueId == FROM_VENUE_ID)
        .filter(offer_models.Offer.subcategoryId == subcategories.MATERIEL_ART_CREATIF.id)
        .filter(offer_models.Offer.validation == offer_mixin.OfferValidationStatus.APPROVED)
        .filter(sa.or_(offer_models.Stock.remainingQuantity.is_(None), offer_models.Stock.remainingQuantity > 0))
        .all()
    )

    print(f"{len(offers_to_copy)} offers to copy")

    _print_offers_csv(offers_to_copy, OFFERS_TO_COPY_BEFORE_CSV)

    if offers_to_copy:
        stocks_copied = []
        offers_copied = []
        all_stocks_to_copy = []
        with transaction():
            for offer_to_copy in offers_to_copy:
                offer_copied = duplicate_object(offer_to_copy, offer_models.Offer)
                offer_copied.venueId = TO_VENUE_ID
                db.session.add(offer_copied)

                offers_copied.append(offer_copied)

                stocks_to_copy: list[offer_models.Stock] = offer_models.Stock.query.filter(
                    offer_models.Stock.offerId == offer_to_copy.id
                ).all()

                print(f"{len(stocks_to_copy)} stocks for offer {offer_to_copy.id}")
                all_stocks_to_copy.extend(stocks_to_copy)

                price_category_by_offer = {}

                for stock_to_copy in stocks_to_copy:
                    stock_copied: offer_models.Stock = duplicate_object(stock_to_copy, offer_models.Stock)
                    stock_copied.quantity = (
                        None
                        if stock_to_copy.quantity is None
                        else stock_to_copy.quantity - stock_to_copy.dnBookedQuantity
                    )
                    stock_copied.dnBookedQuantity = 0
                    stock_copied.offerId = offer_copied.id

                    if stock_to_copy.priceCategoryId:
                        if stock_to_copy.priceCategoryId not in price_category_by_offer:
                            priceCategory_to_copy: offer_models.PriceCategory = offer_models.PriceCategory.query.filter(
                                offer_models.PriceCategory.id == stock_copied.priceCategoryId
                            ).one()
                            priceCategory_copied: offer_models.PriceCategory = duplicate_object(
                                priceCategory_to_copy, offer_models.PriceCategory
                            )
                            priceCategory_copied.offerId = offer_copied.id

                            db.session.add(priceCategory_copied)
                            price_category_by_offer[stock_to_copy.priceCategoryId] = priceCategory_copied.id

                        stock_copied.priceCategoryId = price_category_by_offer[stock_to_copy.priceCategoryId]

                    db.session.add(stock_copied)

                    stocks_copied.append(stock_copied)

                offer_to_copy.validation = offer_models.OfferValidationStatus.REJECTED
                offer_to_copy.lastValidationDate = datetime.datetime.utcnow()
                offer_to_copy.lastValidationType = OfferValidationType.AUTO
                offer_to_copy.lastValidationAuthorUserId = None
                offer_to_copy.isActive = False
                db.session.add(offer_to_copy)

            if dryrun:
                db.session.rollback()

            print(f"{len(stocks_copied)} stocks copied")
            print(f"{len(offers_copied)} offers copied")

        if not dryrun:
            _print_stocks_csv(all_stocks_to_copy, STOCKS_TO_COPY_CSV)
            _print_offers_csv(offers_copied, OFFERS_COPIED_CSV)
            _print_offers_csv(offers_to_copy, OFFERS_TO_COPY_AFTER_CSV)
            _print_stocks_csv(stocks_copied, STOCKS_COPIED_CSV)

        print("fin")


def _print_offers_csv(offers: list[offer_models.Offer], filename: str) -> None:
    if offers:
        with open(os.path.join(EXTRACT_FOLDER, filename), "w", encoding="utf-8", newline="") as offers_csv:
            writer = csv.writer(offers_csv)
            writer.writerow(
                [
                    "offer_id",
                    "offer_name",
                    "offer.validation",
                    "offer.venueId",
                    "offer.subcategoryId",
                    "product_id",
                ]
            )
            for offer in offers:
                product_id = str(offer.product.id) if offer.product else ""
                writer.writerow(
                    [
                        str(offer.id),
                        offer.name,
                        str(offer.validation),
                        str(offer.venueId),
                        offer.subcategoryId,
                        product_id,
                    ]
                )


def _print_stocks_csv(stocks: list[offer_models.Stock], filename: str) -> None:
    if stocks:
        with open(EXTRACT_FOLDER + filename, "w", encoding="utf-8") as stocks_csv:
            writer = csv.writer(stocks_csv)
            writer.writerow(
                [
                    "idAtProviders",
                    "offer_id",
                    "stock_id",
                    "stock.quantity",
                    "stock.dnBookedQuantity",
                    "stock_beginningDatetime",
                    "stock_bookingLimitDatetime",
                    "stock.priceCategoryId",
                ]
            )
            for stock in stocks:
                writer.writerow(
                    [
                        str(stock.idAtProviders),
                        str(stock.offer.id),
                        str(stock.id),
                        str(stock.quantity),
                        str(stock.dnBookedQuantity),
                        format_date(stock.beginningDatetime, "%d/%m/%Y à %Hh%M"),
                        format_date(stock.bookingLimitDatetime, "%d/%m/%Y à %Hh%M"),
                        str(stock.priceCategoryId),
                    ]
                )


def duplicate_object(old_obj, base_model):
    # SQLAlchemy related data class?
    if not isinstance(old_obj, base_model):
        raise TypeError("The given parameter with type {} is not " "mapped by SQLAlchemy.".format(type(old_obj)))

    mapper = sa.inspect(type(old_obj))
    new_obj = type(old_obj)()

    for name, col in mapper.columns.items():
        # no PrimaryKey not Unique
        if not col.primary_key and not col.unique:
            setattr(new_obj, name, getattr(old_obj, name))
            # print(name, getattr(old_obj, name), "=>", getattr(new_obj, name))
        elif col.unique and name != "idAtProviders":
            print("WARN : column not copied : ", name, " base_model", base_model)

    return new_obj


if __name__ == "__main__":
    app.app_context().push()

    description = f"copy offer from venue {FROM_VENUE_ID} to venue {TO_VENUE_ID}"
    print(description)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    print("dry-run", not args.not_dry)

    delete_files_csv(
        [
            OFFERS_TO_COPY_BEFORE_CSV,
            OFFERS_TO_COPY_AFTER_CSV,
            OFFERS_COPIED_CSV,
            STOCKS_TO_COPY_CSV,
            STOCKS_COPIED_CSV,
        ]
    )

    _copy_offers(not args.not_dry)
