from unittest import mock

import pytest
from factory.faker import faker

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors import youtube
from pcapi.core import testing


Fake = faker.Faker(locale="fr_FR")


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @mock.patch("pcapi.core.offers.api.get_video_metadata_from_cache")
    def test_get_offer_video_metadata(self, get_video_metadata_from_cache_mock, client):
        video_url = "https://www.youtube.com/watch?v=WtM4OW2qVjY"
        get_video_metadata_from_cache_mock.return_value = youtube.YoutubeVideoMetadata(
            id="WtM4OW2qVjY",
            title="Title",
            thumbnail_url="https://example.com/high.jpg",
            duration=100,
        )

        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        test_client = client.with_session_auth(email=user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        with testing.assert_num_queries(num_queries):
            response = test_client.get(f"/get-offer-video-data/?videoUrl={video_url}")
            assert response.status_code == 200
        assert response.json == {
            "id": "WtM4OW2qVjY",
            "title": "Title",
            "thumbnailUrl": "https://example.com/high.jpg",
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

    def test_get_offer_video_metadata_unknown_url(self, client):
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
