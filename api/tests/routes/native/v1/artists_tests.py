import pytest

import pcapi.core.artist.factories as artist_factories
from pcapi.core.testing import assert_num_queries


pytest.mark.usefixtures("db_session")


class GetArtistsTest:
    def test_get_artist(self, client):
        artist = artist_factories.ArtistFactory()

        artist_id = artist.id
        nb_queries = 1  # artist
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 200
        assert response.json["id"] == artist.id
        assert response.json["name"] == artist.name
        assert response.json["description"] == artist.description
        assert response.json["image"] == artist.image

    def test_get_artist_with_none_fields(self, client):
        artist = artist_factories.ArtistFactory(description=None, image=None)

        artist_id = artist.id
        nb_queries = 1  # artist
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 200
        assert response.json["id"] == artist.id
        assert response.json["name"] == artist.name
        assert response.json["description"] is None
        assert response.json["image"] is None

    def test_get_artist_with_llm_biography_and_wikipedia_url(self, client):
        artist = artist_factories.ArtistFactory(
            biography="pretty biography",
            description="description",
            wikipedia_url="https://fr.wikipedia.org/wiki/Artist",
        )

        artist_id = artist.id
        nb_queries = 1  # artist
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 200
        assert response.json["description"] == "pretty biography"
        assert response.json["descriptionCredit"] == "© Contenu généré par IA \u2728"
        assert response.json["descriptionSource"] == "https://fr.wikipedia.org/wiki/Artist"

    def test_get_artist_with_llm_biography_without_wikipedia_url(self, client):
        artist = artist_factories.ArtistFactory(
            biography="pretty biography",
            description="description",
            wikipedia_url=None,
        )

        artist_id = artist.id
        nb_queries = 1  # artist
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 200
        assert response.json["description"] == "pretty biography"
        assert response.json["descriptionCredit"] == "© Contenu généré par IA \u2728"
        assert response.json["descriptionSource"] is None

    def test_get_artist_returns_no_credit_or_source_if_biography_is_empty(self, client):
        artist = artist_factories.ArtistFactory(
            biography=None,
            description="description",
            wikipedia_url="https://fr.wikipedia.org/wiki/Artist",
        )

        artist_id = artist.id
        nb_queries = 1  # artist
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 200
        assert response.json["description"] == "description"
        assert response.json["descriptionCredit"] is None
        assert response.json["descriptionSource"] is None

    def test_get_non_existent_artist(self, client):
        artist_id = "123-test-3a2b"
        nb_queries = 1
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 404

    def test_get_blacklisted_artist(self, client):
        artist = artist_factories.ArtistFactory(is_blacklisted=True)

        artist_id = artist.id
        nb_queries = 1  # artist
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 404
