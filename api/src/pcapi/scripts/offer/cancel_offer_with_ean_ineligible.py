"""
PC-24349
Includes offers that have an ineligible EAN and were created manually

- Reject offers
- Deindexes algolia offers
- Remove offers from favorites
- Cancels reservations with confirmed status
- Extract the email addresses of young people (unexpired credit)
"""

import argparse
import csv
import datetime
import os

import sqlalchemy as sa

from pcapi.core import search
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.flask_app import app
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository


EXTRACT_FOLDER = "/tmp/"

TITELIVE_REJECT_EANS_FILE_PATH = EXTRACT_FOLDER + "OUT_all_rejected_eans.csv"

COLUMN_INDICES = {"EAN": 0}
BATCH_SIZE = 100


def _get_products(eans: list[str]) -> list[int]:
    products = (
        offers_models.Product.query.filter(
            offers_models.Product.extraData["ean"].astext.in_(eans), offers_models.Product.isGcuCompatible.is_(False)
        )
        .order_by(offers_models.Product.id)
        .all()
    )

    print(f"{len(products)} products found on {len(eans)} eans")

    products_ineligible_ids = [p.id for p in products]

    return products_ineligible_ids


def _get_offers(eans: list[str], products_ineligible_ids: list[int]) -> list[offers_models.Offer]:
    offers_auto = (
        offers_models.Offer.query.filter(
            offers_models.Offer.lastProviderId.is_(None), offers_models.Offer.productId.in_(products_ineligible_ids)
        )
        .order_by(offers_models.Offer.id)
        .all()
    )
    print(f"{len(offers_auto)} offers_auto found")

    offers_manually = (
        offers_models.Offer.query.filter(
            offers_models.Offer.lastProviderId.is_(None),
            offers_models.Offer.productId.not_in(products_ineligible_ids),
            offers_models.Offer.extraData["ean"].astext.in_(eans),
        )
        .order_by(offers_models.Offer.id)
        .all()
    )
    print(f"{len(offers_manually)} offers_manually found")

    offers = offers_auto + offers_manually
    print(f"{len(offers)} offers found")
    return offers


def _print_offers_csv(offers: list[offers_models.Offer]) -> None:
    if os.path.exists(EXTRACT_FOLDER + "offers_rejected_prod.csv"):
        header = False
        append_write = "a"  # append if already exists
    else:
        header = True
        append_write = "w"  # make a new file if not

    if offers:
        with open(EXTRACT_FOLDER + "offers_rejected_prod.csv", append_write, encoding="utf-8") as offers_rejected_csv:
            if header:
                offers_rejected_csv.write(";".join(["offer_id", "offer_name", "offer_ean", "product_ean"]) + "\n")
            for offer in offers:
                offer_ean = str(offer.extraData["ean"]) if offer.extraData["ean"] else ""
                product_ean = str(offer.product.extraData["ean"]) if offer.product.extraData else ""
                offers_rejected_csv.write(";".join([str(offer.id), offer.name, offer_ean, product_ean]) + "\n")


def _reject_offers(offers: list[offers_models.Offer], dry_run: bool) -> None:
    for offer in offers:
        offer.validation = offers_models.OfferValidationStatus.REJECTED
        offer.lastValidationDate = datetime.datetime.utcnow()
        offer.lastValidationType = OfferValidationType.CGU_INCOMPATIBLE_PRODUCT
        offer.isActive = False

    if not dry_run:
        repository.save(*offers)
        search.unindex_offer_ids([offer.id for offer in offers])


def _remove_from_favorites(offers: list[offers_models.Offer], dry_run: bool) -> None:
    favorites = users_models.Favorite.query.filter(
        users_models.Favorite.offerId.in_([offer.id for offer in offers])
    ).all()

    print(f"{len(favorites)} favorites found")

    if not dry_run:
        repository.delete(*favorites)


def _get_bookings(offers: list[offers_models.Offer]) -> list[bookings_models.Booking]:
    """
    select booking.id as "bookingId", booking."dateCreated", booking.token, booking.amount, booking."userId",
    "user".email, deposit.type, deposit."expirationDate",
    booking."offererId", booking."venueId", venue."bookingEmail",
    offer.id as "offerId", offer.name as "offerName", offer.description as "offerDescription"
    from booking
    join stock on stock.id = booking."stockId"
    join offer on offer.id = stock."offerId"
    join venue on venue.id = booking."venueId"
    join deposit on deposit.id = booking."depositId"
    join "user" on "user".id = booking."userId"
    where stock."offerId" in (1, ...);
    and booking.status = 'CONFIRMED'
    and deposit."expirationDate" <= now()
    order by booking.id asc
    ;
    """

    bookings = (
        bookings_models.Booking.query.join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(offerers_models.Venue, offerers_models.Venue.id == bookings_models.Booking.venueId)
        .join(finance_models.Deposit, finance_models.Deposit.id == bookings_models.Booking.depositId)
        .join(users_models.User, users_models.User.id == bookings_models.Booking.userId)
        .filter(
            offers_models.Offer.id.in_([offer.id for offer in offers]),
            bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
            finance_models.Deposit.expirationDate <= datetime.datetime.utcnow(),
        )
        .options(
            sa.orm.joinedload(bookings_models.Booking.user).load_only(users_models.User.email),
            sa.orm.joinedload(bookings_models.Booking.deposit).load_only(
                finance_models.Deposit.type, finance_models.Deposit.expirationDate
            ),
            sa.orm.joinedload(bookings_models.Booking.venue).load_only(offerers_models.Venue.bookingEmail),
        )
        .order_by(bookings_models.Booking.id)
        .all()
    )
    print(f"{len(bookings)} confirmed bookings found")
    return bookings


def _print_bookings_csv(bookings: list[bookings_models.Booking]) -> None:
    if bookings:
        with open(EXTRACT_FOLDER + "bookings_rejected.csv", "w+", encoding="utf-8") as offers_rejected_csv:
            offers_rejected_csv.write(
                ";".join(
                    [
                        "booking_id",
                        "booking_date",
                        "token",
                        "amount",
                        "user_id",
                        "user_email",
                        "deposit_type",
                        "deposit_expiration_date",
                        "offerer_id",
                        "venue_id",
                        "booking_email",
                        "offer_id",
                        "offer_name",
                    ]
                )
                + "\n"
            )

            for booking in bookings:
                offers_rejected_csv.write(
                    ";".join(
                        [
                            str(booking.id),
                            booking.dateCreated.date().isoformat(),
                            booking.token,
                            booking.amount,
                            str(booking.userId),
                            booking.user.email,
                            booking.deposit.type.value,
                            booking.deposit.expirationDate.date().isoformat(),
                            str(booking.offererId),
                            str(booking.venueId),
                            booking.venue.bookingEmail,
                            str(booking.stock.offerId),
                            booking.stock.offer.name.replace('"', ""),
                        ]
                    )
                    + "\n"
                )


def _cancel_bookings(bookings: list[bookings_models.Booking]) -> None:
    for booking in bookings:
        # do not send transactional email
        bookings_api._cancel_booking(booking, bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE)


# Subdivise list n-sized
def divide_chunks(array: list, n: int) -> list:
    for i in range(0, len(array), n):
        yield array[i : i + n]


def get_eans_from_file() -> list[str]:
    eans = []
    with open(TITELIVE_REJECT_EANS_FILE_PATH, newline="", encoding="iso-8859-1") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        for row in csv_reader:
            ean = row[COLUMN_INDICES["EAN"]]
            eans.append(ean)
    return eans


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cancel bookings on ean ineligible")
    parser.add_argument(
        "--no-dry-run", "-n", help="cancels after listing", dest="dry_run", action="store_false", default=True
    )
    args = parser.parse_args()

    with app.app_context():
        eans = get_eans_from_file()

        print(f"{len(eans)} eans in file")

        # Traitement par paquets
        chunks = divide_chunks(eans, BATCH_SIZE)

        total_chunks = len(eans) / BATCH_SIZE
        print(f"{total_chunks} paquets")

        i = 0
        for eans in chunks:
            products_ineligible_ids = _get_products(eans)

            offers = _get_offers(eans, products_ineligible_ids)

            _print_offers_csv(offers)

            _remove_from_favorites(offers, dry_run=args.dry_run)
            _reject_offers(offers, dry_run=args.dry_run)

            bookings = _get_bookings(offers)
            _print_bookings_csv(bookings)

            if not args.dry_run:
                _cancel_bookings(bookings)

            i = i + 1

            print(f"{i} / {total_chunks} processed")
