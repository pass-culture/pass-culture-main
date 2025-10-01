from typing import Type

from pcapi.connectors.big_query.importer.base import AbstractImporter
from pcapi.connectors.big_query.queries import artist as bq_artist_queries
from pcapi.core.artist import models as artist_models
from pcapi.core.artist.utils import get_artist_type
from pcapi.core.artist.utils import sanitize_author_html
from pcapi.models import db


class ArtistImporter(
    AbstractImporter[bq_artist_queries.ArtistModel, bq_artist_queries.DeltaArtistModel, artist_models.Artist]
):
    def get_sqlalchemy_class(self) -> Type[artist_models.Artist]:
        return artist_models.Artist

    def get_full_import_query(self) -> bq_artist_queries.ArtistQuery:
        return bq_artist_queries.ArtistQuery()

    def get_delta_import_query(self) -> bq_artist_queries.ArtistDeltaQuery:
        return bq_artist_queries.ArtistDeltaQuery()

    def exists(
        self, model: bq_artist_queries.ArtistModel | bq_artist_queries.DeltaArtistModel
    ) -> artist_models.Artist | None:
        return db.session.query(artist_models.Artist).filter_by(id=model.id).first()

    def create(self, model: bq_artist_queries.ArtistModel | bq_artist_queries.DeltaArtistModel) -> artist_models.Artist:
        return artist_models.Artist(
            id=model.id,
            name=model.name,
            description=model.description,
            image=model.image,
            image_author=sanitize_author_html(model.image_author),
            image_license=model.image_license,
            image_license_url=model.image_license_url,
        )

    def update(self, sqlalchemy_obj: artist_models.Artist, delta_model: bq_artist_queries.DeltaArtistModel) -> None:
        sqlalchemy_obj.name = delta_model.name
        sqlalchemy_obj.description = delta_model.description
        sqlalchemy_obj.image = delta_model.image
        sqlalchemy_obj.image_author = sanitize_author_html(delta_model.image_author)
        sqlalchemy_obj.image_license = delta_model.image_license
        sqlalchemy_obj.image_license_url = delta_model.image_license_url


class ArtistProductLinkImporter(
    AbstractImporter[
        bq_artist_queries.ArtistProductLinkModel,
        bq_artist_queries.DeltaArtistProductLinkModel,
        artist_models.ArtistProductLink,
    ]
):
    def get_sqlalchemy_class(self) -> Type[artist_models.ArtistProductLink]:
        return artist_models.ArtistProductLink

    def get_full_import_query(self) -> bq_artist_queries.ArtistProductLinkQuery:
        return bq_artist_queries.ArtistProductLinkQuery()

    def get_delta_import_query(self) -> bq_artist_queries.ArtistProductLinkDeltaQuery:
        return bq_artist_queries.ArtistProductLinkDeltaQuery()

    def exists(
        self, model: bq_artist_queries.ArtistProductLinkModel | bq_artist_queries.DeltaArtistProductLinkModel
    ) -> artist_models.ArtistProductLink | None:
        return (
            db.session.query(artist_models.ArtistProductLink)
            .filter_by(
                artist_id=model.artist_id,
                product_id=model.product_id,
                artist_type=get_artist_type(model.artist_type),
            )
            .first()
        )

    def create(
        self, model: bq_artist_queries.ArtistProductLinkModel | bq_artist_queries.DeltaArtistProductLinkModel
    ) -> artist_models.ArtistProductLink:
        return artist_models.ArtistProductLink(
            artist_id=model.artist_id,
            product_id=model.product_id,
            artist_type=get_artist_type(model.artist_type),
        )

    def update(
        self,
        sqlalchemy_obj: artist_models.ArtistProductLink,
        delta_model: bq_artist_queries.DeltaArtistProductLinkModel,
    ) -> None:
        pass


class ArtistAliasImporter(
    AbstractImporter[
        bq_artist_queries.ArtistAliasModel,
        bq_artist_queries.DeltaArtistAliasModel,
        artist_models.ArtistAlias,
    ]
):
    def get_sqlalchemy_class(self) -> Type[artist_models.ArtistAlias]:
        return artist_models.ArtistAlias

    def get_full_import_query(self) -> bq_artist_queries.ArtistAliasQuery:
        return bq_artist_queries.ArtistAliasQuery()

    def get_delta_import_query(self) -> bq_artist_queries.ArtistAliasDeltaQuery:
        return bq_artist_queries.ArtistAliasDeltaQuery()

    def exists(
        self, model: bq_artist_queries.ArtistAliasModel | bq_artist_queries.DeltaArtistAliasModel
    ) -> artist_models.ArtistAlias | None:
        return (
            db.session.query(artist_models.ArtistAlias)
            .filter_by(
                artist_id=model.artist_id,
                artist_alias_name=model.artist_alias_name,
                offer_category_id=model.offer_category_id,
                artist_type=get_artist_type(model.artist_type),
            )
            .first()
        )

    def create(
        self, model: bq_artist_queries.ArtistAliasModel | bq_artist_queries.DeltaArtistAliasModel
    ) -> artist_models.ArtistAlias:
        return artist_models.ArtistAlias(
            artist_id=model.artist_id,
            artist_alias_name=model.artist_alias_name,
            artist_cluster_id=model.artist_cluster_id,
            artist_type=get_artist_type(model.artist_type),
            artist_wiki_data_id=model.artist_wiki_data_id,
            offer_category_id=model.offer_category_id,
        )

    def update(
        self, sqlalchemy_obj: artist_models.ArtistAlias, delta_model: bq_artist_queries.DeltaArtistAliasModel
    ) -> None:
        sqlalchemy_obj.artist_cluster_id = delta_model.artist_cluster_id
        sqlalchemy_obj.artist_wiki_data_id = delta_model.artist_wiki_data_id
