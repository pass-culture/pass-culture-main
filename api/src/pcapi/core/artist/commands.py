import abc
import logging
import typing
from typing import Iterable
from typing import Type

from sqlalchemy import exc as sa_exc

import pcapi.core.artist.models as artist_models
from pcapi.connectors.big_query import queries as big_query_queries
from pcapi.connectors.big_query.queries.artist import ArtistAliasDeltaQuery
from pcapi.connectors.big_query.queries.artist import ArtistAliasModel
from pcapi.connectors.big_query.queries.artist import ArtistModel
from pcapi.connectors.big_query.queries.artist import ArtistProductLinkDeltaQuery
from pcapi.connectors.big_query.queries.artist import ArtistProductLinkModel
from pcapi.connectors.big_query.queries.artist import DeltaAction
from pcapi.connectors.big_query.queries.artist import DeltaArtistAliasModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistProductLinkModel
from pcapi.core.artist.utils import get_artist_type
from pcapi.core.artist.utils import sanitize_author_html
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.repository import transaction


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000

BigQueryModel = typing.TypeVar(
    "BigQueryModel",
    ArtistModel,
    ArtistProductLinkModel,
    ArtistAliasModel,
)

BigQueryDeltaModel = typing.TypeVar(
    "BigQueryDeltaModel",
    DeltaArtistModel,
    DeltaArtistProductLinkModel,
    DeltaArtistAliasModel,
)

Model = typing.TypeVar("Model", artist_models.Artist, artist_models.ArtistProductLink, artist_models.ArtistAlias)


@blueprint.cli.command("import_all_artists_data")
def import_all_artists_data() -> None:
    import_all_artists()
    import_all_artist_product_links()
    import_all_artist_aliases()


@blueprint.cli.command("update_artists_from_delta")
def update_artists_from_delta() -> None:
    logger.info("Starting artists update from delta tables")

    UpdateArtists().run_delta_update()
    UpdateArtistProductLinks().run_delta_update()
    UpdateArtistAliases().run_delta_update()

    logger.info("Artists update from delta tables finished successfully")


class BaseImportCommon(abc.ABC, typing.Generic[Model]):
    def bulk_update_database(self, inserted_data: list[Model]) -> None:
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

    def _save_one_by_one(self, items: list[Model]) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        for item in items:
            try:
                with transaction():
                    db.session.add(item)
            except sa_exc.IntegrityError as exc:
                logger.error("Failed to import %s: %s", class_name, exc)

    @abc.abstractmethod
    def get_sqlalchemy_class(self) -> Type[Model]:
        raise NotImplementedError


class BaseImportTemplate(BaseImportCommon[Model], abc.ABC, typing.Generic[BigQueryModel, Model]):
    def import_all(self) -> None:
        imported = []
        for item in self.get_all():
            if self.exists(item):
                continue

            new = self.create(item)
            imported.append(new)

            if len(imported) >= BATCH_SIZE:
                self.bulk_update_database(imported)
                imported = []

        self.bulk_update_database(imported)

    @abc.abstractmethod
    def get_all(self) -> Iterable[BigQueryModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, model: BigQueryModel) -> Model | None:
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, model: BigQueryModel) -> Model:
        raise NotImplementedError


class BaseDeltaImportTemplate(BaseImportCommon[Model], abc.ABC, typing.Generic[BigQueryDeltaModel, Model]):
    def run_delta_update(self) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        logger.info("Processing delta for %s.", class_name)

        items_to_upsert = []
        pks_to_delete = []

        for delta_item in self.get_all():
            if delta_item.action == DeltaAction.ADD and not self.exists(delta_item):
                sqlalchemy_obj = self.create(delta_item)
                items_to_upsert.append(sqlalchemy_obj)
            elif delta_item.action == DeltaAction.REMOVE:
                obj_to_delete = self.exists(delta_item)
                if obj_to_delete:
                    pks_to_delete.append(obj_to_delete.id)

            if len(items_to_upsert) >= BATCH_SIZE:
                self.bulk_update_database(items_to_upsert)
                items_to_upsert = []

            if len(pks_to_delete) >= BATCH_SIZE:
                self._bulk_delete(pks_to_delete)
                pks_to_delete = []

        self._bulk_delete(pks_to_delete)
        self.bulk_update_database(items_to_upsert)
        logger.info("Finished processing delta for %s.", class_name)

    def _bulk_delete(self, pks: list) -> None:
        if not pks:
            return

        model_class = self.get_sqlalchemy_class()
        try:
            with transaction():
                query = db.session.query(model_class).filter(model_class.id.in_(pks))
                deleted_count = query.delete(synchronize_session=False)
                logger.info("Successfully deleted %d %s", deleted_count, model_class.__name__)
        except Exception as e:
            logger.error("Failed to bulk delete %s: %s", model_class.__name__, e, exc_info=True)
            db.session.rollback()

    @abc.abstractmethod
    def get_all(self) -> Iterable[BigQueryDeltaModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, model: BigQueryDeltaModel) -> Model | None:
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, model: BigQueryDeltaModel) -> Model:
        raise NotImplementedError


class ImportArtists(BaseImportTemplate[ArtistModel, artist_models.Artist]):
    def get_all(self) -> Iterable[ArtistModel]:
        yield from big_query_queries.ArtistQuery().execute()

    def get_sqlalchemy_class(self) -> Type[artist_models.Artist]:
        return artist_models.Artist

    def exists(self, artist: ArtistModel) -> artist_models.Artist | None:
        return db.session.query(artist_models.Artist).filter_by(id=artist.id).first()

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

    def get_sqlalchemy_class(self) -> Type[artist_models.ArtistAlias]:
        return artist_models.ArtistAlias

    def exists(self, alias: ArtistAliasModel) -> artist_models.ArtistAlias | None:
        return (
            db.session.query(artist_models.ArtistAlias)
            .filter_by(
                artist_id=alias.artist_id,
                artist_alias_name=alias.artist_alias_name,
                offer_category_id=alias.offer_category_id,
                artist_type=get_artist_type(alias.artist_type),
            )
            .first()
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

    def get_sqlalchemy_class(self) -> Type[artist_models.ArtistProductLink]:
        return artist_models.ArtistProductLink

    def exists(self, link: ArtistProductLinkModel) -> artist_models.ArtistProductLink | None:
        return (
            db.session.query(artist_models.ArtistProductLink)
            .filter_by(
                artist_id=link.artist_id,
                product_id=link.product_id,
                artist_type=artist_models.ArtistType(link.artist_type),
            )
            .first()
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


class UpdateArtists(BaseDeltaImportTemplate[DeltaArtistModel, artist_models.Artist]):
    def get_all(self) -> Iterable[DeltaArtistModel]:
        yield from big_query_queries.ArtistDeltaQuery().execute()

    def get_sqlalchemy_class(self) -> Type[artist_models.Artist]:
        return artist_models.Artist

    def exists(self, artist: DeltaArtistModel) -> artist_models.Artist | None:
        return db.session.query(artist_models.Artist).filter_by(id=artist.id).first()

    def create(self, delta_model: DeltaArtistModel) -> artist_models.Artist:
        return artist_models.Artist(
            id=delta_model.id,
            name=delta_model.name,
            description=delta_model.description,
            image=delta_model.image,
            image_author=sanitize_author_html(delta_model.image_author),
            image_license=delta_model.image_license,
            image_license_url=delta_model.image_license_url,
        )


class UpdateArtistProductLinks(BaseDeltaImportTemplate[DeltaArtistProductLinkModel, artist_models.ArtistProductLink]):
    def get_all(self) -> Iterable[DeltaArtistProductLinkModel]:
        yield from ArtistProductLinkDeltaQuery().execute()

    def get_sqlalchemy_class(self) -> Type[artist_models.ArtistProductLink]:
        return artist_models.ArtistProductLink

    def exists(self, link: DeltaArtistProductLinkModel) -> artist_models.ArtistProductLink | None:
        return (
            db.session.query(artist_models.ArtistProductLink)
            .filter_by(
                artist_id=link.artist_id,
                product_id=link.product_id,
                artist_type=artist_models.ArtistType(link.artist_type),
            )
            .first()
        )

    def create(self, delta_model: DeltaArtistProductLinkModel) -> artist_models.ArtistProductLink:
        return artist_models.ArtistProductLink(
            artist_id=delta_model.artist_id,
            product_id=delta_model.product_id,
            artist_type=get_artist_type(delta_model.artist_type),
        )


class UpdateArtistAliases(BaseDeltaImportTemplate[DeltaArtistAliasModel, artist_models.ArtistAlias]):
    def get_all(self) -> Iterable[DeltaArtistAliasModel]:
        yield from ArtistAliasDeltaQuery().execute()

    def get_sqlalchemy_class(self) -> Type[artist_models.ArtistAlias]:
        return artist_models.ArtistAlias

    def exists(self, alias: DeltaArtistAliasModel) -> artist_models.ArtistAlias | None:
        return (
            db.session.query(artist_models.ArtistAlias)
            .filter_by(
                artist_id=alias.artist_id,
                artist_alias_name=alias.artist_alias_name,
                offer_category_id=alias.offer_category_id,
                artist_type=get_artist_type(alias.artist_type),
            )
            .first()
        )

    def create(self, delta_model: DeltaArtistAliasModel) -> artist_models.ArtistAlias:
        return artist_models.ArtistAlias(
            artist_id=delta_model.artist_id,
            artist_alias_name=delta_model.artist_alias_name,
            artist_cluster_id=delta_model.artist_cluster_id,
            artist_type=get_artist_type(delta_model.artist_type),
            artist_wiki_data_id=delta_model.artist_wiki_data_id,
            offer_category_id=delta_model.offer_category_id,
        )
