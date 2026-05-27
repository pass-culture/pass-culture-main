import pytest

import pcapi.core.artist.factories as artist_factories
from pcapi.core.artist.repository import get_filtered_artists_for_search


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_filtered_artists_for_search():
    exact_match_artist = artist_factories.ArtistFactory(name="exact_match", pro_search_score=0)
    artist_factories.ArtistFactory(is_blacklisted=True)
    artist_factories.ArtistFactory(wikidata_id=None)
    artist_factories.ArtistFactory(name="inexact_match1", pro_search_score=1)
    artist2 = artist_factories.ArtistFactory(name="inexact_match2", pro_search_score=4)
    artist3 = artist_factories.ArtistFactory(name="inexact_match3", pro_search_score=2)
    artist4 = artist_factories.ArtistFactory(name="inexact_match4", pro_search_score=6)
    artist_factories.ArtistFactory(name="not_exact_match5", pro_search_score=0)

    artists_list = get_filtered_artists_for_search("exact_match")
    assert artists_list == [exact_match_artist, artist4, artist2, artist3]
