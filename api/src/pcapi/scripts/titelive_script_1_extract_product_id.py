import argparse
import collections
import csv
import logging
import socket
import time
import typing

import pcapi.core.fraud.models as fraud_models
from pcapi.core.offers import models
from pcapi.core.providers.titelive_gtl import get_gtl
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
from pcapi.scripts.script_utils import log_remote_to_local_cmd


logger = logging.getLogger(__name__)

HOSTNAME = socket.gethostname()

TITELIVE_EXTRACT_FILE_PATH = "/tmp/extractionPassCulture-2023-08-18.csv"

OUT_REJECTED_PRODUCT_IDS_FILE_PATH = "/tmp/OUT_rejected_product_ids.csv"
OUT_ALL_REJECTED_EANS_FILE_PATH = "/tmp/OUT_all_rejected_eans.csv"
GET_OUT_DETAIL_REJECTED_EANS_FILE_PATH = lambda reason: f"/tmp/OUT_{reason}_rejected_eans.csv"

HEADER_LINE_COUNT = 1
COLUMN_INDICES = {
    "EAN": 0,
    "CODE_SUPPORT": 1,
    "IDLECTORAT": 2,
    "TAUX_TVA": 3,
    "CODE_GTL": 4,
    "TITLE": 7,
    "COMMENT": 8,
}

# because titelive now use 0.1 precision decimal :)
PAPER_PRESS_VAT_LOW_PRECISION = "2,10"
BASE_VAT_LOW_PRECISION = "20,0"


def reject_inappropriate_products(ean: str, dry: bool = False) -> list[int]:
    products = models.Product.query.filter(models.Product.extraData["ean"].astext == ean).all()
    productIds: list[int] = [p.id for p in products]

    if not products:
        return productIds

    for product in products:
        product.isGcuCompatible = False
        db.session.add(product)

    try:
        if dry:
            db.session.rollback()
        else:
            db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark product as inappropriate: %s",
            extra={"ean": ean, "products": productIds, "exc": str(exception)},
        )
        return []
    logger.info(
        "Rejected inappropriate products",
        extra={"ean": ean, "products": productIds},
    )

    return productIds


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
    if taux_tva in (BASE_VAT, BASE_VAT_LOW_PRECISION):
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

    if taux_tva in (PAPER_PRESS_VAT, PAPER_PRESS_VAT_LOW_PRECISION) and code_support == PAPER_PRESS_SUPPORT_CODE:
        return "press"

    return None


def update_products(file_path: str, dry: bool) -> None:
    product_whitelist_eans = {
        ean for ean, in fraud_models.ProductWhitelist.query.with_entities(fraud_models.ProductWhitelist.ean).all()
    }

    comments_dict: dict[str, str] = {}

    with open(file_path, newline="", encoding="iso-8859-1") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        total_rows = 0

        whitelisted_eans: list[str] = []
        rejected_eans: list[str] = []
        reasons: dict[str, dict] = collections.defaultdict(lambda: {"eans": [], "total": 0})
        productIds: list[int] = []

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
            comments_dict[ean] = row[COLUMN_INDICES["COMMENT"]]

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
                    productIds += reject_inappropriate_products(ean, dry=dry)

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

        with open(OUT_REJECTED_PRODUCT_IDS_FILE_PATH, "w+", encoding="utf-8") as cancelled_product_ids_csv:
            productIds = list(set(productIds))
            cancelled_product_ids_csv.write("\n".join(map(str, productIds)))
            logger.info("%s rejected product ids written in %s", len(productIds), OUT_REJECTED_PRODUCT_IDS_FILE_PATH)
            output_files.append(OUT_REJECTED_PRODUCT_IDS_FILE_PATH)

        if not dry:
            log_remote_to_local_cmd(output_files)


if __name__ == "__main__":
    with app.app_context():
        start = time.time()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--save", help="Save change to database", type=bool, action=argparse.BooleanOptionalAction, default=False
        )
        dry_run = not parser.parse_args().save

        logger.info(
            "[reject products] Reading GTL csv extract %s %s",
            TITELIVE_EXTRACT_FILE_PATH,
            "in dry run mode" if dry_run else "",
        )
        update_products(TITELIVE_EXTRACT_FILE_PATH, dry_run)
        logger.info("Total duration: %s seconds", time.time() - start)
        if dry_run:
            logger.info("[dryrun] Rerun with --save to apply those changes into the database")
