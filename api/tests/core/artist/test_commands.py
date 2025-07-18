import logging
import uuid
from unittest import mock

import pytest

import pcapi.core.artist.models as artist_models
from pcapi.connectors.big_query.queries.artist import ArtistProductLinkModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistAliasModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistModel
from pcapi.connectors.big_query.queries.artist import DeltaArtistProductLinkModel
from pcapi.core.artist import commands
from pcapi.core.artist.commands import DeltaAction
from pcapi.core.artist.factories import ArtistAliasFactory
from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.artist.factories import ArtistProductLinkFactory
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistAlias
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory
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

        commands.import_all_artists()

        get_all_artists_mock.assert_called_once()

        all_artists = db.session.query(Artist).all()
        assert len(all_artists) == 2

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistQuery.execute")
    def test_import_all_artists_creates_artists_is_idempotent(
        self,
        get_all_artists_mock,
    ):
        get_all_artists_mock.return_value = fixtures.big_query_artist_fixture

        commands.import_all_artists()

        get_all_artists_mock.assert_called_once()

        all_artists = db.session.query(Artist).all()
        assert len(all_artists) == 2

        get_all_artists_mock.reset_mock()
        commands.import_all_artists()

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
            commands.import_all_artist_product_links()

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

        commands.import_all_artists()
        commands.import_all_artist_aliases()

        get_all_artist_aliases_mock.assert_called_once()

        all_artist_aliases = db.session.query(ArtistAlias).all()

        assert len(all_artist_aliases) == 4

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistProductLinkQuery.execute")
    @mock.patch("pcapi.core.artist.commands.BATCH_SIZE", 2)
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

        with caplog.at_level(logging.INFO):
            commands.import_all_artist_product_links()

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
            DeltaArtistModel(id=artist_to_delete.id, action=DeltaAction.REMOVE),
        ]

        commands.UpdateArtists().run_delta_update()

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

        commands.UpdateArtistProductLinks().run_delta_update()

        assert db.session.query(ArtistProductLink).filter_by(id=link_to_keep.id).first() is not None
        assert (
            db.session.query(ArtistProductLink)
            .filter_by(artist_id=artist.id, product_id=product2.id, artist_type=artist_models.ArtistType.AUTHOR)
            .first()
            is not None
        )
        assert db.session.query(ArtistProductLink).filter_by(id=link_to_delete_id).first() is None
        assert db.session.query(ArtistProductLink).count() == 2

    @mock.patch("pcapi.core.artist.commands.ArtistAliasDeltaQuery.execute")
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

        commands.UpdateArtistAliases().run_delta_update()

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
