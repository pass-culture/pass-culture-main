import argparse
import collections
import csv
import datetime
import itertools
import logging
import os
import socket
import time
import typing

import sqlalchemy as sa

from pcapi import settings
from pcapi.core import search
import pcapi.core.bookings.api as bookings_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.offers import models
from pcapi.core.providers.titelive_gtl import get_gtl
import pcapi.core.users.models as users_models
from pcapi.flask_app import app
from pcapi.local_providers.titelive_things.titelive_things import ADULT_ADVISOR_TEXT
from pcapi.local_providers.titelive_things.titelive_things import BASE_VAT
from pcapi.local_providers.titelive_things.titelive_things import BOX_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import CALENDAR_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_01_EXTRACURRICULAR
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_01_SCHOOL
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_01_YOUNG
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_02_AFTER_3_AND_BEFORE_6
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_02_BEFORE_3
from pcapi.local_providers.titelive_things.titelive_things import LECTORAT_EIGHTEEN_ID
from pcapi.local_providers.titelive_things.titelive_things import OBJECT_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import PAPER_CONSUMABLE_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import PAPER_PRESS_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import PAPER_PRESS_VAT
from pcapi.local_providers.titelive_things.titelive_things import POSTER_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import TOEFL_TEXT
from pcapi.local_providers.titelive_things.titelive_things import TOEIC_TEXT
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository


logger = logging.getLogger(__name__)

HOSTNAME = socket.gethostname()

TITELIVE_EXTRACT_FILE_PATH = "/tmp/ExtractPassCulture.csv"
TITELIVE_EXTRACT_COMMENT_FILE_PATH = "/tmp/extraction_public_averti.csv"


OUT_CANCELLED_BOOKING_EMAILS_FILE_PATH = "/tmp/OUT_cancelled_bookings_emails.csv"
OUT_ALL_REJECTED_EANS_FILE_PATH = "/tmp/OUT_all_rejected_eans.csv"
GET_OUT_DETAIL_REJECTED_EANS_FILE_PATH = lambda reason: f"/tmp/OUT_{reason}_rejected_eans.csv"

HEADER_LINE_COUNT = 1
COMMENT_COLUMN_INDICES = {
    "EAN": 0,
    "COMMENT": 1,
}
COLUMN_INDICES = {
    "EAN": 0,
    "CODE_SUPPORT": 1,
    "IDLECTORAT": 2,
    "TAUX_TVA": 3,
    "CODE_GTL": 4,
    "TITLE": 7,
}


# This if the exact copy of offers_api.reject_inappropriate_products with dry run support and return list of email instead of bool
def reject_inappropriate_products(ean: str, dry: bool = False) -> list[str]:
    products = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).all()
    emails: list[str] = []

    if not products:
        return emails

    for product in products:
        product.isGcuCompatible = False
        db.session.add(product)

    offers_query = models.Offer.query.filter(
        models.Offer.productId.in_(p.id for p in products),
        models.Offer.validation != models.OfferValidationStatus.REJECTED,
    ).options(sa.orm.joinedload(models.Offer.stocks).joinedload(models.Stock.bookings))

    offers = offers_query.all()

    if not dry:
        offers_query.update(
            values={
                "validation": models.OfferValidationStatus.REJECTED,
                "lastValidationDate": datetime.datetime.utcnow(),
                "lastValidationType": OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
            },
            synchronize_session="fetch",
        )

    offer_ids = []
    for offer in offers:
        offer_ids.append(offer.id)
        if dry:
            bookings = list(itertools.chain.from_iterable(stock.bookings for stock in offer.stocks))
        else:
            bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)

        for booking in bookings:
            emails.append(booking.user.email)

        # `send_booking_cancellation_emails_to_user_and_offerer` would send an e-mail to the pro and
        # none to the beneficiary. We want the opposite. E-mails will be sent by a separate script.
        # if send_booking_cancellation_emails and not dry:
        #     for booking in bookings:
        #         send_booking_cancellation_emails_to_user_and_offerer(booking, reason=BookingCancellationReasons.FRAUD)

    try:
        if not dry:
            db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark product and offers as inappropriate: %s",
            extra={"ean": ean, "products": [p.id for p in products], "exc": str(exception)},
        )
        return emails
    logger.info(
        "Rejected inappropriate products",
        extra={"ean": ean, "products": [p.id for p in products], "offers": offer_ids},
    )

    if offer_ids and not dry:
        favorites = users_models.Favorite.query.filter(users_models.Favorite.offerId.in_(offer_ids)).all()
        repository.delete(*favorites)
        if not settings.IS_STAGING:
            search.async_index_offer_ids(offer_ids)

    return emails


def get_ineligibility_reason(**kwargs: typing.Any) -> str | None:
    gtl_id = kwargs.get("gtl_id")
    code_support = kwargs.get("code_support")
    id_lectorat = kwargs.get("id_lectorat")
    taux_tva = kwargs.get("taux_tva")
    title = kwargs.get("title")
    comment = kwargs.get("comment")

    gtl = None

    if title:
        title = title.lower()

    if comment:
        comment = comment.lower()

    try:
        if gtl_id:
            gtl = get_gtl(gtl_id)
    except KeyError:
        pass

    # Ouvrage avec pierres ou encens, jeux de société ou escape game en coffrets,
    # marchandisage : jouets, goodies, peluches, posters, papeterie, etc...
    if taux_tva == BASE_VAT:
        return "vat-20"

    # ouvrage du rayon scolaire
    if gtl and gtl["level_01_code"] == GTL_LEVEL_01_SCHOOL:
        return "school"

    # ouvrage du rayon parascolaire,
    # code de la route (méthode d'apprentissage + codes basiques), code nautique, code aviation, etc...
    if gtl and gtl["level_01_code"] == GTL_LEVEL_01_EXTRACURRICULAR:
        return "extracurricular"

    if code_support == CALENDAR_SUPPORT_CODE:
        return "calendar"

    if code_support == POSTER_SUPPORT_CODE:
        return "poster"

    if code_support == PAPER_CONSUMABLE_SUPPORT_CODE:
        return "paper-consumable"

    # Coffrets (contenant un produit + un petit livret)
    if code_support == BOX_SUPPORT_CODE:
        return "box"

    # Oracles contenant des jeux de tarot
    if code_support == OBJECT_SUPPORT_CODE:
        return "object"

    # # ouvrage "lectorat 18+" (Pornographie / ultra-violence)
    if id_lectorat == LECTORAT_EIGHTEEN_ID and comment and ADULT_ADVISOR_TEXT in comment:
        return "pornography-or-violence"

    # Petite jeunesse (livres pour le bains, peluches, puzzles, etc...)
    if (
        gtl
        and gtl["level_01_code"] == GTL_LEVEL_01_YOUNG
        and gtl["level_02_code"]
        in [
            GTL_LEVEL_02_BEFORE_3,
            GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ]
    ):
        return "small-young"

    # Toeic or toefl
    if TOEIC_TEXT in title or TOEFL_TEXT in title:
        return "toeic-toefl"

    if taux_tva == PAPER_PRESS_VAT and code_support == PAPER_PRESS_SUPPORT_CODE:
        return "press"

    return None


def _get_remote_to_local_cmd(file_path: str, env: str) -> str:
    return f"kubectl cp -n {env} {HOSTNAME}:{file_path} {os.path.basename(file_path)}"


def update_products(file_path: str, comments_file_path: str, dry: bool) -> None:
    product_whitelist_eans = {
        ean for ean, in fraud_models.ProductWhitelist.query.with_entities(fraud_models.ProductWhitelist.ean).all()
    }

    comments_dict: dict[str, str] = {}

    with open(comments_file_path, newline="", encoding="utf-8") as csv_comments_file:
        csv_reader = csv.reader(csv_comments_file, delimiter=";")
        for index, row in enumerate(csv_reader, 1):
            if index <= HEADER_LINE_COUNT:
                continue
            ean = row[COMMENT_COLUMN_INDICES["EAN"]]
            if ean:
                comments_dict[ean] = row[COMMENT_COLUMN_INDICES["COMMENT"]]

    with open(file_path, newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        total_rows = 0

        whitelisted_eans: list[str] = []
        rejected_eans: list[str] = []
        reasons: dict[str, dict] = collections.defaultdict(lambda: {"eans": [], "total": 0})
        emails: list[str] = []

        for index, row in enumerate(csv_reader, 1):
            if index <= HEADER_LINE_COUNT:
                continue
            total_rows += 1
            ean = row[COLUMN_INDICES["EAN"]]
            gtl_id = row[COLUMN_INDICES["CODE_GTL"]]
            code_support = row[COLUMN_INDICES["CODE_SUPPORT"]]
            id_lectorat = row[COLUMN_INDICES["IDLECTORAT"]]
            taux_tva = row[COLUMN_INDICES["TAUX_TVA"]]
            taux_tva = taux_tva.replace(".", ",")  #  fix decimal separator different from titelive_things files.
            title = row[COLUMN_INDICES["TITLE"]]

            ineligibility_reason = get_ineligibility_reason(
                gtl_id=gtl_id,
                code_support=code_support,
                id_lectorat=id_lectorat,
                taux_tva=taux_tva,
                title=title,
                comment=comments_dict.get(ean, ""),
            )

            if ineligibility_reason:
                if ean in product_whitelist_eans:
                    whitelisted_eans.append(ean)
                else:
                    reasons[ineligibility_reason]["eans"].append(ean)
                    reasons[ineligibility_reason]["total"] += 1
                    rejected_eans.append(ean)
                    emails += reject_inappropriate_products(ean, dry=dry)

        logger.info(
            "%s whitelisted EANs found in CSV (out of %s in product_whitelist table): %s",
            len(whitelisted_eans),
            len(product_whitelist_eans),
            whitelisted_eans,
        )

        output_files: list[str] = []

        with open(OUT_ALL_REJECTED_EANS_FILE_PATH, "w+", encoding="utf-8") as all_rejected_eans_csv:
            all_rejected_eans_csv.write("\n".join(rejected_eans))
            logger.info("%s EANs rejected written in %s", len(rejected_eans), OUT_ALL_REJECTED_EANS_FILE_PATH)
            output_files.append(OUT_ALL_REJECTED_EANS_FILE_PATH)

        for reason in reasons:
            reason_file_path = GET_OUT_DETAIL_REJECTED_EANS_FILE_PATH(reason)
            with open(reason_file_path, "w+", encoding="utf-8") as reason_csv:
                reason_csv.write("\n".join(reasons[reason]["eans"]))
                logger.info(
                    "%s EANs rejected with reason=%s written in %s", reasons[reason]["total"], reason, reason_file_path
                )
                output_files.append(reason_file_path)

        with open(OUT_CANCELLED_BOOKING_EMAILS_FILE_PATH, "w+", encoding="utf-8") as cancelled_bookings_emails_csv:
            emails = list(set(emails))
            cancelled_bookings_emails_csv.write("\n".join(emails))
            logger.info("%s emails with bookings written in %s", len(emails), OUT_CANCELLED_BOOKING_EMAILS_FILE_PATH)
            output_files.append(OUT_CANCELLED_BOOKING_EMAILS_FILE_PATH)

        env = ""
        if "staging" in HOSTNAME:
            env = "staging"
        elif "production" in HOSTNAME:
            env = "production"

        if env and not dry:
            download_file_cmds = "\n            ".join(
                [_get_remote_to_local_cmd(output_file, env) for output_file in output_files]
            )
            print(
                f"""
            To download output files:
            
            {download_file_cmds}
            
            """
            )


if __name__ == "__main__":
    with app.app_context():
        start = time.time()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--save", help="Save change to database", type=bool, action=argparse.BooleanOptionalAction, default=False
        )
        dry_run = not parser.parse_args().save

        logger.info(
            "Reading GTL csv extract %s,%s %s",
            TITELIVE_EXTRACT_FILE_PATH,
            TITELIVE_EXTRACT_COMMENT_FILE_PATH,
            "in dry run mode" if dry_run else "",
        )
        update_products(TITELIVE_EXTRACT_FILE_PATH, TITELIVE_EXTRACT_COMMENT_FILE_PATH, dry_run)
        logger.info("Total duration: %s seconds", time.time() - start)
        if dry_run:
            logger.info("[dryrun] Rerun with --save to apply those changes into the database")
