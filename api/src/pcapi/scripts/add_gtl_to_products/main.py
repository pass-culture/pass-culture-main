"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/BSR-add-gtl-to-existing-products/api/src/pcapi/scripts/add_gtl_to_products/main.py

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.offers.models import Product
from pcapi.models import db


logger = logging.getLogger(__name__)


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        yield from csv_rows


def main(filename: str) -> None:
    rows = _read_csv_file(filename)
    for row in rows:
        ean = row["ean"].rjust(13, "0")  # given csv files deleted the starting 0 of some EAN
        if row["gtl"]:
            gtl = row["gtl"]
            product = db.session.query(Product).filter(Product.ean == ean).one_or_none()
            if product:
                old_extra_data = product.extraData or {}
                product.extraData = {**old_extra_data, **{"gtl_id": gtl}}
                logger.info(f"Product {product.id} now has gtl_id {gtl}")
                db.session.add(product)
        else:
            logger.info(f"No gtl given for EAN: {ean}")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", required=True)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(args.filename)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
