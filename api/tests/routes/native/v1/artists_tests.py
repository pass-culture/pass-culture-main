import pcapi.core.artist.factories as artist_factories
from pcapi.core.testing import assert_num_queries


class GetArtistsTest:
    def test_get_artists(self, client):
        artist = artist_factories.ArtistFactory()

        artist_id = artist.id
        nb_queries = 1
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")
            assert response.status_code == 200

        assert response.json["id"] == artist.id
        assert response.json["name"] == artist.name

    def test_get_artists_do_not_exist(self, client):
        _ = artist_factories.ArtistFactory()

        artist_id = "123-test-3a2b"
        nb_queries = 1
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/artists/{artist_id}")
            assert response.status_code == 404
