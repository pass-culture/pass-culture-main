"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-39366-rattrapage-artistes \
  -f NAMESPACE=link_artists_to_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import itertools
import logging
import os
import typing

import sqlalchemy as sa
from sqlalchemy import exc as sa_exc

from pcapi.app import app
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
OFFER_ID_HEADER = "offer_id"
ARTIST_TYPE_HEADER = "artist_type"
CUSTOM_NAME_HEADER = "custom_name"
ARTIST_ID_HEADER = "artist_id"


class BatchFailure(Exception):
    pass


def read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def create_offer_artist_link(offer_id: int, row: dict) -> dict | None:
    """
    Lorsqu'on lance ce script, la table artist_offer_link est vide
    """

    artist_type = row[ARTIST_TYPE_HEADER]
    custom_name = str(row[CUSTOM_NAME_HEADER])
    artist_id = str(row[ARTIST_ID_HEADER])

    if artist_id:
        return {
            "offer_id": offer_id,
            "artist_type": artist_type,
            "artist_id": artist_id,
        }
    elif custom_name:
        return {
            "offer_id": offer_id,
            "artist_type": artist_type,
            "custom_name": custom_name,
        }

    logger.warning(f"Ligne ignorée : pas d'artist_id ni de custom_name pour offer_id {offer_id}")
    return None


def process_batch(batch_rows: tuple, not_dry: bool) -> None:
    batch_offer_ids = {int(row[OFFER_ID_HEADER]) for row in batch_rows if int(row[OFFER_ID_HEADER])}

    existing_offer_ids = {
        offer.id
        for offer in db.session.query(offers_models.Offer)
        .filter(
            offers_models.Offer.id.in_(batch_offer_ids),
            offers_models.Offer.productId.is_(None),  # on enlève les offres liées à des produits
        )
        .all()
    }

    links_to_add = []
    for row in batch_rows:
        offer_id = int(row[(OFFER_ID_HEADER)])

        if offer_id not in existing_offer_ids:
            logger.error(f"Offer ID {offer_id} introuvable ou liée à un produit")
            continue

        try:
            link = create_offer_artist_link(offer_id, row)
            if link:
                links_to_add.append(link)
        except Exception as e:
            logger.error(f"Erreur lors de la création du artist_offer_link pour l'offre {offer_id}: {e}")

    if links_to_add:
        try:
            db.session.execute(sa.insert(artist_models.ArtistOfferLink), links_to_add)
            if not_dry:
                db.session.commit()
                logger.info(f"Batch terminé avec succès, ajout de {len(links_to_add)} artist_offer_links")
            else:
                db.session.flush()
                db.session.rollback()
        except sa_exc.IntegrityError:
            db.session.rollback()
            raise BatchFailure("Erreur d'intégrité lors de la création d'artist_offer_links pour ce batch")
        except sa_exc.SQLAlchemyError as e:
            db.session.rollback()
            raise BatchFailure(f"Erreur lors du flush/commit du batch: {e}")

    db.session.expunge_all()


def main(not_dry: bool, filename: str, start_from_batch: int = 1) -> None:
    rows = read_csv_file(filename)

    for batch_idx, batch_rows in enumerate(itertools.batched(rows, BATCH_SIZE), start=1):
        if batch_idx < start_from_batch:
            continue

        logger.info(f"Traitement du batch {batch_idx}")
        process_batch(batch_rows, not_dry)

    if not not_dry:
        db.session.rollback()
        logger.info("Dry run terminé, rollback des données")
    else:
        logger.info("Script terminé avec succès")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--start-from-batch", type=int, default=1)
    args = parser.parse_args()
    filename = "artist_update"

    main(not_dry=args.not_dry, start_from_batch=args.start_from_batch, filename=filename)
