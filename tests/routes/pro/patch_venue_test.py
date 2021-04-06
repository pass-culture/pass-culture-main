from unittest.mock import patch

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.models import Venue
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200:
    @pytest.mark.usefixtures("db_session")
    def test_should_update_venue(self, app):
        # given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )

        venue_type = offers_factories.VenueTypeFactory(label="Musée")
        venue_label = offers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        venue_id = venue.id

        # when
        response = auth_request.patch(
            "/venues/%s" % humanize(venue.id),
            json={
                "name": "Ma librairie",
                "venueTypeId": humanize(venue_type.id),
                "venueLabelId": humanize(venue_label.id),
            },
        )

        # then
        assert response.status_code == 200
        venue = Venue.query.get(venue_id)
        assert venue.name == "Ma librairie"
        assert venue.venueTypeId == venue_type.id
        json = response.json
        assert json["isValidated"] is True
        assert "validationToken" not in json
        assert venue.isValidated

    @pytest.mark.usefixtures("db_session")
    def when_there_is_no_siret_yet(self, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            comment="Pas de siret",
            managingOfferer=user_offerer.offerer,
            siret=None,
        )

        venue_data = {
            "siret": user_offerer.offerer.siren + "11111",
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 200
        assert response.json["siret"] == venue_data["siret"]

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.delete_venue_from_iris_venues")
    @patch("pcapi.core.offerers.api.link_valid_venue_to_irises")
    def when_venue_is_physical_expect_delete_venue_from_iris_venues_and_link_venue_to_irises_to_be_called(
        self, mock_link_venue_to_iris_if_valid, mock_delete_venue_from_iris_venues, app
    ):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            isVirtual=False,
        )

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        venue_coordinates = {"latitude": 2, "longitude": 48}

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_coordinates)
        idx = response.json["id"]
        venue = Venue.query.filter_by(id=dehumanize(idx)).one()

        # Then
        mock_delete_venue_from_iris_venues.assert_called_once_with(venue.id)
        mock_link_venue_to_iris_if_valid.assert_called_once_with(venue)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.delete_venue_from_iris_venues")
    def when_venue_is_virtual_expect_delete_venue_from_iris_venues_not_to_be_called(
        self, mock_delete_venue_from_iris_venues, app
    ):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
            siret=None,
            isVirtual=True,
        )

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        venue_coordinates = {"latitude": 2, "longitude": 48}

        # when
        auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_coordinates)

        # Then
        mock_delete_venue_from_iris_venues.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.routes.pro.venues.redis.add_venue_id")
    def when_updating_a_venue_on_public_name_expect_relative_venue_id_to_be_added_to_redis(self, mock_redis, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            publicName="My old name",
            managingOfferer=user_offerer.offerer,
        )
        venue_data = {
            "publicName": "Mon nouveau nom",
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 200
        mock_redis.assert_called_once_with(client=app.redis_client, venue_id=venue.id)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_updating_a_venue_on_siret_expect_relative_venue_id_to_not_be_added_to_redis(self, mock_redis, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            comment="Pas de siret",
            siret=None,
            managingOfferer=user_offerer.offerer,
        )
        siret = venue.managingOfferer.siren + "11111"

        venue_data = {
            "siret": siret,
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 200
        mock_redis.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    def when_siret_does_not_change(self, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )
        venue_data = {
            "siret": venue.siret,
        }
        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 200
        assert response.json["siret"] == venue.siret


class Returns400:
    @pytest.mark.usefixtures("db_session")
    def when_trying_to_patch_siret_when_already_one(self, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer,
        )

        venue_data = {
            "siret": venue.managingOfferer.siren + "12345",
        }
        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=venue_data)

        # Then
        assert response.status_code == 400
        assert response.json["siret"] == ["Vous ne pouvez pas modifier le siret d'un lieu"]

    @pytest.mark.usefixtures("db_session")
    def when_latitude_out_of_range_and_longitude_wrong_format(self, app):
        # given
        user_offerer = offers_factories.UserOffererFactory()
        venue = offers_factories.VenueFactory(
            isVirtual=False,
            managingOfferer=user_offerer.offerer,
        )

        auth_request = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        data = {"latitude": -98.82387, "longitude": "112°3534"}

        # when
        response = auth_request.patch("/venues/%s" % humanize(venue.id), json=data)

        # then
        assert response.status_code == 400
        assert response.json["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
        assert response.json["longitude"] == ["Format incorrect"]
