import pytest

from pcapi.core.videos import exceptions as videos_exceptions
from pcapi.core.videos import platforms as videos_platforms


TEST_VIDEO_ID = "YnBs1MuGSAA"


@pytest.mark.usefixtures("db_session")
class GetPlatformTest:
    def test_get_platform_names(self):
        available_platforms = videos_platforms.get_supported_platform_names()
        assert available_platforms == [videos_platforms.YouTubePlatform.display_name]

    @pytest.mark.parametrize(
        "video_url,expected_platform",
        [
            (f"https://www.youtube.com/watch?v={TEST_VIDEO_ID}", videos_platforms.YouTubePlatform),
            (f"https://youtu.be/f{TEST_VIDEO_ID}", videos_platforms.YouTubePlatform),
        ],
    )
    def test_get_platform_for_url(self, video_url, expected_platform):
        platform = videos_platforms.get_platform_for_url(video_url)
        assert isinstance(platform, expected_platform)

    @pytest.mark.parametrize(
        "video_url",
        [
            "https://vimeo.com/1078258590",
            "https://www.other.com",
            "dQw4w9WgXcQ",
            "https://www.youtube.comjesuisunvilainhacker",  # we do not accept hackers
            "m.youtube.com/watch?v=dQw4w9WgXcQ",  # we require https://
            "www.youtube.com/embed/dQw4w9WgXcQ",
            "youtube.com/v/dQw4w9WgXcQ",
            "ghtps://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ],
    )
    def test_get_unsupported_platform_for_url_should_raise(self, video_url):
        with pytest.raises(videos_exceptions.UnsupportedVideoUrlError) as error:
            videos_platforms.get_platform_for_url(video_url)
        assert (
            str(error.value)
            == "L'URL vidéo n'est pas supportée. Veuillez utiliser une URL d'une des plateformes suivantes : YouTube"
        )


class YouTubePlatformTest:
    @pytest.mark.parametrize(
        "url,video_id",
        [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("http://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
            ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/e/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLUMRshJ8e2c4oQ60D4Ew15A1LgN5C7Y3X", "dQw4w9WgXcQ"),
        ],
    )
    def test_extract_video_id_from_url(self, url, video_id):
        assert videos_platforms.YouTubePlatform.get_video_id(url) == video_id

    @pytest.mark.parametrize(
        "url,exception",
        [
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ"),  # we do not accept shorts
            ("https://www.youtube.com/@Msnight_fall",),  # we do not accept channels
            ("https://www.youtube.com.jesuiscool.fr",),  # we do not accept subdomains, even if you are cool
        ],
    )
    def test_extract_video_id_from_unsupported_url_should_fail(self, url, exception):
        with pytest.raises(videos_exceptions.InvalidYoutubeVideoUrl):
            videos_platforms.YouTubePlatform.get_video_id(url)

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeTestingBackend")
    def test_fetch_metadata(self):
        youtube_platform = videos_platforms.YouTubePlatform()
        video_metadata = youtube_platform.fetch_metadata(TEST_VIDEO_ID)
        assert video_metadata.id == TEST_VIDEO_ID
        assert video_metadata.title == "Mock Video Title"
        assert video_metadata.thumbnail_url == f"https://example.com/vi/{TEST_VIDEO_ID}/default.jpg"
        assert video_metadata.duration == 300

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeNotFoundBackend")
    def test_fetch_metadata_not_found_should_raise(self):
        youtube_platform = videos_platforms.YouTubePlatform()
        with pytest.raises(videos_exceptions.YoutubeVideoNotFound):
            youtube_platform.fetch_metadata(TEST_VIDEO_ID)
