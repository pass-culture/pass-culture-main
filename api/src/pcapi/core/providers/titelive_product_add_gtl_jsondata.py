import csv
import logging
import math
from pathlib import Path
import sys
import time

import sqlalchemy as sa

import pcapi.core.offers.models as offers_models
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.utils.csr import get_csr_from_csr_id


logger = logging.getLogger(__name__)

HEADER_LINE_COUNT = 1

COLUMN_INDICES = {
    "EAN": 0,
    "CODE_GTL": 4,
    "CODE_CLIL": 5,
    "CODE_CSR": 6,
}

EXTRA_DATA_KEYS = {
    "ean": "ean",
    "code_gtl": "gtl_id",
    "code_clil": "code_clil",
    "code_csr": "csr_id",
    "rayon": "rayon",
}


class CsvGtlImportException(Exception):
    pass


# Thanks to https://stackoverflow.com/a/2135920/2127277
def split_in_pages(a: list[str], n: int) -> list[list[str]]:
    k, m = divmod(len(a), n)
    return list(a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def update_products(file_path: str, dry: bool) -> None:
    with open(file_path, newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        total_rows = 0

        ean_datas = {}
        ean_data_list = []
        ean_duplicates = []

        for index, row in enumerate(csv_reader):
            if index >= HEADER_LINE_COUNT:
                total_rows += 1
                ean = row[COLUMN_INDICES["EAN"]]
                gtl_id = row[COLUMN_INDICES["CODE_GTL"]]
                code_clil = row[COLUMN_INDICES["CODE_CLIL"]]
                csr_id = row[COLUMN_INDICES["CODE_CSR"]]
                csr = get_csr_from_csr_id(csr_id)

                # Using offer_models.OfferExtraData is much slower
                extra_data = {
                    EXTRA_DATA_KEYS["ean"]: ean,
                    EXTRA_DATA_KEYS["code_gtl"]: gtl_id,
                    EXTRA_DATA_KEYS["code_clil"]: code_clil,
                    EXTRA_DATA_KEYS["code_csr"]: csr_id,
                    EXTRA_DATA_KEYS["rayon"]: csr["label"] if csr else None,
                }

                if not ean in ean_datas:
                    ean_datas[ean] = extra_data  # this is useful for performance reasons
                    ean_data_list.append(extra_data)
                else:
                    ean_duplicates.append(ean)

        eans = set(ean_datas.keys())

        matching_product_in_db_count = (
            offers_models.Product.query.filter(offers_models.Product.idAtProviders.in_(eans))
            .options(sa.orm.load_only(offers_models.Product.id, offers_models.Product.extraData))
            .count()
        )

        logger.info("Total rows: %s", total_rows)
        logger.info("Total EANs: %s", len(eans))
        logger.info("Ignoring %s EANs present more than once in CSV extract: %s", len(ean_duplicates), ean_duplicates)
        logger.info("Total matching products in database: %s", matching_product_in_db_count)

        products_and_eans_diff_count = len(eans) - matching_product_in_db_count

        if products_and_eans_diff_count != 0:
            logger.info(
                "%s EANs in CSV are not in the database...",
                products_and_eans_diff_count,
            )

        total = len(eans)
        per_page = 1000
        nb_pages = math.ceil(total / per_page)

        logger.info(
            "%s EANs will have extraData edited by batch of %s entries and a total of %s pages",
            total,
            per_page,
            nb_pages,
        )

        pages = split_in_pages(list(eans), nb_pages)
        errors: list[dict] = []

        for index, eans_in_page in enumerate(pages):
            page_id = index + 1

            products = (
                offers_models.Product.query.filter(offers_models.Product.idAtProviders.in_(eans_in_page))
                .options(
                    sa.orm.load_only(
                        offers_models.Product.id, offers_models.Product.idAtProviders, offers_models.Product.extraData
                    )
                )
                .all()
            )

            has_missing_entries_in_db = len(eans_in_page) - len(products) > 0
            if has_missing_entries_in_db:
                logger.warning(
                    "[Page %s/%s] Partial matching: %s/%s database entries found: %s",
                    page_id,
                    nb_pages,
                    len(products),
                    len(eans_in_page),
                    {
                        "page_id": page_id,
                        "ean_not_in_db_total": len(eans_in_page) - len(products),
                        "ean_not_in_db": set(eans_in_page).difference([p.idAtProviders for p in products]),
                    },
                )

            for product in products:
                product.extraData[EXTRA_DATA_KEYS["ean"]] = ean_datas[product.idAtProviders][EXTRA_DATA_KEYS["ean"]]
                product.extraData[EXTRA_DATA_KEYS["code_gtl"]] = ean_datas[product.idAtProviders][
                    EXTRA_DATA_KEYS["code_gtl"]
                ]
                product.extraData[EXTRA_DATA_KEYS["code_clil"]] = ean_datas[product.idAtProviders][
                    EXTRA_DATA_KEYS["code_clil"]
                ]
                product.extraData[EXTRA_DATA_KEYS["code_csr"]] = ean_datas[product.idAtProviders][
                    EXTRA_DATA_KEYS["code_csr"]
                ]
                product.extraData[EXTRA_DATA_KEYS["rayon"]] = (
                    ean_datas[product.idAtProviders][EXTRA_DATA_KEYS["rayon"]]
                    or product.extraData[EXTRA_DATA_KEYS["rayon"]]
                    if EXTRA_DATA_KEYS["rayon"] in product.extraData
                    else None
                )
                if not dry:
                    db.session.add(product)

            if not dry:
                try:
                    db.session.commit()
                except sa.exc.IntegrityError as exception:
                    eans_in_db = {p.idAtProviders for p in products}
                    errors.append(
                        {
                            "page_id": page_id,
                            "db_entries": eans_in_db,
                            "page_entries": eans_in_page,
                            "exception": str(exception),
                        }
                    )
                    logger.error(
                        "[Page %s/%s] Failed to update %s products, rolling back... (eans_in_page: %s) (ean_in_db: %s)",
                        page_id,
                        nb_pages,
                        len(products),
                        eans_in_page,
                        eans_in_db,
                    )
                    db.session.rollback()

                db.session.expunge_all()

        failed_eans = 0
        for error in errors:
            failed_eans += len(error["db_entries"])

        if len(errors) > 0:
            logger.error("Something wrong happened: %s", errors)

        completion_progress_in_percent = (
            (matching_product_in_db_count - failed_eans) / matching_product_in_db_count * 100
        )
        logger.info(
            "Successfully updated %s products out of %s in database for a total of %s requested EANs (%s), exiting...",
            matching_product_in_db_count - failed_eans,
            matching_product_in_db_count,
            len(eans),
            f"{round(completion_progress_in_percent, 2)}%",
        )

        if dry:
            logger.info("[dryrun] Rerun without --dry-run to apply those changes into the database")


if __name__ == "__main__":
    with app.app_context():
        start = time.time()
        dry_run = False

        directory = Path().cwd().parent.parent
        file_name = "ExtractPassCulture.csv"
        csv_file_path = f"{directory}/{file_name}"

        if len(sys.argv) > 1:
            if sys.argv[1] in ["-d", "--dry-run"]:
                dry_run = True
            else:
                csv_file_path = sys.argv[1]

        if len(sys.argv) > 2 and sys.argv[2] in ["-d", "--dry-run"]:
            dry_run = True

        logger.info("Reading GTL csv extract %s %s", csv_file_path, "in dry run mode" if dry_run else "")
        update_products(csv_file_path, dry_run)
        logger.info("Total duration: %s seconds", time.time() - start)
