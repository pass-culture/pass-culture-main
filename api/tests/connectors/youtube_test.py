from unittest import mock

import pytest

from pcapi.connectors import youtube
from pcapi.connectors.serialization.youtube_serializers import parse_iso8601_duration_to_seconds
from pcapi.utils import requests


class GetVideoMetadataTest:
    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_video_metadata_success(self, mock_requests_get, settings):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "test_video_id",
                    "snippet": {
                        "title": "Test Video",
                        "thumbnails": {
                            "high": {"url": "https://example.com/high.jpg"},
                        },
                    },
                    "contentDetails": {"duration": "PT1M40S"},
                }
            ]
        }
        mock_requests_get.return_value = mock_response

        metadata = youtube.get_video_metadata("test_video_id")

        assert metadata.id == "test_video_id"
        assert metadata.title == "Test Video"
        assert metadata.thumbnail_url == "https://example.com/high.jpg"
        assert metadata.duration == 100
        mock_requests_get.assert_called_once_with(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "id": "test_video_id",
                "key": settings.YOUTUBE_API_KEY,
                "part": "snippet,contentDetails",
            },
        )

    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_video_metadata_api_error(self, mock_requests_get):
        mock_requests_get.side_effect = requests.exceptions.RequestException
        with pytest.raises(requests.ExternalAPIException):
            youtube.get_video_metadata("test_video_id")

    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_video_metadata_no_items(self, mock_requests_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_requests_get.return_value = mock_response

        metadata = youtube.get_video_metadata("test_video_id")
        assert metadata is None

    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_video_metadata_incomplete_data(self, mock_requests_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "1", "snippet": {"title": "Test Video"}}]}
        mock_requests_get.return_value = mock_response

        with pytest.raises(requests.ExternalAPIException):
            youtube.get_video_metadata("test_video_id")


class SerializerTest:
    @pytest.mark.parametrize(
        "duration_str,expected_seconds",
        [
            ("PT1M30S", 90),
            ("PT2H", 7200),
            ("PT45S", 45),
            ("PT1H2M3S", 3723),
        ],
    )
    def test_parse_iso8601_duration(self, duration_str, expected_seconds):
        assert parse_iso8601_duration_to_seconds(duration_str) == expected_seconds

    def test_parse_iso8601_duration_invalid(self):
        with pytest.raises(ValueError):
            parse_iso8601_duration_to_seconds("P1D")
