"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-41603-rattrapage-artistes-encore \
  -f NAMESPACE=clean_artist_again \
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

from pcapi.core.artist import models as artist_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
OFFER_ID_HEADER = "offer_id"
CUSTOM_NAME_HEADER = "custom_name"
ARTIST_ID_HEADER = "artist_id"


def read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def process_batch(batch_rows: tuple, commit: bool) -> None:
    # on récupère les ID pour faire une seule requête en DB pour récupérer les noms d'artistes nécessaires
    artist_ids_to_fetch = set()
    rows_to_process = []

    for row in batch_rows:
        offer_id = int(row.get(OFFER_ID_HEADER))
        artist_id = str(row.get(ARTIST_ID_HEADER))
        custom_name = str(row.get(CUSTOM_NAME_HEADER))

        if artist_id:
            rows_to_process.append(row)  # on ne veut mettre à jour que les artist_offer_link avec un artist_id
            if not custom_name:
                artist_ids_to_fetch.add(artist_id)  # si pas de custom name -> on cherche le nom de l'Artist

    # Requête pour avoir les noms d'artistes
    stmt = sa.select(artist_models.Artist.id, artist_models.Artist.name).where(
        artist_models.Artist.id.in_(artist_ids_to_fetch)
    )
    results = db.session.execute(stmt).all()
    artist_names_mapping = {r.id: r.name for r in results}

    # Mappings d'artist_offer_link pour l'update
    artist_offer_links_to_update = []
    for row in rows_to_process:
        artist_id = str(row[ARTIST_ID_HEADER])
        custom_name = str(row[CUSTOM_NAME_HEADER])

        resolved_name = custom_name if custom_name else artist_names_mapping.get(artist_id)

        if not resolved_name:
            logger.warning(f"Impossible de trouver un nom pour l'artiste {artist_id} (offre {offer_id})")
            continue

        artist_offer_links_to_update.append(
            {
                "offer_id": offer_id,  # PK pour identifier le bon ArtistOfferLink lors de l'update
                "artist_id": None,  # on supprime l'artist id
                "custom_name": resolved_name,  # on met un custom name à la place
                "_target_artist_id": artist_id,  # PK pour identifier le bon ArtistOfferLink lors de l'update
            }
        )

    # Update
    for link in artist_offer_links_to_update:
        try:
            with atomic():
                update_stmt = (
                    sa.update(artist_models.ArtistOfferLink)
                    .filter_by(
                        offer_id=link["offer_id"],
                        artist_id=link["_target_artist_id"],
                    )
                    .values(artist_id=None, custom_name=link["custom_name"])
                )
                db.session.execute(update_stmt)

        except sa_exc.IntegrityError:
            # Si on arrive ici, c'est que (offer_id, artist_type, custom_name) existe déjà,
            # du coup on supprime la ligne qui contient l'artist_id
            logger.info(
                f"Suppression de l'offer artist link pour l'offre {row[OFFER_ID_HEADER]} avec l'artist id: {link['_target_artist_id']}"
            )

            delete_stmt = sa.delete(artist_models.ArtistOfferLink).where(
                artist_models.ArtistOfferLink.offer_id == link["offer_id"],
                artist_models.ArtistOfferLink.artist_id == link["_target_artist_id"],
            )
            db.session.execute(delete_stmt)

        if commit:
            db.session.commit()
            logger.info(f"Batch traité : {len(artist_offer_links_to_update)} liens mis à jour.")
        else:
            db.session.flush()
            logger.info(f"Dry run : {len(artist_offer_links_to_update)} liens auraient été mis à jour.")

    db.session.expunge_all()


def main(commit: bool, filename: str, start_from_batch: int = 1) -> None:
    rows = read_csv_file(filename)

    for batch_idx, batch_rows in enumerate(itertools.batched(rows, BATCH_SIZE), start=1):
        if batch_idx < start_from_batch:
            continue

        logger.info(f"Traitement du batch {batch_idx}")
        process_batch(batch_rows, commit)

    if not commit:
        db.session.rollback()
        logger.info("Dry run terminé, rollback des données")
    else:
        logger.info("Script terminé avec succès")


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--start-from-batch", type=int, default=1)
    args = parser.parse_args()
    filename = "artist_cleanup"

    main(commit=args.commit, start_from_batch=args.start_from_batch, filename=filename)
