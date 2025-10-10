import json

import pytest

from pcapi.core.videos import api
from pcapi.utils.requests import ExternalAPIException


@pytest.mark.usefixtures("db_session")
class VideoIdExtractionTest:
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
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", None),  # we do not accept shorts
            ("https://www.other.com", None),
            ("dQw4w9WgXcQ", None),
            ("https://www.youtube.com/@Msnight_fall", None),  # we do not accept channels
            ("https://www.youtube.com.jesuiscool.fr", None),  # we do not accept subdomains, even if you are cool
            ("https://www.youtube.comjesuisunvilainhacker", None),  # we do not accept hackers
            ("m.youtube.com/watch?v=dQw4w9WgXcQ", None),  # we require https://
            ("www.youtube.com/embed/dQw4w9WgXcQ", None),
            ("youtube.com/v/dQw4w9WgXcQ", None),
            ("ghtps://www.youtube.com/watch?v=dQw4w9WgXcQ", None),
        ],
    )
    def test_extract_youtube_video_id_from_url(self, url, video_id):
        assert api.extract_video_id(url) == video_id


@pytest.mark.usefixtures("db_session")
class GetVideoMetadataFromCacheTest:
    VIDEO_ID = "WtM4OW2qVjY"

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeExceptionBackend")
    def test_get_video_metadata_from_cache_with_data_in_cache(self, app):
        video_url = f"https://www.youtube.com/watch?v={self.VIDEO_ID}"
        video_id = api.extract_video_id(video_url)
        app.redis_client.set(
            f"{api.YOUTUBE_INFO_CACHE_PREFIX}{video_id}",
            json.dumps(
                {
                    "title": "Title",
                    "thumbnail_url": "thumbnail url",
                    "duration": 100,
                }
            ),
        )
        video_metadata = api.get_video_metadata_from_cache(video_url)
        assert video_metadata.id == video_id
        assert video_metadata.title == "Title"
        assert video_metadata.thumbnail_url == "thumbnail url"
        assert video_metadata.duration == 100

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeTestingBackend")
    def test_get_video_metadata_from_cache_without_data_in_cache(self):
        video_url = f"https://www.youtube.com/watch?v={self.VIDEO_ID}"

        video_metadata = api.get_video_metadata_from_cache(video_url)
        assert video_metadata.id == self.VIDEO_ID
        assert video_metadata.title == "Mock Video Title"
        assert video_metadata.thumbnail_url == f"https://example.com/vi/{self.VIDEO_ID}/default.jpg"
        assert video_metadata.duration == 300

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeExceptionBackend")
    def test_get_video_metadata_from_cache_without_data_in_cache_connector_raise_error(self):
        video_url = "https://www.youtube.com/watch?v=WtM4OW2qVjY"

        with pytest.raises(ExternalAPIException):
            api.get_video_metadata_from_cache(video_url)
