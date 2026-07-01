import json

import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
from pcapi import settings
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")

DS_URL = "https://example.com/recommendation"
DS_SIMILAR_ARTISTS_URL = DS_URL + "/similar_artists/{artist_id}"


def _ds_response(artist_ids: list[str]) -> bytes:
    return json.dumps(
        {
            "similar_artists": [{"artist_id_match": aid, "rank": i + 1} for i, aid in enumerate(artist_ids)],
            "params": {"artist_id": "irrelevant", "call_id": "test-call-id"},
        }
    ).encode()


def _link_artist_to_bookable_offer(artist):
    product = offers_factories.ProductFactory()
    artist_factories.ArtistProductLinkFactory(artist_id=artist.id, product_id=product.id)
    offer = offers_factories.ThingOfferFactory(product=product)
    offers_factories.StockFactory(offer=offer)


@pytest.mark.settings(
    RECOMMENDATION_BACKEND="pcapi.connectors.recommendation.HttpBackend",
    RECOMMENDATION_API_URL=DS_URL,
)
class GetSimilarArtistsTest:
    def test_returns_similar_artists_in_ds_order(self, client, requests_mock):
        first = artist_factories.ArtistFactory(name="First similar")
        second = artist_factories.ArtistFactory(name="Second similar")
        _link_artist_to_bookable_offer(first)
        _link_artist_to_bookable_offer(second)
        source_id = "00000000-0000-0000-0000-000000000001"

        requests_mock.get(
            DS_SIMILAR_ARTISTS_URL.format(artist_id=source_id),
            content=_ds_response([first.id, second.id]),
        )

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert response.json == {
            "artists": [
                {"id": first.id, "name": first.name, "image": first.thumbUrl},
                {"id": second.id, "name": second.name, "image": second.thumbUrl},
            ]
        }

    def test_similar_artist_image_uses_bucket_url_when_mediation_uuid_is_set(self, client, requests_mock):
        similar = artist_factories.ArtistFactory(name="Similar", mediation_uuid="some-mediation-uuid")
        _link_artist_to_bookable_offer(similar)
        source_id = "00000000-0000-0000-0000-000000000001"

        requests_mock.get(
            DS_SIMILAR_ARTISTS_URL.format(artist_id=source_id),
            content=_ds_response([similar.id]),
        )

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        expected_url = f"{settings.OBJECT_STORAGE_URL}/{settings.ARTIST_THUMBS_FOLDER_NAME}/{similar.mediation_uuid}"
        assert response.json["artists"][0]["image"] == expected_url
        assert response.json["artists"][0]["image"] != similar.image

    def test_skips_blacklisted_similar(self, client, requests_mock):
        blacklisted = artist_factories.ArtistFactory(is_blacklisted=True)
        ok_artist = artist_factories.ArtistFactory()
        _link_artist_to_bookable_offer(ok_artist)
        source_id = "00000000-0000-0000-0000-000000000001"

        requests_mock.get(
            DS_SIMILAR_ARTISTS_URL.format(artist_id=source_id),
            content=_ds_response([blacklisted.id, ok_artist.id]),
        )

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert len(response.json["artists"]) == 1
        assert response.json["artists"][0]["id"] == ok_artist.id

    def test_skips_similar_without_eligible_offer(self, client, requests_mock):
        no_offer = artist_factories.ArtistFactory()
        ok_artist = artist_factories.ArtistFactory()
        _link_artist_to_bookable_offer(ok_artist)
        source_id = "00000000-0000-0000-0000-000000000001"

        requests_mock.get(
            DS_SIMILAR_ARTISTS_URL.format(artist_id=source_id),
            content=_ds_response([no_offer.id, ok_artist.id]),
        )

        with assert_num_queries(1):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert len(response.json["artists"]) == 1
        assert response.json["artists"][0]["id"] == ok_artist.id

    def test_empty_when_ds_returns_empty_list(self, client, requests_mock):
        source_id = "00000000-0000-0000-0000-000000000001"

        requests_mock.get(
            DS_SIMILAR_ARTISTS_URL.format(artist_id=source_id),
            content=_ds_response([]),
        )

        with assert_num_queries(0):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert response.json == {"artists": []}

    def test_empty_on_recommendation_api_timeout(self, client, requests_mock):
        from pcapi.utils import requests as pcapi_requests

        source_id = "00000000-0000-0000-0000-000000000001"
        requests_mock.get(
            DS_SIMILAR_ARTISTS_URL.format(artist_id=source_id),
            exc=pcapi_requests.exceptions.Timeout,
        )

        with assert_num_queries(0):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert response.json == {"artists": []}

    def test_empty_on_recommendation_api_error(self, client, requests_mock):
        from pcapi.utils import requests as pcapi_requests

        source_id = "00000000-0000-0000-0000-000000000001"
        requests_mock.get(
            DS_SIMILAR_ARTISTS_URL.format(artist_id=source_id),
            exc=pcapi_requests.exceptions.ConnectionError,
        )

        with assert_num_queries(0):
            response = client.get(f"/native/v1/artists/{source_id}/similar")

        assert response.status_code == 200
        assert response.json == {"artists": []}


def test_returns_400_when_artist_id_is_not_a_uuid(client):
    with assert_num_queries(0):
        response = client.get("/native/v1/artists/not-a-uuid/similar")

    assert response.status_code == 400
