"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=stg \
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
import unicodedata

import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from pcapi.core.artist import models as artist_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
OFFER_ID_HEADER = "offer_id"
ARTIST_TYPE_HEADER = "artist_type"


def read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def slugify_name(name: str) -> str:
    """
    Retourne le nom en minuscule et sans accents
    """
    if not name:
        return ""
    normalized = unicodedata.normalize("NFD", name)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn").lower().strip()


def _update_artist_offer_links(rows_to_process: dict, offers_mapping: dict, links_mapping: dict) -> set:
    modified_offers = set()

    for o_id, a_type in rows_to_process.keys():
        offer = offers_mapping.get(o_id)
        extra_data = offer.extraData if offer else None
        name_to_keep = extra_data.get(a_type) if extra_data else None

        if not name_to_keep:
            continue

        existing_links = [link for link in links_mapping.get(o_id, []) if link.artist_type.value == a_type]

        if not existing_links:
            continue

        existing_link_to_keep = next(
            (link for link in existing_links if link.artist_id is None and link.custom_name == name_to_keep), None
        )

        if existing_link_to_keep:
            duplicates = [link for link in existing_links if link.id != existing_link_to_keep.id]
        else:
            existing_link_to_update = existing_links[0]
            duplicates = existing_links[1:]

            update_stmt = (
                sa.update(artist_models.ArtistOfferLink)
                .where(artist_models.ArtistOfferLink.id == existing_link_to_update.id)
                .values(custom_name=name_to_keep, artist_id=None)
            )
            db.session.execute(update_stmt)

        modified_offers.add(o_id)

        for duplicate in duplicates:
            delete_stmt = sa.delete(artist_models.ArtistOfferLink).where(
                artist_models.ArtistOfferLink.id == duplicate.id
            )
            db.session.execute(delete_stmt)
            logger.info(f"Offre {o_id} ({a_type}) : Suppression du lien doublon ID {duplicate.id}")

    return modified_offers


def _clean_duplicates(modified_offers: set) -> None:
    cleanup_stmt = sa.select(
        artist_models.ArtistOfferLink.id,
        artist_models.ArtistOfferLink.offer_id,
        artist_models.ArtistOfferLink.artist_type,
        artist_models.ArtistOfferLink.custom_name,
    ).where(
        artist_models.ArtistOfferLink.offer_id.in_(list(modified_offers)),
        artist_models.ArtistOfferLink.artist_id.is_(None),
    )

    existing_links = db.session.execute(cleanup_stmt).all()

    # Si on a le même tuple (offer_id, artist_type, slug_name) -> On ne garde que la première ligne
    seen_combinations = {}
    links_ids_to_delete = []

    for link in existing_links:
        slug = slugify_name(link.custom_name)
        key = (link.offer_id, link.artist_type, slug)

        if key in seen_combinations:
            # le tuple (offer_id, artist_type, slug_name) à déjà été vu : on marque cet ArtistOfferLink pour être supprimé
            links_ids_to_delete.append(link.id)
            logger.info(
                f"Doublon détecté pour l'ArtistOfferLink {link.id}) sur l'offre {link.offer_id} avec le nom {link.custom_name}."
            )
        else:
            seen_combinations[key] = link.id

    if links_ids_to_delete:
        delete_duplicates_stmt = sa.delete(artist_models.ArtistOfferLink).where(
            artist_models.ArtistOfferLink.id.in_(links_ids_to_delete)
        )
        db.session.execute(delete_duplicates_stmt)
        logger.info(f"{len(links_ids_to_delete)} liens en doublon supprimés de la table ArtistOfferLink.")


def process_batch(batch_rows: tuple, commit: bool) -> None:
    offer_ids_to_fetch = []
    rows = []

    for row in batch_rows:
        o_id = int(row.get(OFFER_ID_HEADER))
        a_type = row.get(ARTIST_TYPE_HEADER)
        offer_ids_to_fetch.append(o_id)
        rows.append({"offer_id": o_id, "artist_type": a_type})

    rows_to_process = {(r["offer_id"], r["artist_type"]): r for r in rows}
    offer_stmt = (
        sa.select(offers_models.Offer)
        .where(offers_models.Offer.id.in_(list(offer_ids_to_fetch)))
        .options(joinedload(offers_models.Offer.product))
    )
    offers_mapping = {offer.id: offer for offer in db.session.scalars(offer_stmt).all()}

    links_stmt = sa.select(artist_models.ArtistOfferLink).where(
        artist_models.ArtistOfferLink.offer_id.in_(list(offer_ids_to_fetch))
    )

    links_mapping: dict[int, list] = dict()
    for link in db.session.scalars(links_stmt).all():
        if link.offer_id not in links_mapping:
            links_mapping[link.offer_id] = []
        links_mapping[link.offer_id].append(link)

    # 1/2 : Remplacer les ArtistOfferLink ayant un custom_name uniquement par la bonne valeur dans les extraData
    modified_offers = _update_artist_offer_links(rows_to_process, offers_mapping, links_mapping)

    # 2/2 on supprime les doublons (cf ticket JIRA)
    if modified_offers:
        _clean_duplicates(modified_offers)

    if commit:
        db.session.commit()
    else:
        db.session.flush()

    logger.info("Fin du batch")
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
