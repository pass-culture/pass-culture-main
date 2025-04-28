import logging
from unittest import mock

import pytest

from pcapi.connectors.big_query.queries.artist import ArtistProductLinkModel
from pcapi.core.artist import commands
from pcapi.core.artist.factories import ArtistFactory
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
            product_ids=[album.id for album in books_by_same_artist], artist_id=author.id, artist_type="AUTHOR"
        ) + fixtures.build_big_query_artist_product_link_fixture(
            product_ids=[album.id for album in albums_by_same_artist],
            artist_id=performer.id,
            artist_type="PERFORMER",
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
            ArtistProductLinkModel(artist_id=artist.id, product_id=999999999, artist_type="AUTHOR"),
            ArtistProductLinkModel(artist_id=artist.id, product_id=existing_product.id, artist_type="AUTHOR"),
        ]

        with caplog.at_level(logging.INFO):
            commands.import_all_artist_product_links()

        assert 'Key (product_id)=(999999999) is not present in table "product"' in caplog.text
        assert db.session.query(ArtistProductLink).count() == 1
