import json
from unittest import mock

import pytest
from factory.faker import faker
from flask import current_app

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


Fake = faker.Faker(locale="fr_FR")


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_offer_video_metadata(self, mock_requests_get, client):
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

        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        with testing.assert_num_queries(num_queries):
            response = test_client.get("/get-offer-video-data/?videoUrl=https://www.youtube.com/watch?v=b1kbLwvqugk")
            assert response.status_code == 200
        assert response.json == {
            "id": "test_video_id",
            "title": "Test Video",
            "thumbnailUrl": "https://example.com/high.jpg",
            "duration": 100,
        }
        assert json.loads(current_app.redis_client.get("youtube_video_test_video_id")) == {
            "title": "Test Video",
            "thumbnail_url": "https://example.com/high.jpg",
            "duration": 100,
        }


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_get_offer_video_metadata_url_not_from_youtube(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # rollback (atomic)
        with testing.assert_num_queries(num_queries):
            response = test_client.get(
                "/get-offer-video-data/?videoUrl=https://www.wrong_platform.com/watch?v=b1kbLwvqugk"
            )
            assert response.status_code == 400

    @mock.patch("pcapi.connectors.youtube.requests.get")
    def test_get_offer_video_metadata_unknown_url(self, mock_requests_get, client):
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
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # rollback (atomic)
        with testing.assert_num_queries(num_queries):
            response = test_client.get("/get-offer-video-data/?videoUrl=https://www.youtube.com/watch?v=unknown")
            assert response.status_code == 400

    @mock.patch("pcapi.connectors.youtube.get_video_metadata")
    def test_get_offer_video_metadata_youtube_api_error(self, mock_get_video_metadata, client):
        mock_get_video_metadata.return_value = None

        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # rollback (atomic)
        with testing.assert_num_queries(num_queries):
            response = test_client.get("/get-offer-video-data/?videoUrl=https://www.youtube.com/watch?v=b1kbLwvqugk")
            assert response.status_code == 400
