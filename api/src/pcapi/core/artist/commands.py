import abc
import logging
import typing
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

BigQueryModel = typing.TypeVar("BigQueryModel", ArtistModel, ArtistProductLinkModel, ArtistAliasModel)
Model = typing.TypeVar("Model", artist_models.Artist, artist_models.ArtistProductLink, artist_models.ArtistAlias)


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

        with transaction():
            db.session.bulk_save_objects(inserted_data)

        name_of_class = type(inserted_data[0]).__name__
        logger.info("Successfully imported %s %s", len(inserted_data), name_of_class)

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
        return artist_models.Artist.query.filter_by(id=artist.id).first() is not None

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
            artist_models.ArtistAlias.query.filter_by(
                artist_id=alias.artist_id,
                artist_alias_name=alias.artist_alias_name,
                artist_cluster_id=alias.artist_cluster_id,
            ).first()
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
            artist_models.ArtistProductLink.query.filter_by(
                artist_id=link.artist_id,
                product_id=link.product_id,
            ).first()
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
