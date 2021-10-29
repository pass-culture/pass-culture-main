import datetime
import logging
from typing import Optional
from unittest.mock import MagicMock
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
import pytest

import pcapi.core.fraud.models as fraud_models
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import ImportStatus


pytestmark = pytest.mark.usefixtures("db_session")


def build_date_of_birth_from_age(age: Optional[int]) -> datetime.datetime:
    return datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0)) - relativedelta(years=age, months=1)


class EduconnectTest:
    email = "lucy.ellingson@example.com"
    request_id = "id-XXMmsDBrJGm1N0761"
    request_id_key_prefix = "educonnect-saml-request-"
    default_underage_user_age = 15

    def connect_to_educonnect(self, client, app):
        user = users_factories.UserFactory(email=self.email)
        access_token = create_access_token(identity=self.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        # Calling /saml/educonnect/login redirects to educonnect login
        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")
        prefixed_request_id = app.redis_client.keys(f"{self.request_id_key_prefix}*")[0]
        request_id = prefixed_request_id[len(self.request_id_key_prefix) :]

        return user, request_id

    def test_get_educonnect_login(self, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        assert int(app.redis_client.get(f"{self.request_id_key_prefix}{request_id}")) == user.id

    @override_settings(IS_PROD=True)
    @override_settings(API_URL_FOR_EDUCONNECT="https://backend.passculture.app")
    def test_get_educonnect_login_production(self, client, app):
        user = users_factories.UserFactory(email=self.email)
        access_token = create_access_token(identity=self.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://educonnect.education.gouv.fr/idp")
        assert len(app.redis_client.keys(f"{self.request_id_key_prefix}*")) == 1

        request_id = app.redis_client.keys(f"{self.request_id_key_prefix}*")[0]
        assert int(app.redis_client.get(request_id)) == user.id

    @patch("pcapi.core.users.external.educonnect.api.get_saml_client")
    def test_on_educonnect_authentication_response(self, mock_get_educonnect_saml_client, client, caplog, app):
        # set user_id in redis as if /saml/educonnect/login was called
        user = users_factories.UserFactory(email=self.email)
        app.redis_client.set(f"{self.request_id_key_prefix}{self.request_id}", user.id)

        mock_saml_client = MagicMock()
        mock_saml_response = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Max"],
            "sn": ["SENS"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": ["5ba682c0fc6a05edf07cd8ed0219258f"],
        }
        mock_saml_response.in_response_to = self.request_id

        with caplog.at_level(logging.INFO):
            response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/idcheck/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert caplog.records[0].extra == {
            "date_of_birth": "2006-08-18",
            "educonnect_connection_date": "2021-10-08T11:51:33.437000",
            "educonnect_id": "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875",
            "ine_hash": "5ba682c0fc6a05edf07cd8ed0219258f",
            "first_name": "Max",
            "last_name": "SENS",
            "logout_url": "https://educonnect.education.gouv.fr/Logout",
            "saml_request_id": self.request_id,
            "student_level": "2212",
            "user_email": self.email,
        }

        assert fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).one_or_none() is not None

    @patch("pcapi.core.users.external.educonnect.api.get_educonnect_user")
    def test_complete_educonnect_beneficiary_activation(self, mock_get_educonnect_user, client, app, caplog):
        # the user initiates an educonnect login
        user, request_id = self.connect_to_educonnect(client, app)

        # Then Educonnect will call /saml/acs
        educonnect_user = users_factories.EduconnectUserFactory(
            first_name="Lucy", last_name="Ellingson", saml_request_id=request_id
        )
        mock_get_educonnect_user.return_value = educonnect_user

        with caplog.at_level(logging.INFO):
            response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302

        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user, type=fraud_models.FraudCheckType.EDUCONNECT
            ).one_or_none()
            is not None
        )
        assert user.beneficiaryFraudResult.status == fraud_models.FraudStatus.OK

        beneficiary_import = BeneficiaryImport.query.filter_by(beneficiaryId=user.id).one_or_none()
        assert beneficiary_import is not None
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert user.firstName == "Lucy"
        assert user.lastName == "Ellingson"
        assert user.dateOfBirth == datetime.datetime.combine(
            datetime.datetime.today() - relativedelta(years=15, months=1), datetime.time(0, 0)
        )

        access_token = create_access_token(identity=user.email)

        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        profile_data = {
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
        }

        response = client.patch("/native/v1/beneficiary_information", profile_data)

        assert user.roles == [user_models.UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20

    @patch("pcapi.core.users.external.educonnect.api.get_educonnect_user")
    def test_educonnect_redirects_to_success_page_with_waning_log(self, mock_get_educonnect_user, client, app, caplog):
        user, request_id = self.connect_to_educonnect(client, app)
        educonnect_user = users_factories.EduconnectUserFactory(saml_request_id=request_id)
        mock_get_educonnect_user.return_value = educonnect_user

        users_factories.UserFactory(
            firstName=educonnect_user.first_name,
            lastName=educonnect_user.last_name,
            dateOfBirth=build_date_of_birth_from_age(self.default_underage_user_age).date(),
            roles=[user_models.UserRole.UNDERAGE_BENEFICIARY],
        )

        with caplog.at_level(logging.WARNING):
            response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        print(response.location)
        assert response.location.startswith("https://webapp-v2.example.com/idcheck/validation")
        assert caplog.messages == ["Fraud suspicion after Educonnect authentication: "]
        assert caplog.records[0].extra == {"userId": user.id, "educonnectId": educonnect_user.educonnect_id}

    @patch("pcapi.core.users.external.educonnect.api.get_educonnect_user")
    def test_educonnect_redirects_to_error_page_too_young(self, mock_get_educonnect_user, client, app):
        _, request_id = self.connect_to_educonnect(client, app)
        age = 14
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location.startswith(
            "https://webapp-v2.example.com/idcheck/educonnect/erreur?code=UserAgeNotValid"
        )

    @patch("pcapi.core.users.external.educonnect.api.get_educonnect_user")
    def test_educonnect_redirects_to_error_page_too_old(self, mock_get_educonnect_user, client, app):
        _, request_id = self.connect_to_educonnect(client, app)
        age = 18
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location.startswith(
            "https://webapp-v2.example.com/idcheck/educonnect/erreur?code=UserAgeNotValid"
        )

    @patch("pcapi.core.users.external.educonnect.api.get_educonnect_user")
    def test_educonnect_connection_synchronizes_data(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 15

        previous_user_first_name = user.firstName
        previous_user_last_name = user.lastName
        previous_user_date_of_birth = user.dateOfBirth

        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age, last_name="Hayward", first_name="Verona"
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert user.firstName != previous_user_first_name
        assert user.firstName == "Verona"
        assert user.lastName != previous_user_last_name
        assert user.lastName == "Hayward"
        assert user.dateOfBirth != previous_user_date_of_birth
        assert user.dateOfBirth == datetime.datetime.combine(
            datetime.date.today() - relativedelta(years=age, months=1), datetime.time(0, 0)
        )
