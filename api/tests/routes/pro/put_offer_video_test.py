from unittest import mock

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors import youtube
from pcapi.core.offerers import models as offerers_models
from pcapi.core.videos import exceptions as videos_exceptions
from pcapi.utils.requests import ExternalAPIException


pytestmark = pytest.mark.usefixtures("db_session")

YOUTUBE_VIDEO_ID = "uy5z7jiDmlg"
YOUTUBE_VIDEO_URL = f"https://www.youtube.com/watch?v={YOUTUBE_VIDEO_ID}"


class Returns200Test:
    endpoint = "/offers/{offer_id}/video"

    @mock.patch("pcapi.core.videos.api.get_video_metadata_from_cache")
    def test_add_video_to_offer(self, mock_get_metadata, client):
        mock_get_metadata.return_value = youtube.YoutubeVideoMetadata(
            id=YOUTUBE_VIDEO_ID,
            title="title",
            thumbnail_url=f"https://example.com/vi/{YOUTUBE_VIDEO_ID}/default.jpg",
            duration=300,
        )
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        response = client.with_session_auth("user@example.com").put(
            self.endpoint.format(offer_id=offer.id), json={"videoUrl": YOUTUBE_VIDEO_URL}
        )

        assert response.status_code == 200
        assert response.json == {
            "videoDuration": 300,
            "videoExternalId": YOUTUBE_VIDEO_ID,
            "videoTitle": "title",
            "videoThumbnailUrl": f"https://example.com/vi/{YOUTUBE_VIDEO_ID}/default.jpg",
            "videoUrl": YOUTUBE_VIDEO_URL,
        }

    def test_remove_video_from_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.OfferMetaDataFactory(
            offer=offer,
            videoUrl=YOUTUBE_VIDEO_URL,
            videoExternalId=YOUTUBE_VIDEO_ID,
            videoTitle="title",
            videoThumbnailUrl=f"https://example.com/vi/{YOUTUBE_VIDEO_ID}/default.jpg",
            videoDuration=300,
        )

        response = client.with_session_auth("user@example.com").put(
            self.endpoint.format(offer_id=offer.id), json={"videoUrl": ""}
        )

        assert response.status_code == 200
        assert response.json == {
            "videoDuration": None,
            "videoExternalId": None,
            "videoTitle": None,
            "videoThumbnailUrl": None,
            "videoUrl": None,
        }


class Returns400Test:
    endpoint = "/offers/{offer_id}/video"

    def test_url_not_from_youtube(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        response = client.with_session_auth("user@example.com").put(
            self.endpoint.format(offer_id=offer.id), json={"videoUrl": "https://vimeo.com/123456789"}
        )

        assert response.status_code == 400
        assert response.json["videoUrl"] == [
            "Veuillez renseigner une URL provenant de la plateforme Youtube. Les shorts et les chaînes ne sont pas acceptées."
        ]

    @mock.patch("pcapi.core.videos.api.get_video_metadata_from_cache", side_effect=ExternalAPIException(True))
    def test_external_api_error(self, mock_get_metadata, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        response = client.with_session_auth("user@example.com").put(
            self.endpoint.format(offer_id=offer.id), json={"videoUrl": YOUTUBE_VIDEO_URL}
        )

        assert response.status_code == 400
        assert response.json["videoUrl"] == ["Nous rencontrons des problèmes de serveur, veuillez réessayer plus tard"]

    @mock.patch(
        "pcapi.core.videos.api.get_video_metadata_from_cache", side_effect=videos_exceptions.YoutubeVideoNotFound()
    )
    def test_youtube_video_not_found(self, mock_get_metadata, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        response = client.with_session_auth("user@example.com").put(
            self.endpoint.format(offer_id=offer.id), json={"videoUrl": YOUTUBE_VIDEO_URL}
        )

        assert response.status_code == 400
        assert response.json["videoUrl"] == ["URL Youtube non trouvée, vérifiez si votre vidéo n’est pas en privé."]


class Returns403Test:
    endpoint = "/offers/{offer_id}/video"

    def test_error_if_venue_is_closed(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, state=offerers_models.VenueState.CLOSED
        )
        offer = offers_factories.OfferFactory(venue=venue)

        response = client.with_session_auth("user@example.com").put(
            self.endpoint.format(offer_id=offer.id), json={"videoUrl": YOUTUBE_VIDEO_URL}
        )

        assert response.status_code == 403


class Returns404Test:
    endpoint = "/offers/{offer_id}/video"

    def test_offer_not_found(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        response = client.with_session_auth("user@example.com").put(
            self.endpoint.format(offer_id=0), json={"videoUrl": YOUTUBE_VIDEO_URL}
        )

        assert response.status_code == 404

    def test_user_has_no_access_to_offerer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        users_factories.UserFactory(email="no-access@example.com")

        response = client.with_session_auth("no-access@example.com").put(
            self.endpoint.format(offer_id=offer.id), json={"videoUrl": YOUTUBE_VIDEO_URL}
        )

        assert response.status_code == 404
