import argparse
import csv
import datetime
import logging
import os
import socket
import time

import sqlalchemy as sa

from pcapi import settings
from pcapi.core import search
from pcapi.core.offers import models
import pcapi.core.users.models as users_models
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository


logger = logging.getLogger(__name__)

HOSTNAME = socket.gethostname()

IN_REJECTED_PRODUCT_IDS_FILE_PATH = "/tmp/OUT_rejected_product_ids.csv"
OUT_REJECTED_OFFER_IDS_FILE_PATH = "/tmp/OUT_rejected_offer_ids.csv"


def reject_inappropriate_offers(products_ids: list[int], dry: bool = False) -> list[str]:
    if dry:
        offers = models.Offer.query.filter(
            models.Offer.productId.in_(products_ids),
            models.Offer.validation != models.OfferValidationStatus.REJECTED,
        ).all()

        offer_ids = [o.id for o in offers]
    else:
        res = db.session.execute(
            sa.update(models.Offer)
            .returning(models.Offer.id)
            .where(
                models.Offer.productId.in_(products_ids),
                models.Offer.validation != models.OfferValidationStatus.REJECTED,
            )
            .values(
                validation=models.OfferValidationStatus.REJECTED,
                lastValidationDate=datetime.datetime.utcnow(),
                lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
            ),
            execution_options={"synchronize_session": False},
        )
        offer_ids = [offer_id for offer_id, in res.fetchall()]
    try:
        if dry:
            db.session.rollback()
        else:
            db.session.commit()
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Could not mark offers as inappropriate: %s",
            extra={"offerIds": offer_ids, "exc": str(exception)},
        )
        return []
    logger.info(
        "Rejected inappropriate offers",
        extra={"offerIds": offer_ids},
    )

    if offer_ids and not dry:
        favorites = users_models.Favorite.query.filter(users_models.Favorite.offerId.in_(offer_ids)).all()
        repository.delete(*favorites)
        if not settings.IS_STAGING:
            search.async_index_offer_ids(offer_ids)

    return offer_ids


def _get_remote_to_local_cmd(file_path: str, env: str) -> str:
    return f"kubectl cp -n {env} {HOSTNAME}:{file_path} {os.path.basename(file_path)}"


def update_offers(file_path: str, dry: bool) -> None:
    with open(file_path, newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        product_ids: list[int] = []
        offer_ids: list[int] = []

        for index, row in enumerate(csv_reader):  # pylint:disable=unused-variable
            product_ids.append(int(row[0]))

        offer_ids += reject_inappropriate_offers(product_ids, dry=dry)

        output_files: list[str] = []

        with open(OUT_REJECTED_OFFER_IDS_FILE_PATH, "w+", encoding="utf-8") as cancelled_offer_ids_csv:
            offer_ids = list(set(offer_ids))
            cancelled_offer_ids_csv.write("\n".join(map(str, offer_ids)))
            logger.info("%s emails with bookings written in %s", len(offer_ids), OUT_REJECTED_OFFER_IDS_FILE_PATH)
            output_files.append(OUT_REJECTED_OFFER_IDS_FILE_PATH)

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
            "[reject offers] Reading productIds csv extract %s %s",
            IN_REJECTED_PRODUCT_IDS_FILE_PATH,
            "in dry run mode" if dry_run else "",
        )
        update_offers(IN_REJECTED_PRODUCT_IDS_FILE_PATH, dry_run)
        logger.info("Total duration: %s seconds", time.time() - start)
        if dry_run:
            logger.info("[dryrun] Rerun with --save to apply those changes into the database")
