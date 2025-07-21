import pcapi.core.artist.factories as artist_factories
from pcapi.core.testing import assert_num_queries


class GetArtistsTest:
    def test_get_artist(self, client):
        artist = artist_factories.ArtistFactory()

        artist_id = artist.id
        nb_queries = 1
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
        nb_queries += 1  # product mediation
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")

        assert response.status_code == 200
        assert response.json["id"] == artist.id
        assert response.json["name"] == artist.name
        assert response.json["description"] is None
        assert response.json["image"] is None

    def test_get_non_existent_artist(self, client):
        _ = artist_factories.ArtistFactory()

        artist_id = "123-test-3a2b"
        nb_queries = 1
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")
            assert response.status_code == 404
