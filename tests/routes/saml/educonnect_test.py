import datetime
import logging
from unittest.mock import MagicMock
from unittest.mock import patch

from flask_jwt_extended.utils import create_access_token
import pytest

import pcapi.core.fraud.models as fraud_models
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users.external.educonnect.models import EduconnectUser


pytestmark = pytest.mark.usefixtures("db_session")


class EduconnectTest:
    email = "lucy.ellingson@example.com"
    request_id = "id-XXMmsDBrJGm1N0761"
    request_id_key_prefix = "educonnect-saml-request-"

    def test_get_educonnect_login(self, client, app):
        user = users_factories.UserFactory(email=self.email)
        access_token = create_access_token(identity=self.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")
        assert len(app.redis_client.keys(f"{self.request_id_key_prefix}*")) == 1

        request_id = app.redis_client.keys(f"{self.request_id_key_prefix}*")[0]
        assert int(app.redis_client.get(request_id)) == user.id

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
            "first_name": "Max",
            "last_name": "SENS",
            "logout_url": "https://educonnect.education.gouv.fr/Logout",
            "saml_request_id": self.request_id,
            "student_level": "2212",
            "user_email": self.email,
        }

        assert fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).one_or_none() is not None

    @patch("pcapi.core.users.external.educonnect.api.get_educonnect_user")
    def test_complete_educonnect_login(self, mock_get_educonnect_user, client, app, caplog):
        user = users_factories.UserFactory(email=self.email)
        access_token = create_access_token(identity=self.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        # Calling /saml/educonnect/login redirects to educonnect login
        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")
        assert len(app.redis_client.keys(f"{self.request_id_key_prefix}*")) == 1

        request_id_key = app.redis_client.keys(f"{self.request_id_key_prefix}*")[0]
        assert int(app.redis_client.get(request_id_key)) == user.id

        request_id = request_id_key[len(f"{self.request_id_key_prefix}") :]

        # Then Educonnect will call /saml/acs
        mock_get_educonnect_user.return_value = EduconnectUser(
            connection_datetime=datetime.datetime.strptime("2021-10-08 11:51:33.437000", "%Y-%m-%d %H:%M:%S.%f"),
            birth_date=datetime.datetime.strptime("2006-08-18", "%Y-%m-%d").date(),
            educonnect_id="e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875",
            first_name="Max",
            last_name="SENS",
            logout_url="https://educonnect.education.gouv.fr/Logout",
            saml_request_id=request_id,
            student_level="2212",
        )

        with caplog.at_level(logging.INFO):
            response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert caplog.records[0].extra == {
            "date_of_birth": "2006-08-18",
            "educonnect_connection_date": "2021-10-08T11:51:33.437000",
            "educonnect_id": "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875",
            "first_name": "Max",
            "last_name": "SENS",
            "logout_url": "https://educonnect.education.gouv.fr/Logout",
            "saml_request_id": request_id,
            "student_level": "2212",
            "user_email": self.email,
        }

        assert fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).one_or_none() is not None
