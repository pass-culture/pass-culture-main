from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class IsAlgoliaIndexingTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_on_name_are_triggered(self, mocked_add_venue_id, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory(user__email="patch_venue_algolia_test@example.com")
        user = user_offerer.user
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            name="old names",
            publicName="old name",
            city="old City",
        )
        json_data = {"name": "my new name"}
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        auth_request.patch("/venues/%s" % humanize(venue.id), json=json_data)

        # Then
        assert mocked_add_venue_id.called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_on_public_name_are_triggered(self, mocked_add_venue_id, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory(user__email="patch_venue_algolia_test@example.com")
        user = user_offerer.user
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            name="old names",
            publicName="old name",
            city="old City",
        )
        json_data = {"publicName": "my new name"}
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        auth_request.patch("/venues/%s" % humanize(venue.id), json=json_data)

        # Then
        assert mocked_add_venue_id.called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_on_city_are_triggered(self, mocked_add_venue_id, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory(user__email="patch_venue_algolia_test@example.com")
        user = user_offerer.user
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            name="old names",
            publicName="old name",
            city="old City",
        )
        json_data = {"city": "My new city"}
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        auth_request.patch("/venues/%s" % humanize(venue.id), json=json_data)

        # Then
        assert mocked_add_venue_id.called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_are_not_on_algolia_fields_it_should_return_false(self, mocked_add_venue_id, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory(user__email="patch_venue_algolia_test@example.com")
        user = user_offerer.user
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            name="old names",
            publicName="old name",
            city="old City",
        )
        json_data = {"siret": "7896542311234", "banana": None}
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        auth_request.patch("/venues/%s" % humanize(venue.id), json=json_data)

        # Then
        assert mocked_add_venue_id.not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_in_payload_are_same_as_previous_it_should_return_false(self, mocked_add_venue_id, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory(user__email="patch_venue_algolia_test@example.com")
        user = user_offerer.user
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            name="old names",
            publicName="old name",
            city="old City",
        )
        json_data = {"city": "old City"}
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        auth_request.patch("/venues/%s" % humanize(venue.id), json=json_data)

        # Then
        assert mocked_add_venue_id.not_called()
