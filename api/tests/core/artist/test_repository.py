import pytest

import pcapi.core.artist.factories as artist_factories
from pcapi.core.artist.repository import get_artist_by_music_platform_id
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


class GetArtistByMusicPlatformIdTest:
    @pytest.mark.parametrize(
        "platform", ["spotify_id", "isni_id", "apple_music_id", "deezer_id", "genius_id", "soundcloud_id"]
    )
    def test_should_find_the_artist_on_every_platform(self, platform):
        artist = artist_factories.ArtistFactory()
        artist_factories.ArtistMusicPlatformFactory(artist=artist, **{platform: "some-platform-id"})

        assert get_artist_by_music_platform_id(platform, "some-platform-id") == artist

    def test_should_return_none_when_the_id_is_unknown(self):
        artist = artist_factories.ArtistFactory()
        artist_factories.ArtistMusicPlatformFactory(artist=artist, spotify_id="known")

        assert get_artist_by_music_platform_id("spotify_id", "unknown") is None

    def test_should_ignore_a_blacklisted_artist(self):
        artist = artist_factories.ArtistFactory(is_blacklisted=True)
        artist_factories.ArtistMusicPlatformFactory(artist=artist, spotify_id="known")

        assert get_artist_by_music_platform_id("spotify_id", "known") is None
