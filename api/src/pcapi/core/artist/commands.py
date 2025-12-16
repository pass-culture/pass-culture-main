import itertools
import logging

import click
import sqlalchemy as sa

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


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)

BATCH_SIZE = 1000

ARTIST_IMPORTERS: list[AbstractImporter] = [
    ArtistImporter(),
    ArtistProductLinkImporter(),
    ArtistAliasImporter(),
]


@blueprint.cli.command("compute_artists_most_relevant_image")
@click.option("--batch-size", type=int, default=BATCH_SIZE, help="Number of artists to process at a time.")
def _compute_artists_most_relevant_image(batch_size: int = BATCH_SIZE) -> None:
    compute_artists_most_relevant_image(batch_size)


def compute_artists_most_relevant_image(batch_size: int = BATCH_SIZE) -> None:
    # Fetch all ids at once. This avoids potential "named cursor isn't valid anymore"
    # error by separating the query from the update/commit loop.
    artist_ids_to_process = db.session.scalars(
        sa.select(artist_models.Artist.id).filter(artist_models.Artist.image.is_(None))
    )
    total_artists_updated = 0
    for artist_id_batch in itertools.batched(artist_ids_to_process, batch_size):
        artists_batch = db.session.query(artist_models.Artist).filter(artist_models.Artist.id.in_(artist_id_batch))
        updated_artist_ids = []
        for artist in artists_batch:
            most_relevant_image = artist_api.get_artist_image_url(artist)
            if most_relevant_image and most_relevant_image != artist.computed_image:
                artist.computed_image = most_relevant_image
                updated_artist_ids.append(artist.id)

        if updated_artist_ids:
            db.session.commit()
            async_index_artist_ids(updated_artist_ids, reason=IndexationReason.ARTIST_IMAGE_UPDATE)
            total_artists_updated += len(updated_artist_ids)
            logger.info("Updated %d artists from batch", len(updated_artist_ids))

    logger.info("Updated %d artist images", total_artists_updated)


@blueprint.cli.command("update_artists_from_delta")
def update_artists_from_delta() -> None:
    logger.info("Starting artists update from delta tables...")
    for importer in ARTIST_IMPORTERS:
        importer.run_delta_update()
    logger.info("Artists update from delta tables finished successfully.")
