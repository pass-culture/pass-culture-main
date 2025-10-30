import logging
import uuid
from unittest import mock

import pytest

import pcapi.core.artist.models as artist_models
import pcapi.core.offers.factories as offers_factories
from pcapi.connectors.big_query.importer.artist import ArtistAliasImporter
from pcapi.connectors.big_query.importer.artist import ArtistImporter
from pcapi.connectors.big_query.importer.artist import ArtistProductLinkImporter
from pcapi.connectors.big_query.importer.base import DeltaAction
from pcapi.connectors.big_query.queries.artist import ArtistProductLinkModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistAliasModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistProductLinkModel
from pcapi.core.artist import commands
from pcapi.core.artist.factories import ArtistAliasFactory
from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.artist.factories import ArtistProductLinkFactory
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistAlias
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.search import redis_queues
from pcapi.core.search.models import IndexationReason
from pcapi.models import db

from . import fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class ImportAllArtistsTest:
    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistQuery.execute")
    def test_import_all_artists_creates_artists(
        self,
        get_all_artists_mock,
    ):
        get_all_artists_mock.return_value = fixtures.big_query_artist_fixture

        ArtistImporter().import_all()

        get_all_artists_mock.assert_called_once()
        all_artists = db.session.query(Artist).all()
        assert len(all_artists) == 2

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistQuery.execute")
    def test_import_all_artists_creates_artists_is_idempotent(self, get_all_artists_mock):
        get_all_artists_mock.return_value = fixtures.big_query_artist_fixture

        ArtistImporter().import_all()

        get_all_artists_mock.assert_called_once()

        all_artists = db.session.query(Artist).all()
        assert len(all_artists) == 2

        get_all_artists_mock.reset_mock()
        ArtistImporter().import_all()

        get_all_artists_mock.assert_called_once()
        all_artists = db.session.query(Artist).all()
        assert len(all_artists) == 2

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistProductLinkQuery.execute")
    def test_import_all_artist_product_links_creates_product_links(self, get_all_artists_product_links_mock, caplog):
        albums_by_same_artist = ProductFactory.create_batch(
            size=4, subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id
        )
        books_by_same_artist = ProductFactory.create_batch(size=4, subcategoryId=subcategories.LIVRE_PAPIER.id)
        author = ArtistFactory()
        performer = ArtistFactory()

        artists_product_link_fixture = fixtures.build_big_query_artist_product_link_fixture(
            product_ids=[album.id for album in books_by_same_artist],
            artist_id=author.id,
            artist_type=artist_models.ArtistType.AUTHOR.value,
        ) + fixtures.build_big_query_artist_product_link_fixture(
            product_ids=[album.id for album in albums_by_same_artist],
            artist_id=performer.id,
            artist_type=artist_models.ArtistType.PERFORMER.value,
        )
        get_all_artists_product_links_mock.return_value = artists_product_link_fixture

        with caplog.at_level(logging.INFO):
            ArtistProductLinkImporter().import_all()

        get_all_artists_product_links_mock.assert_called_once()

        author = db.session.query(Artist).filter_by(id=author.id).one()
        for product in author.products:
            assert product in books_by_same_artist

        performer = db.session.query(Artist).filter_by(id=performer.id).one()
        for product in performer.products:
            assert product in albums_by_same_artist

        assert "Successfully imported 8 ArtistProductLink" in caplog.text

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistAliasQuery.execute")
    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistQuery.execute")
    def test_import_all_artist_aliases_creates_artist_aliases_creates_artist_aliases(
        self,
        get_all_artists_mock,
        get_all_artist_aliases_mock,
    ):
        get_all_artist_aliases_mock.return_value = fixtures.big_query_artist_alias_fixture
        get_all_artists_mock.return_value = fixtures.big_query_artist_fixture

        ArtistImporter().import_all()
        ArtistAliasImporter().import_all()

        get_all_artist_aliases_mock.assert_called_once()
        all_artist_aliases = db.session.query(ArtistAlias).all()
        assert len(all_artist_aliases) == 4

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistProductLinkQuery.execute")
    @mock.patch("pcapi.connectors.big_query.importer.base.BATCH_SIZE", 2)
    def test_import_all_artist_ignores_missing_products(self, get_all_artists_product_link_mock, caplog):
        artist = ArtistFactory()
        existing_product = ProductFactory()
        get_all_artists_product_link_mock.return_value = [
            ArtistProductLinkModel(
                artist_id=artist.id, product_id=999999999, artist_type=artist_models.ArtistType.AUTHOR.value
            ),
            ArtistProductLinkModel(
                artist_id=artist.id, product_id=existing_product.id, artist_type=artist_models.ArtistType.AUTHOR.value
            ),
        ]

        with caplog.at_level(logging.ERROR):
            ArtistProductLinkImporter().import_all()

        assert 'Key (product_id)=(999999999) is not present in table "product"' in caplog.text
        assert db.session.query(ArtistProductLink).count() == 1


class UpdateArtistsFromDeltaTest:
    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_updates_and_creates_artists(self, mock_artist_delta_query):
        artist_to_delete_id = str(uuid.uuid4())
        artist_to_delete = ArtistFactory(id=artist_to_delete_id)
        new_artist_id = str(uuid.uuid4())
        mock_artist_delta_query.return_value = [
            DeltaArtistModel(id=new_artist_id, action=DeltaAction.ADD, name="Nouvel Artiste"),
            DeltaArtistModel(id=artist_to_delete.id, action=DeltaAction.REMOVE, name="Artist to Delete"),
        ]

        ArtistImporter().run_delta_update()

        assert db.session.query(Artist).filter_by(id=new_artist_id).first() is not None
        assert db.session.query(Artist).filter_by(id=artist_to_delete_id).first() is None
        assert db.session.query(Artist).count() == 1

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistProductLinkDeltaQuery.execute")
    def test_updates_and_creates_artist_product_links(self, mock_link_delta_query):
        artist = ArtistFactory()
        product = ProductFactory()
        product2 = ProductFactory()

        link_to_delete = ArtistProductLinkFactory(
            artist_id=artist.id, product_id=product.id, artist_type=artist_models.ArtistType.AUTHOR
        )
        link_to_keep = ArtistProductLinkFactory(
            artist_id=artist.id, product_id=product.id, artist_type=artist_models.ArtistType.PERFORMER
        )
        link_to_delete_id = link_to_delete.id

        mock_link_delta_query.return_value = [
            DeltaArtistProductLinkModel(
                artist_id=artist.id,
                product_id=product2.id,
                artist_type=artist_models.ArtistType.AUTHOR.value,
                action=DeltaAction.ADD,
            ),
            DeltaArtistProductLinkModel(
                artist_id=link_to_delete.artist_id,
                product_id=link_to_delete.product_id,
                artist_type=artist_models.ArtistType.AUTHOR.value,
                action=DeltaAction.REMOVE,
            ),
        ]

        ArtistProductLinkImporter().run_delta_update()

        assert db.session.query(ArtistProductLink).filter_by(id=link_to_keep.id).first() is not None
        assert (
            db.session.query(ArtistProductLink)
            .filter_by(artist_id=artist.id, product_id=product2.id, artist_type=artist_models.ArtistType.AUTHOR)
            .first()
            is not None
        )
        assert db.session.query(ArtistProductLink).filter_by(id=link_to_delete_id).first() is None
        assert db.session.query(ArtistProductLink).count() == 2

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistAliasDeltaQuery.execute")
    def test_updates_and_creates_artist_aliases(self, mock_alias_delta_query):
        artist = ArtistFactory()
        alias_name_to_delete = "Alias a supprimer"
        offer_category_id = "LIVRE"
        artist_type = artist_models.ArtistType.AUTHOR
        alias_to_keep = ArtistAliasFactory(
            artist_id=artist.id,
            artist_alias_name=alias_name_to_delete,
            offer_category_id="MUSIQUE_LIVE",
            artist_type=artist_type,
        )
        alias_to_delete = ArtistAliasFactory(
            artist_id=artist.id,
            artist_alias_name=alias_name_to_delete,
            offer_category_id=offer_category_id,
            artist_type=artist_type,
        )
        alias_to_delete_id = alias_to_delete.id

        new_alias = "Tout Nouvel Alias"
        mock_alias_delta_query.return_value = [
            DeltaArtistAliasModel(
                artist_id=artist.id,
                artist_alias_name=new_alias,
                offer_category_id=offer_category_id,
                artist_type=artist_type.value,
                action=DeltaAction.ADD,
            ),
            DeltaArtistAliasModel(
                artist_id=artist.id,
                artist_alias_name=alias_name_to_delete,
                offer_category_id=offer_category_id,
                artist_type=artist_type.value,
                action=DeltaAction.REMOVE,
            ),
        ]

        ArtistAliasImporter().run_delta_update()

        assert (
            db.session.query(ArtistAlias)
            .filter_by(
                artist_id=artist.id,
                artist_alias_name=new_alias,
                offer_category_id=offer_category_id,
                artist_type=artist_type,
            )
            .first()
            is not None
        )
        assert db.session.query(ArtistAlias).filter_by(id=alias_to_keep.id).first() is not None
        assert db.session.query(ArtistAlias).filter_by(id=alias_to_delete_id).first() is None
        assert db.session.query(ArtistAlias).count() == 2

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_update_action_modifies_existing_artist(self, mock_artist_delta_query):
        artist_to_update = ArtistFactory(name="Ancien Nom", description="Description initiale")
        initial_artist_count = db.session.query(Artist).count()
        mock_artist_delta_query.return_value = [
            DeltaArtistModel(
                id=artist_to_update.id,
                name="Nouveau Nom",
                description="Description mise à jour",
                action=DeltaAction.UPDATE,
            ),
        ]

        ArtistImporter().run_delta_update()

        assert artist_to_update.name == "Nouveau Nom"
        assert artist_to_update.description == "Description mise à jour"
        assert db.session.query(Artist).count() == initial_artist_count

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistDeltaQuery.execute")
    def test_update_action_does_nothing_for_non_existent_artist(self, mock_artist_delta_query):
        ArtistFactory()
        initial_artist_count = db.session.query(Artist).count()
        non_existent_id = str(uuid.uuid4())
        mock_artist_delta_query.return_value = [
            DeltaArtistModel(id=non_existent_id, name="Artiste Fantôme", action=DeltaAction.UPDATE),
        ]

        ArtistImporter().run_delta_update()

        assert db.session.query(Artist).filter_by(id=non_existent_id).first() is None
        assert db.session.query(Artist).count() == initial_artist_count


class ComputeArtistsMostRelevantImageTest:
    @mock.patch("pcapi.core.artist.commands.async_index_artist_ids")
    def test_compute_artists_most_relevant_image_if_no_image_set(self, mock_async_index_artist):
        artist = ArtistFactory(image=None, computed_image=None)
        product_mediation = offers_factories.ProductMediationFactory()
        ArtistProductLinkFactory(artist_id=artist.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image()

        assert artist.computed_image == product_mediation.url
        mock_async_index_artist.assert_called_once_with([artist.id], reason=IndexationReason.ARTIST_IMAGE_UPDATE)

    def test_process_artists_by_batch(self, app, clear_redis):
        artists = ArtistFactory.create_batch(5, image=None, computed_image=None)
        product_mediation = offers_factories.ProductMediationFactory()
        for artist in artists:
            ArtistProductLinkFactory(artist_id=artist.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image(batch_size=2)

        assert all(artist.computed_image == product_mediation.url for artist in artists)
        app.redis_client.smembers(redis_queues.REDIS_ARTIST_IDS_TO_INDEX) == {artist.id for artist in artists}

    @mock.patch("pcapi.core.artist.commands.async_index_artist_ids")
    def test_update_artists_computed_image_only_if_changed(self, mock_async_index_artist):
        product_mediation = offers_factories.ProductMediationFactory()
        artist_with_update = ArtistFactory(image=None, computed_image="http://another.url.com")
        artist_without_update = ArtistFactory(image=None, computed_image=product_mediation.url)
        ArtistProductLinkFactory(artist_id=artist_with_update.id, product_id=product_mediation.product.id)
        ArtistProductLinkFactory(artist_id=artist_without_update.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image()

        assert artist_with_update.computed_image == product_mediation.url
        assert artist_without_update.computed_image == product_mediation.url
        mock_async_index_artist.assert_called_once_with(
            [artist_with_update.id], reason=IndexationReason.ARTIST_IMAGE_UPDATE
        )

    @mock.patch("pcapi.core.artist.commands.async_index_artist_ids")
    def test_does_nothing_if_image_set(self, mock_async_index_artist):
        artist = ArtistFactory(image="http://example.com")
        product_mediation = offers_factories.ProductMediationFactory()
        ArtistProductLinkFactory(artist_id=artist.id, product_id=product_mediation.product.id)

        commands.compute_artists_most_relevant_image()

        assert artist.computed_image is None
        assert artist.image == "http://example.com"
        mock_async_index_artist.assert_not_called()
