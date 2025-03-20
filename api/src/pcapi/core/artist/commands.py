import logging
from typing import Iterable

from pcapi.connectors.big_query import queries as big_query_queries
from pcapi.connectors.big_query.queries.artist import ArtistAliasModel
from pcapi.connectors.big_query.queries.artist import ArtistModel
from pcapi.connectors.big_query.queries.artist import ArtistProductLinkModel
import pcapi.core.artist.models as artist_models
from pcapi.core.artist.utils import get_artist_type
from pcapi.core.artist.utils import sanitize_author_html
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


@blueprint.cli.command("import_all_artists_data")
def import_all_artists_data() -> None:
    import_all_artists()
    import_all_artist_product_links()
    import_all_artist_aliases()


def get_all_artists() -> Iterable[ArtistModel]:
    yield from big_query_queries.ArtistQuery().execute()


def get_all_artist_product_links() -> Iterable[ArtistProductLinkModel]:
    yield from big_query_queries.ArtistProductLinkQuery().execute()


def get_all_artist_aliases() -> Iterable[ArtistAliasModel]:
    yield from big_query_queries.ArtistAliasQuery().execute()


def bulk_update_database(inserted_data: list) -> None:
    if not inserted_data:
        return
    with transaction():
        db.session.bulk_save_objects(inserted_data)

    name_of_class = type(inserted_data[0]).__name__

    logger.info("Successfully imported %s %s", len(inserted_data), name_of_class)


def import_all_artists() -> None:
    logger.info("Importing artists from big query table")
    imported_artists = []

    for raw_artist in get_all_artists():
        existing_artist = artist_models.Artist.query.filter_by(id=raw_artist.id).first()
        if existing_artist:
            continue

        image_author = sanitize_author_html(raw_artist.image_author)

        new_artist = artist_models.Artist(
            id=raw_artist.id,
            name=raw_artist.name,
            description=raw_artist.description,
            image=raw_artist.image,
            image_author=image_author,
            image_license=raw_artist.image_license,
            image_license_url=raw_artist.image_license_url,
        )

        imported_artists.append(new_artist)
        if len(imported_artists) == BATCH_SIZE:
            bulk_update_database(imported_artists)
            imported_artists = []

    bulk_update_database(imported_artists)


def import_all_artist_product_links() -> None:
    logger.info("Importing artist product links from BigQuery")
    imported_product_links: list[artist_models.ArtistProductLink] = []

    for raw_product_link in get_all_artist_product_links():
        existing_product_link = artist_models.ArtistProductLink.query.filter_by(
            artist_id=raw_product_link.artist_id,
            product_id=raw_product_link.product_id,
        ).first()
        if existing_product_link:
            continue

        new_product_link = artist_models.ArtistProductLink(
            artist_id=raw_product_link.artist_id,
            product_id=raw_product_link.product_id,
            artist_type=get_artist_type(raw_product_link.artist_type),
        )

        imported_product_links.append(new_product_link)
        if len(imported_product_links) == BATCH_SIZE:
            bulk_update_database(imported_product_links)
            imported_product_links = []

    bulk_update_database(imported_product_links)


def import_all_artist_aliases() -> None:
    logger.info("Importing artist aliases from BigQuery")
    imported_aliases: list[artist_models.ArtistAlias] = []

    for raw_alias in get_all_artist_aliases():
        existing_alias = artist_models.ArtistAlias.query.filter_by(
            artist_id=raw_alias.artist_id,
            artist_alias_name=raw_alias.artist_alias_name,
        ).first()
        if existing_alias:
            continue

        new_alias = artist_models.ArtistAlias(
            artist_id=raw_alias.artist_id,
            artist_alias_name=raw_alias.artist_alias_name,
            artist_cluster_id=raw_alias.artist_cluster_id,
            artist_type=get_artist_type(raw_alias.artist_type),
            artist_wiki_data_id=raw_alias.artist_wiki_data_id,
            offer_category_id=raw_alias.offer_category_id,
        )

        imported_aliases.append(new_alias)
        if len(imported_aliases) == BATCH_SIZE:
            bulk_update_database(imported_aliases)
            imported_aliases = []

    bulk_update_database(imported_aliases)
