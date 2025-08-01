import pytest

from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.search import testing
from pcapi.scripts.index_all_artists.main import get_artist_batches
from pcapi.scripts.index_all_artists.main import get_number_of_artists
from pcapi.scripts.index_all_artists.main import index_all_artists


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_number_of_artists():
    ArtistFactory.create_batch(2)

    count = get_number_of_artists()

    assert count == 2


def test_get_artist_batches():
    ArtistFactory.create_batch(5)

    batches = list(get_artist_batches(batch_size=2))

    assert len(batches) == 3


def test_index_all_artists():
    artists = ArtistFactory.create_batch(2)
    index_all_artists(batch_size=2)

    assert len(testing.search_store["artists"]) == 2
    assert testing.search_store["artists"] == {
        artists[0].id: {
            "objectID": artists[0].id,
            "description": artists[0].description,
            "image": artists[0].image,
            "name": artists[0].name,
        },
        artists[1].id: {
            "objectID": artists[1].id,
            "description": artists[1].description,
            "image": artists[1].image,
            "name": artists[1].name,
        },
    }
