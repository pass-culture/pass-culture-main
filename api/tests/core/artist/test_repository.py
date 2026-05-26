import pytest

import pcapi.core.artist.factories as artist_factories
from pcapi.core.artist.repository import get_filtered_artists_for_search


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_filtered_artists_for_search():
    exact_match_artist = artist_factories.ArtistFactory(name="exact_match", pro_search_score=0)
    artist_no_wikidata_id = artist_factories.ArtistFactory(is_blacklisted=True)
    blacklisted_artist = artist_factories.ArtistFactory(wikidata_id=None)
    artist1 = artist_factories.ArtistFactory(name="inexact_match1", pro_search_score=1)
    artist2 = artist_factories.ArtistFactory(name="inexact_match2", pro_search_score=4)
    artist3 = artist_factories.ArtistFactory(name="inexact_match3", pro_search_score=2)
    artist4 = artist_factories.ArtistFactory(name="inexact_match4", pro_search_score=6)
    artist_out_of_range = artist_factories.ArtistFactory(name="not_exact_match5", pro_search_score=0)

    artists_list = get_filtered_artists_for_search("exact_match")
    assert len(artists_list) == 5
    assert artists_list[0] == exact_match_artist

    # check order by pro_search_score
    assert artists_list[1] == artist4
    assert artists_list[2] == artist2
    assert artists_list[3] == artist3
    assert artists_list[4] == artist1

    assert artist1 in artists_list
    assert artist2 in artists_list
    assert artist3 in artists_list
    assert artist4 in artists_list
    assert artist_no_wikidata_id not in artists_list
    assert blacklisted_artist not in artists_list
    assert artist_out_of_range not in artists_list
