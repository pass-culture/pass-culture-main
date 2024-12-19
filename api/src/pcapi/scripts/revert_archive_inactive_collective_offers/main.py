import argparse
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"{namespace_dir}/archived_offer_ids.txt"

    offer_ids = []
    with open(file_path, "r", encoding="utf-8") as ids_file:
        for line in ids_file.readlines():
            offer_id_str = line.replace("\n", "")
            if not offer_id_str:
                continue

            offer_ids.append(int(offer_id_str))

    logger.info("%s offers to revert", len(offer_ids))
    collective_offers: typing.Iterable[educational_models.CollectiveOffer] = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id.in_(offer_ids))
        .order_by(educational_models.CollectiveOffer.id)
        .yield_per(1000)
    )

    for offer in collective_offers:
        if not offer.isArchived:
            logger.warning("Offer with id %s is already not archived, skipping", offer.id)
            continue

        if offer.isActive:
            logger.warning("Offer with id %s is active", offer.id)

        offer.dateArchived = None

    if args.not_dry:
        logger.info("Finished revert archive offers")
        db.session.commit()
    else:
        logger.info("Finished dry run for revert archive offers, rollback")
        db.session.rollback()
