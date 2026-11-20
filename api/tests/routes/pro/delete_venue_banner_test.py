from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi import settings
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.search.models import IndexationReason
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class VenueBannerTest:
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_delete_banner(self, mock_search_async_index_venue_ids, mock_delete_public_object, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, venueTypeCode=VenueTypeCode.LIBRARY
        )

        timestamp = 1602720000
        expected_thumb_base_path = f"{venue.thumb_path_component}/{humanize(venue.id)}_{timestamp}"
        venue.bannerUrl = f"{settings.OBJECT_STORAGE_URL}/{expected_thumb_base_path}"

        expected_original_thumb_base_path = f"{venue.thumb_path_component}/{humanize(venue.id)}_{timestamp + 1}"
        original_image_url = f"{settings.OBJECT_STORAGE_URL}/{expected_original_thumb_base_path}"
        venue.bannerMeta = {"image_credit": "Photographe", "original_image_url": original_image_url}

        client = client.with_session_auth(email=user_offerer.user.email)
        offerer_url = f"/offerers/{user_offerer.offerer.id}"

        offerer_response = client.get(offerer_url)
        assert offerer_response.status_code == 200
        [managed_venue] = offerer_response.json["managedVenues"]
        assert managed_venue["id"] == venue.id
        assert managed_venue["bannerUrl"] == venue.bannerUrl
        assert managed_venue["bannerMeta"]["original_image_url"] == original_image_url

        response = client.delete(f"/venues/{venue.id}/banner")
        assert response.status_code == 204

        venue_response = client.get(f"/venues/{venue.id}")
        assert venue_response.status_code == 200
        assert venue_response.json["bannerUrl"] is None
        assert venue_response.json["bannerMeta"] is None

        offerer_response = client.get(offerer_url)
        assert offerer_response.status_code == 200
        [managed_venue] = offerer_response.json["managedVenues"]
        assert managed_venue["id"] == venue.id
        assert managed_venue["bannerUrl"] is None
        assert managed_venue["bannerMeta"] is None

        assert mock_delete_public_object.call_args_list == [
            (("thumbs", expected_thumb_base_path),),
            (("thumbs", expected_original_thumb_base_path),),
        ]

        mock_search_async_index_venue_ids.assert_called_once_with(
            [venue.id],
            reason=IndexationReason.VENUE_BANNER_DELETION,
        )

    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_delete_banner_legacy_url(self, mock_search_async_index_venue_ids, mock_delete_public_object, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        expected_thumb_base_path = f"{venue.thumb_path_component}/{humanize(venue.id)}"
        venue.bannerUrl = f"{settings.OBJECT_STORAGE_URL}/{expected_thumb_base_path}"
        venue.bannerMeta = {}

        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete(f"/venues/{venue.id}/banner")
        assert response.status_code == 204

        mock_delete_public_object.assert_called_once_with("thumbs", expected_thumb_base_path)

        mock_search_async_index_venue_ids.assert_called_once_with(
            [venue.id],
            reason=IndexationReason.VENUE_BANNER_DELETION,
        )

    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    def test_delete_no_banner(self, mock_delete_public_object, client):
        """
        Test that an API call to delete a venue's banner works even if
        the venue does not have any (DELETE method must be idempotent)
        """
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, venueTypeCode=VenueTypeCode.LIBRARY, bannerUrl=None
        )

        client = client.with_session_auth(email=user_offerer.user.email)

        venue_url = f"/venues/{venue.id}"
        response = client.get(venue_url)
        assert response.status_code == 200
        assert response.json["bannerUrl"] is None
        assert response.json["bannerMeta"] is None
        assert "/assets/venue_default_images/" in venue.bannerUrl

        for _ in range(2):
            response = client.delete(f"{venue_url}/banner")
            assert response.status_code == 204

        response = client.get(venue_url)
        assert response.status_code == 200
        assert response.json["bannerUrl"] is None
        assert response.json["bannerMeta"] is None

        mock_delete_public_object.assert_not_called()

    def test_unknown_venue(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete("/venues/1234/banner")
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    @patch("pcapi.core.offerers.api.delete_venue_banner")
    def test_no_access_rights(self, mock_delete_venue_banner, client):
        user = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory()  # user has no rights to do anything with this venue

        client = client.with_session_auth(email=user.user.email)

        response = client.delete(f"/venues/{venue.id}/banner")
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

        mock_delete_venue_banner.assert_not_called()
