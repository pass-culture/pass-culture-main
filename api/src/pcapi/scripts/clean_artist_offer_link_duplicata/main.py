"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-40608-nettoyage-artistes \
  -f NAMESPACE=clean_artist_offer_link_duplicata \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import itertools
import logging
import os
import typing
import unicodedata

from pcapi.app import app
from pcapi.core.artist import models as artist_models
from pcapi.models import db


logger = logging.getLogger(__name__)

BATCH_SIZE = 10000
OFFER_ID_HEADER = "offer_id"


def read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def strip_accents(s: str) -> str:
    """
    source: stackoverflow, petit instant de nostalgie vintage
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    """
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def process_batch(batch_rows: tuple, commit: bool) -> None:
    batch_offer_ids = {int(row[OFFER_ID_HEADER]) for row in batch_rows if row[OFFER_ID_HEADER]}

    artist_offer_links = (
        db.session.query(artist_models.ArtistOfferLink)
        .outerjoin(artist_models.Artist)
        .filter(artist_models.ArtistOfferLink.offer_id.in_(batch_offer_ids))
    ).all()

    seen_links: dict[tuple, artist_models.ArtistOfferLink] = {}
    ids_to_delete = []

    for link in artist_offer_links:
        # on récupère le nom et on le normalise
        artist_name = link.custom_name or (link.artist.name if link.artist else "")
        artist_name_normalized = strip_accents(artist_name.lower().strip())

        # je sais pas si c'est la meilleur façon de faire
        key = (link.offer_id, link.artist_type, artist_name_normalized)

        if key in seen_links:
            existing_link = seen_links[key]
            current_link_has_artist_id = link.artist_id is not None
            existing_link_has_artist_id = existing_link.artist_id is not None

            # on supprime l'entrée d'artist_offer_link sans artist_id
            if current_link_has_artist_id and not existing_link_has_artist_id:
                ids_to_delete.append(existing_link.id)
                seen_links[key] = link
            elif not current_link_has_artist_id and existing_link_has_artist_id:
                ids_to_delete.append(link.id)

            # il n'y a pas de cas de doublons sur l'artist id pour une même offre+artist_type,
            # donc le dernier cas est le suivant:
            # on a deux entrées avec des custom name: on supprime celui dont l'ID est le plus
            # récent (vu avec le métier)
            else:
                if link.id < existing_link.id:
                    ids_to_delete.append(existing_link.id)
                    seen_links[key] = link
                else:
                    ids_to_delete.append(link.id)
        # on n'a pas encore vu ce triptique offre - artist_type - nom
        else:
            seen_links[key] = link

    # ça va être sympa la recette 🍲
    logger.info(f"Voici les ID qu'on va retirer de la table artist_offer_link {ids_to_delete}")

    if ids_to_delete:
        try:
            count = (
                db.session.query(artist_models.ArtistOfferLink)
                .filter(artist_models.ArtistOfferLink.id.in_(ids_to_delete))
                .delete(synchronize_session=False)
            )

            logger.info(f"Supprimé {count} doublons")
            if commit:
                db.session.commit()
            else:
                db.session.flush()
                db.session.rollback()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression : {e}")
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
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--start-from-batch", type=int, default=1)
    args = parser.parse_args()
    filename = "artist_update"

    main(commit=args.commit, start_from_batch=args.start_from_batch, filename=filename)
