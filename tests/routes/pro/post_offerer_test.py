import copy
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.core.offerers.factories import VirtualVenueTypeFactory
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.core.users.factories import AdminFactory
from pcapi.core.users.factories import ProFactory
from pcapi.models import UserOfferer
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


api_entreprise_json_mock = {
    "unite_legale": {"etablissement_siege": {"siret": ""}, "etablissements": [], "activite_principale": ""}
}
DEFAULT_DIGITAL_VENUE_LABEL = "Offre numérique"


class Returns201Test:
    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def when_creating_a_virtual_venue(self, mock_api_entreprise, app):
        # given
        mock_api_entreprise.return_value = MagicMock(
            status_code=200, text="", json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock))
        )

        pro = ProFactory()
        digital_venue_type = VirtualVenueTypeFactory()
        body = {
            "name": "Test Offerer",
            "siren": "418166096",
            "address": "123 rue de Paris",
            "postalCode": "93100",
            "city": "Montreuil",
        }

        # when
        response = TestClient(app.test_client()).with_session_auth(pro.email).post("/offerers", json=body)

        # then
        assert response.status_code == 201
        assert response.json["siren"] == "418166096"
        assert response.json["name"] == "Test Offerer"
        virtual_venues = list(filter(lambda v: v["isVirtual"], response.json["managedVenues"]))
        assert len(virtual_venues) == 1
        assert virtual_venues[0]["venueTypeId"] == humanize(digital_venue_type.id)

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def when_no_address_is_provided(self, mock_api_entreprise, app):
        # given
        mock_api_entreprise.return_value = MagicMock(
            status_code=200, text="", json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock))
        )

        pro = ProFactory()
        VirtualVenueTypeFactory()
        body = {"name": "Test Offerer", "siren": "418166096", "postalCode": "93100", "city": "Montreuil"}

        # when
        response = TestClient(app.test_client()).with_session_auth(pro.email).post("/offerers", json=body)

        # then
        assert response.status_code == 201
        assert response.json["siren"] == "418166096"
        assert response.json["name"] == "Test Offerer"

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def when_current_user_is_admin(self, mock_api_entreprise, app):
        # Given
        mock_api_entreprise.return_value = MagicMock(
            status_code=200, text="", json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock))
        )

        admin = AdminFactory()
        VirtualVenueTypeFactory()
        body = {
            "name": "Test Offerer",
            "siren": "418166096",
            "address": "123 rue de Paris",
            "postalCode": "93100",
            "city": "Montreuil",
        }

        # When
        response = TestClient(app.test_client()).with_session_auth(admin.email).post("/offerers", json=body)

        # then
        assert response.status_code == 201

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def expect_the_current_user_to_have_access_to_new_offerer(self, mock_api_entreprise, app):
        # Given
        mock_api_entreprise.return_value = MagicMock(
            status_code=200, text="", json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock))
        )

        pro = ProFactory()
        VirtualVenueTypeFactory()
        body = {
            "name": "Test Offerer",
            "siren": "418166096",
            "address": "123 rue de Paris",
            "postalCode": "93100",
            "city": "Montreuil",
        }

        # when
        response = TestClient(app.test_client()).with_session_auth(pro.email).post("/offerers", json=body)

        # then
        assert response.status_code == 201
        offerer = Offerer.query.first()
        assert offerer.UserOfferers[0].user == pro

    @patch("pcapi.domain.admin_emails.make_validation_email_object")
    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def when_offerer_already_have_user_offerer_new_user_offerer_has_validation_token(
        self, mock_api_entreprise, make_validation_email_object, app
    ):
        # Given
        make_validation_email_object.return_value = {"Html-part": None}
        mock_api_entreprise.return_value = MagicMock(
            status_code=200, text="", json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock))
        )

        pro = ProFactory()
        offerer = OffererFactory()
        UserOffererFactory(offerer=offerer, validationToken=None)
        VirtualVenueTypeFactory()
        body = {
            "name": offerer.name,
            "siren": offerer.siren,
            "address": offerer.address,
            "postalCode": offerer.postalCode,
            "city": offerer.city,
        }

        # when
        response = TestClient(app.test_client()).with_session_auth(pro.email).post("/offerers", json=body)

        # then
        assert response.status_code == 201
        offerer = Offerer.query.first()
        created_user_offerer = (
            UserOfferer.query.filter(UserOfferer.offerer == offerer).filter(UserOfferer.user == pro).one()
        )
        assert created_user_offerer.validationToken is not None
