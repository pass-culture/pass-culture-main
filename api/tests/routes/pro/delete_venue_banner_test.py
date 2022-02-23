from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class VenueBannerTest:
    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    def test_delete_banner(self, mock_delete_public_object, client):
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete(f"/venues/{humanize(venue.id)}/banner")
        assert response.status_code == 204

        mock_delete_public_object.assert_called_once()

    @patch("pcapi.core.object_storage.backends.local.LocalBackend.delete_public_object")
    def test_delete_no_banner(self, mock_delete_public_object, client):
        """
        Test that an API call to delete a venue's banner works even if
        the venue does not have any (DELETE method must be idempotent)
        """
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer, bannerUrl=None)

        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete(f"/venues/{humanize(venue.id)}/banner")
        assert response.status_code == 204

        mock_delete_public_object.assert_not_called()

    def test_unknown_venue(self, client):
        user_offerer = offers_factories.UserOffererFactory()
        client = client.with_session_auth(email=user_offerer.user.email)

        response = client.delete("/venues/AZERTYUIOP1234567890/banner")
        assert response.status_code == 404
