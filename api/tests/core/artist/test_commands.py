from unittest import mock

import pytest

from pcapi.core.artist import commands
from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistAlias
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory

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

        all_artists = Artist.query.all()
        assert len(all_artists) == 2

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistQuery.execute")
    def test_import_all_artists_creates_artists_is_idempotent(
        self,
        get_all_artists_mock,
    ):
        get_all_artists_mock.return_value = fixtures.big_query_artist_fixture

        commands.import_all_artists()

        get_all_artists_mock.assert_called_once()

        all_artists = Artist.query.all()
        assert len(all_artists) == 2

        get_all_artists_mock.reset_mock()
        commands.import_all_artists()

        get_all_artists_mock.assert_called_once()

        all_artists = Artist.query.all()
        assert len(all_artists) == 2

    @mock.patch("pcapi.connectors.big_query.queries.artist.ArtistProductLinkQuery.execute")
    def test_import_all_artist_product_links_creates_product_links(
        self,
        get_all_artists_product_links_mock,
    ):
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

        commands.import_all_artist_product_links()

        get_all_artists_product_links_mock.assert_called_once()

        author = Artist.query.filter_by(id=author.id).one()
        for product in author.products:
            assert product in books_by_same_artist

        performer = Artist.query.filter_by(id=performer.id).one()
        for product in performer.products:
            assert product in albums_by_same_artist

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

        all_artist_aliases = ArtistAlias.query.all()

        assert len(all_artist_aliases) == 4
