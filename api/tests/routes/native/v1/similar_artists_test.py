import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


def _link_artist_to_bookable_offer(artist: artist_models.Artist) -> None:
    product = offers_factories.ProductFactory()
    artist_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=product.id)
    offer = offers_factories.ThingOfferFactory(product=product)
    offers_factories.StockFactory(offer=offer)


class GetSimilarArtistsTest:
    def test_returns_similar_artists_ordered(self, client):
        source = artist_factories.ArtistFactory()
        first = artist_factories.ArtistFactory(name="First similar")
        second = artist_factories.ArtistFactory(name="Second similar")
        _link_artist_to_bookable_offer(first)
        _link_artist_to_bookable_offer(second)
        artist_factories.ArtistSimilarArtistFactory(
            source_artist=source,
            target_artist=second,
            similarity_rank=1,
        )
        artist_factories.ArtistSimilarArtistFactory(
            source_artist=source,
            target_artist=first,
            similarity_rank=2,
        )
        source_id = source.id
        expected_artists = [
            {"id": second.id, "name": second.name, "image": second.thumbUrl},
            {"id": first.id, "name": first.name, "image": first.thumbUrl},
        ]

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert response.json == {"artists": expected_artists}

    def test_skips_blacklisted_similar(self, client):
        source = artist_factories.ArtistFactory()
        blacklisted = artist_factories.ArtistFactory(is_blacklisted=True)
        ok_similar = artist_factories.ArtistFactory()
        _link_artist_to_bookable_offer(ok_similar)
        artist_factories.ArtistSimilarArtistFactory(
            source_artist=source,
            target_artist=blacklisted,
            similarity_rank=1,
        )
        artist_factories.ArtistSimilarArtistFactory(
            source_artist=source,
            target_artist=ok_similar,
            similarity_rank=2,
        )
        source_id = source.id
        expected_id = ok_similar.id

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert len(response.json["artists"]) == 1
        assert response.json["artists"][0]["id"] == expected_id

    def test_skips_similar_without_eligible_offer(self, client):
        source = artist_factories.ArtistFactory()
        no_offer = artist_factories.ArtistFactory()
        ok_similar = artist_factories.ArtistFactory()
        _link_artist_to_bookable_offer(ok_similar)
        artist_factories.ArtistSimilarArtistFactory(
            source_artist=source,
            target_artist=no_offer,
            similarity_rank=1,
        )
        artist_factories.ArtistSimilarArtistFactory(
            source_artist=source,
            target_artist=ok_similar,
            similarity_rank=2,
        )
        source_id = source.id
        expected_id = ok_similar.id

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert len(response.json["artists"]) == 1
        assert response.json["artists"][0]["id"] == expected_id

    def test_empty_when_no_similar_rows(self, client):
        source = artist_factories.ArtistFactory()
        source_id = source.id

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert response.json == {"artists": []}

    def test_empty_when_source_missing(self, client):
        with assert_num_queries(1):
            response = client.get("/native/v1/artists/non-existent-id/similar")

        assert response.status_code == 200
        assert response.json == {"artists": []}

    def test_empty_when_source_blacklisted(self, client):
        source = artist_factories.ArtistFactory(is_blacklisted=True)
        similar = artist_factories.ArtistFactory()
        _link_artist_to_bookable_offer(similar)
        artist_factories.ArtistSimilarArtistFactory(
            source_artist=source,
            target_artist=similar,
            similarity_rank=1,
        )
        source_id = source.id

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert response.json == {"artists": []}
