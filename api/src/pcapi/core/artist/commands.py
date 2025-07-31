import abc
import logging
import typing
from typing import Iterable

import sqlalchemy as sa
from sqlalchemy import exc as sa_exc

import pcapi.core.artist.models as artist_models
from pcapi.connectors.big_query import queries as big_query_queries
from pcapi.connectors.big_query.queries.artist import ArtistAliasModel
from pcapi.connectors.big_query.queries.artist import ArtistModel
from pcapi.connectors.big_query.queries.artist import ArtistProductLinkModel
from pcapi.core.artist.api import update_artists_image_from_products
from pcapi.core.artist.utils import get_artist_type
from pcapi.core.artist.utils import sanitize_author_html
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.chunks import get_chunks


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000

BigQueryModel = typing.TypeVar("BigQueryModel", ArtistModel, ArtistProductLinkModel, ArtistAliasModel)
Model = typing.TypeVar("Model", artist_models.Artist, artist_models.ArtistProductLink, artist_models.ArtistAlias)


@blueprint.cli.command("fill_artist_images_from_products")
def fill_artist_images_from_products() -> None:
    artists_query = sa.select(artist_models.Artist.id).where(artist_models.Artist.image.is_(None))
    artist_batches = get_chunks(db.session.execute(artists_query).scalars().yield_per(100))
    for artists in artist_batches:
        update_artists_image_from_products(artists)


@blueprint.cli.command("import_all_artists_data")
def import_all_artists_data() -> None:
    import_all_artists()
    import_all_artist_product_links()
    import_all_artist_aliases()


class BaseImportTemplate(abc.ABC, typing.Generic[BigQueryModel, Model]):
    def import_all(self) -> None:
        imported = []
        for item in self.get_all():
            if self.exists(item):
                continue

            new = self.create(item)
            imported.append(new)

            if len(imported) == BATCH_SIZE:
                self.bulk_update_database(imported)
                imported = []

        self.bulk_update_database(imported)

    def bulk_update_database(self, inserted_data: list) -> None:
        if not inserted_data:
            return

        class_name = type(inserted_data[0]).__name__
        try:
            with transaction():
                db.session.bulk_save_objects(inserted_data)
        except sa_exc.IntegrityError as exc:
            logger.info("Failed to import batch of %s: %s. Importing one by one.", class_name, exc)
            self._save_one_by_one(inserted_data)
        else:
            logger.info("Successfully imported %s %s", len(inserted_data), class_name)

    def _save_one_by_one(self, inserted_data: list) -> None:
        class_name = type(inserted_data[0]).__name__
        for item in inserted_data:
            try:
                with transaction():
                    db.session.add(item)
            except sa_exc.IntegrityError as exc:
                logger.error("Failed to import %s: %s", class_name, exc)

    @abc.abstractmethod
    def get_all(self) -> Iterable[BigQueryModel]:
        raise NotImplementedError()

    @abc.abstractmethod
    def exists(self, model: BigQueryModel) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, model: BigQueryModel) -> Model:
        raise NotImplementedError()


class ImportArtists(BaseImportTemplate[ArtistModel, artist_models.Artist]):
    def get_all(self) -> Iterable[ArtistModel]:
        yield from big_query_queries.ArtistQuery().execute()

    def exists(self, artist: ArtistModel) -> bool:
        return db.session.query(artist_models.Artist).filter_by(id=artist.id).first() is not None

    def create(self, artist: ArtistModel) -> artist_models.Artist:
        return artist_models.Artist(
            id=artist.id,
            name=artist.name,
            description=artist.description,
            image=artist.image,
            image_author=sanitize_author_html(artist.image_author),
            image_license=artist.image_license,
            image_license_url=artist.image_license_url,
        )


class ImportAliases(BaseImportTemplate[ArtistAliasModel, artist_models.ArtistAlias]):
    def get_all(self) -> Iterable[ArtistAliasModel]:
        yield from big_query_queries.ArtistAliasQuery().execute()

    def exists(self, alias: ArtistAliasModel) -> bool:
        return (
            db.session.query(artist_models.ArtistAlias)
            .filter_by(
                artist_id=alias.artist_id,
                artist_alias_name=alias.artist_alias_name,
                artist_cluster_id=alias.artist_cluster_id,
            )
            .first()
            is not None
        )

    def create(self, alias: ArtistAliasModel) -> artist_models.ArtistAlias:
        return artist_models.ArtistAlias(
            artist_id=alias.artist_id,
            artist_alias_name=alias.artist_alias_name,
            artist_cluster_id=alias.artist_cluster_id,
            artist_type=get_artist_type(alias.artist_type),
            artist_wiki_data_id=alias.artist_wiki_data_id,
            offer_category_id=alias.offer_category_id,
        )


class ImportProductLinks(BaseImportTemplate[ArtistProductLinkModel, artist_models.ArtistProductLink]):
    def get_all(self) -> Iterable[ArtistProductLinkModel]:
        yield from big_query_queries.ArtistProductLinkQuery().execute()

    def exists(self, link: ArtistProductLinkModel) -> bool:
        return (
            db.session.query(artist_models.ArtistProductLink)
            .filter_by(
                artist_id=link.artist_id,
                product_id=link.product_id,
            )
            .first()
            is not None
        )

    def create(self, link: ArtistProductLinkModel) -> artist_models.ArtistProductLink:
        return artist_models.ArtistProductLink(
            artist_id=link.artist_id,
            product_id=link.product_id,
            artist_type=get_artist_type(link.artist_type),
        )


def import_all_artists() -> None:
    logger.info("Importing artists from big query table")
    ImportArtists().import_all()


def import_all_artist_product_links() -> None:
    logger.info("Importing artist product links from BigQuery")
    ImportProductLinks().import_all()


def import_all_artist_aliases() -> None:
    logger.info("Importing artist aliases from BigQuery")
    ImportAliases().import_all()
