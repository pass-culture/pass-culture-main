import logging

import click
import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

import pcapi.core.artist.models as artist_models
from pcapi.connectors.big_query.importer.artist import ArtistAliasImporter
from pcapi.connectors.big_query.importer.artist import ArtistImporter
from pcapi.connectors.big_query.importer.artist import ArtistProductLinkImporter
from pcapi.connectors.big_query.importer.base import AbstractImporter
from pcapi.core.artist import api as artist_api
from pcapi.core.search import async_index_artist_ids
from pcapi.core.search.models import IndexationReason
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.chunks import get_chunks
from pcapi.utils.repository import transaction


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)

BATCH_SIZE = 1000

ARTIST_IMPORTERS: list[AbstractImporter] = [
    ArtistImporter(),
    ArtistProductLinkImporter(),
    ArtistAliasImporter(),
]


def truncate_artist_tables() -> None:
    with transaction():
        db.session.execute(sa.text("TRUNCATE TABLE artist_product_link"))
    logger.info("ArtistProductLink table truncated")

    with transaction():
        db.session.execute(sa.text("TRUNCATE TABLE artist_alias"))
    logger.info("ArtistAlias table truncated")

    with transaction():
        # Here we use `DELETE` instead of `TRUNCATE` because we are less likely to get
        # an Access Exclusive Lock on table `artist`, on which there is more traffic.
        db.session.execute(sa.text("DELETE FROM artist"))
    logger.info("Artist table truncated")


@blueprint.cli.command("compute_artists_most_relevant_image")
def _compute_artists_most_relevant_image() -> None:
    compute_artists_most_relevant_image()


def compute_artists_most_relevant_image() -> None:
    artists_query: sa_orm.Query[artist_models.Artist] = (
        db.session.query(artist_models.Artist).filter(artist_models.Artist.image.is_(None)).yield_per(BATCH_SIZE)
    )
    total_artists_updated = 0
    for artists_batch in get_chunks(artists_query, chunk_size=BATCH_SIZE):
        updated_artist_ids = []
        for artist in artists_batch:
            most_relevant_image = artist_api.get_artist_image_url(artist)
            if most_relevant_image and most_relevant_image != artist.computed_image:
                artist.computed_image = most_relevant_image
                updated_artist_ids.append(artist.id)

        db.session.commit()
        async_index_artist_ids(updated_artist_ids, reason=IndexationReason.ARTIST_IMAGE_UPDATE)
        total_artists_updated += len(updated_artist_ids)

    logger.info("Updated %d artist images", total_artists_updated)


@blueprint.cli.command("import_all_artists_data")
@click.option("--clear", is_flag=True, help="Truncate artists tables before importing data.")
def import_all_artists_data(clear: bool = False) -> None:
    if clear:
        truncate_artist_tables()

    logger.info("Importing all artists data from BigQuery...")
    for importer in ARTIST_IMPORTERS:
        importer.import_all()
    logger.info("Finished importing all artists data.")


@blueprint.cli.command("update_artists_from_delta")
def update_artists_from_delta() -> None:
    logger.info("Starting artists update from delta tables...")
    for importer in ARTIST_IMPORTERS:
        importer.run_delta_update()
    logger.info("Artists update from delta tables finished successfully.")
