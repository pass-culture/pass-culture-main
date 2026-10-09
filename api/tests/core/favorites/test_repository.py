import pytest

from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.favorites import factories
from pcapi.core.favorites import repository
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.users.factories import UserFactory


pytestmark = pytest.mark.usefixtures("db_session")


class FavoriteOffersTest:
    def test_get_favorite_offer(self):
        user = UserFactory()
        offer = OfferFactory()
        favorite = factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        favs_from_db = repository.get_favorite_offers_for(user)

        assert len(favs_from_db) == 1
        assert favs_from_db[0].favorite.offer.id == favorite.offer.id

    def test_insert_favorite_offer(self):
        user = UserFactory()
        offer = OfferFactory()

        repository.create_favorite_offer(user, offer)

        favs_from_db = repository.get_favorite_offers_for(user)

        assert len(favs_from_db) == 1
        assert favs_from_db[0].favorite.offer.id == offer.id

    def test_delete_favorite_offer(self):
        user = UserFactory()
        offer = OfferFactory()
        offer2 = OfferFactory()
        favorite = factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        factories.FavoriteOfferFactory(
            user=user,
            offer=offer2,
        )

        favs_from_db = repository.get_favorite_offers_for(user)
        assert len(favs_from_db) == 2

        repository.delete_favorite("offer", favorite.id)

        favs_from_db = repository.get_favorite_offers_for(user)
        assert len(favs_from_db) == 1

    def test_should_upsert_on_re_insert(self):
        user = UserFactory()
        offer = OfferFactory()

        favorite, is_inserted = repository.create_favorite_offer(user, offer)
        assert favorite is not None
        assert is_inserted is True

        favorite_2, is_inserted = repository.create_favorite_offer(user, offer)
        assert favorite.id == favorite_2.id
        assert is_inserted is False


class FavoriteArtistTest:
    def test_get_favorite_artist(self):
        user = UserFactory()
        artist = ArtistFactory()
        favorite = factories.FavoriteArtistFactory(
            user=user,
            artist=artist,
        )

        favs_from_db = repository.get_favorite_artists_for(user)

        assert len(favs_from_db) == 1
        assert favs_from_db[0].id == favorite.artist.id

    def test_insert_favorite_artist(self):
        user = UserFactory()
        artist = ArtistFactory()

        repository.create_favorite_artist(user, artist)

        favs_from_db = repository.get_favorite_artists_for(user)

        assert len(favs_from_db) == 1
        assert favs_from_db[0].id == artist.id

    def test_delete_favorite_artist(self):
        user = UserFactory()
        artist = ArtistFactory()
        artist2 = ArtistFactory()
        favorite = factories.FavoriteArtistFactory(
            user=user,
            artist=artist,
        )

        factories.FavoriteArtistFactory(
            user=user,
            artist=artist2,
        )

        favs_from_db = repository.get_favorite_artists_for(user)
        assert len(favs_from_db) == 2

        repository.delete_favorite("artist", favorite.id)

        favs_from_db = repository.get_favorite_artists_for(user)
        assert len(favs_from_db) == 1

    def test_should_upsert_on_re_insert(self):
        user = UserFactory()
        artist = ArtistFactory()

        favorite, is_inserted = repository.create_favorite_artist(user, artist)
        assert favorite is not None
        assert is_inserted is True

        favorite_2, is_inserted = repository.create_favorite_artist(user, artist)
        assert favorite.id == favorite_2.id
        assert is_inserted is False
