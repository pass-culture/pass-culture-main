from unittest.mock import patch

import pytest

from pcapi import settings
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class VenueBannerTest:
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_delete_banner(self, mock_search_async_index_venue_ids, mock_delete_public_object, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        timestamp = 1602720000
        expected_thumb_base_path = f"{venue.thumb_path_component}/{humanize(venue.id)}_{timestamp}"
        venue.bannerUrl = f"{settings.OBJECT_STORAGE_URL}/{expected_thumb_base_path}"

        expected_original_thumb_base_path = f"{venue.thumb_path_component}/{humanize(venue.id)}_{timestamp + 1}"
        venue.bannerMeta = {"original_image_url": f"{settings.OBJECT_STORAGE_URL}/{expected_original_thumb_base_path}"}

        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete(f"/venues/{humanize(venue.id)}/banner")
        assert response.status_code == 204

        assert mock_delete_public_object.call_args_list == [
            (("thumbs", expected_thumb_base_path),),
            (("thumbs", expected_original_thumb_base_path),),
        ]

        mock_search_async_index_venue_ids.assert_called_once_with([venue.id])

    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_delete_banner_legacy_url(self, mock_search_async_index_venue_ids, mock_delete_public_object, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        expected_thumb_base_path = f"{venue.thumb_path_component}/{humanize(venue.id)}"
        venue.bannerUrl = f"{settings.OBJECT_STORAGE_URL}/{expected_thumb_base_path}"
        venue.bannerMeta = {}

        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete(f"/venues/{humanize(venue.id)}/banner")
        assert response.status_code == 204

        mock_delete_public_object.assert_called_once_with("thumbs", expected_thumb_base_path)

        mock_search_async_index_venue_ids.assert_called_once_with([venue.id])

    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    def test_delete_no_banner(self, mock_delete_public_object, client):
        """
        Test that an API call to delete a venue's banner works even if
        the venue does not have any (DELETE method must be idempotent)
        """
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, bannerUrl=None)

        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete(f"/venues/{humanize(venue.id)}/banner")
        assert response.status_code == 204

        mock_delete_public_object.assert_not_called()

    def test_unknown_venue(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete("/venues/AZERTYUIOP1234567890/banner")
        assert response.status_code == 404

    @patch("pcapi.core.offerers.api.delete_venue_banner")
    def test_no_access_rights(self, mock_delete_venue_banner, client):
        user = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory()  # user has no rights to do anything with this venue

        client = client.with_session_auth(email=user.user.email)

        response = client.delete(f"/venues/{humanize(venue.id)}/banner")
        assert response.status_code == 403

        mock_delete_venue_banner.assert_not_called()
