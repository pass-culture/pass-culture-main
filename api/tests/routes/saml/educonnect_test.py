import datetime
import logging
from typing import Optional
from unittest.mock import MagicMock
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
import freezegun
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud.api import has_passed_educonnect
import pcapi.core.fraud.models as fraud_models
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models


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

    def test_educonnect_login_no_redirect(self, client):
        users_factories.UserFactory(email=self.email)
        access_token = create_access_token(identity=self.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/saml/educonnect/login?redirect=false")

        assert response.status_code == 204
        assert response.headers["educonnect-redirect"].startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")
        assert response.headers["Access-Control-Expose-Headers"] == "educonnect-redirect"

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

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    def test_on_educonnect_authentication_response(self, mock_get_educonnect_saml_client, client, caplog, app):
        # set user_id in redis as if /saml/educonnect/login was called
        ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
        fraud_factories.IneHashWhitelistFactory(ine_hash=ine_hash)
        user = users_factories.UserFactory(email=self.email)
        app.redis_client.set(f"{self.request_id_key_prefix}{self.request_id}", user.id)

        mock_saml_client = MagicMock()
        mock_saml_response = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Max"],
            "sn": ["SENS"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["eleve1d"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": [ine_hash],
        }
        mock_saml_response.in_response_to = self.request_id

        with caplog.at_level(logging.INFO):
            with freezegun.freeze_time("2021-10-10"):
                response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/educonnect/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert caplog.records[0].extra == {
            "date_of_birth": "2006-08-18",
            "educonnect_connection_date": "2021-10-08T11:51:33.437000",
            "educonnect_id": "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875",
            "ine_hash": ine_hash,
            "first_name": "Max",
            "last_name": "SENS",
            "logout_url": "https://educonnect.education.gouv.fr/Logout",
            "user_type": "eleve1d",
            "saml_request_id": self.request_id,
            "school_uai": "school_uai",
            "student_level": "2212",
            "user_email": self.email,
            "user_id": user.id,
        }

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.EDUCONNECT
        ).one()

        assert fraud_check.resultContent == {
            "birth_date": "2006-08-18",
            "educonnect_id": "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875",
            "first_name": "Max",
            "ine_hash": ine_hash,
            "last_name": "SENS",
            "registration_datetime": "2021-10-10T00:00:00",
            "school_uai": "school_uai",
            "student_level": "2212",
        }
        assert has_passed_educonnect(user)
        assert user.firstName == "Max"
        assert user.lastName == "SENS"
        assert user.dateOfBirth == datetime.datetime(2006, 8, 18, 0, 0)
        assert user.ineHash == ine_hash

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    def test_connexion_date_missing(self, mock_get_educonnect_saml_client, client, caplog, app):
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
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["eleve1d"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": ["ine_hash"],
        }
        mock_saml_response.in_response_to = self.request_id

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/educonnect/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.EDUCONNECT, status=fraud_models.FraudCheckStatus.OK
        ).one()

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    def test_birth_date_missing(self, mock_get_educonnect_saml_client, client, caplog, app):
        user = users_factories.UserFactory(email=self.email)
        app.redis_client.set(f"{self.request_id_key_prefix}{self.request_id}", user.id)

        mock_saml_client = MagicMock()
        mock_saml_response = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Max"],
            "sn": ["SENS"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["eleve1d"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": ["ine_hash"],
        }
        mock_saml_response.in_response_to = self.request_id

        with caplog.at_level(logging.ERROR):
            response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/educonnect/erreur?logout_url=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert caplog.records[0].extra == {
            "parsed_data": {
                "givenName": ["Max"],
                "sn": ["SENS"],
                "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
                "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
                "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["eleve1d"],
                "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                    "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
                ],
                "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
                "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
                "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": ["ine_hash"],
            }
        }

        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user, type=fraud_models.FraudCheckType.EDUCONNECT
            ).first()
            is None
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    def test_user_type_not_student(self, mock_get_educonnect_saml_client, client, caplog, app):
        # set user_id in redis as if /saml/educonnect/login was called
        user = users_factories.UserFactory(email=self.email)
        app.redis_client.set(f"{self.request_id_key_prefix}{self.request_id}", user.id)

        mock_saml_client = MagicMock()
        mock_saml_response = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Sugar"],
            "sn": ["Daddy"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["resp1d"],
        }
        mock_saml_response.in_response_to = self.request_id

        with caplog.at_level(logging.INFO):
            response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/educonnect/erreur?code=UserTypeNotStudent&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )
        assert caplog.records[0].extra == {"saml_request_id": self.request_id, "user_id": str(user.id)}
        assert caplog.records[0].message == "Wrong user type of educonnect user"

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_redirects_to_success_page_with_warning_log(self, mock_get_educonnect_user, client, app, caplog):
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
        assert response.location.startswith("https://webapp-v2.example.com/educonnect/validation")
        assert caplog.messages == [
            "Fraud suspicion after educonnect authentication with codes: ine_not_whitelisted, duplicate_user"
        ]
        assert caplog.records[0].extra == {"user_id": user.id}

    @override_features(ENABLE_UNDERAGE_GENERALISATION=True)
    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    @freezegun.freeze_time("2021-12-15")  # during opening
    def test_16_year_old_but_not_eligible(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        user.dateOfBirth = datetime.date(2005, 12, 17)  # birthday during opening and required age
        educonnect_user = users_factories.EduconnectUserFactory(
            saml_request_id=request_id,
            birth_date=datetime.date(2006, 12, 11),  # birthday before opening but required age
        )
        mock_get_educonnect_user.return_value = educonnect_user

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302

        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?code=UserAgeNotValid&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )
        assert len(user.subscriptionMessages) == 1
        assert (
            user.subscriptionMessages[0].userMessage
            == "La date de naissance de ton dossier Educonnect (11/12/2006) indique que tu n'es pas éligible. Tu seras éligible le 22/12/2021."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @freezegun.freeze_time("2021-12-21")
    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    def test_educonnect_redirects_to_error_page_too_young(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 14
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?code=UserAgeNotValid&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )
        assert len(user.subscriptionMessages) == 1
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier a été refusé. La date de naissance enregistrée sur ton compte Educonnect (21/11/2007) indique que tu n'as pas entre 15 et 17 ans."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    @freezegun.freeze_time("2021-12-21")
    def test_educonnect_redirects_to_error_page_18_years_old(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 18
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?code=UserAgeNotValid18YearsOld&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )
        assert len(user.subscriptionMessages) == 1
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier a été refusé. La date de naissance enregistrée sur ton compte Educonnect (21/11/2003) indique que tu n'as pas entre 15 et 17 ans."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @freezegun.freeze_time("2021-12-21")
    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    def test_educonnect_redirects_to_error_page_too_old(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 20
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?code=UserAgeNotValid&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )
        assert len(user.subscriptionMessages) == 1
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier a été refusé. La date de naissance enregistrée sur ton compte Educonnect (21/11/2001) indique que tu n'as pas entre 15 et 17 ans."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
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

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_ine_not_whitelisted(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, ine_hash="identifiantNonWhitlisté"
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?code=UserNotWhitelisted&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )
        assert len(user.subscriptionMessages) == 1
        assert (
            user.subscriptionMessages[0].userMessage
            == "Tu ne fais pas partie de la phase de test. Encore un peu de patience, on se donne rendez-vous en janvier."
        )

    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_ine_whitelist_filter_off(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, ine_hash="identifiantNonWhitlisté"
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location.startswith("https://webapp-v2.example.com/educonnect/validation")
        assert user.is_beneficiary

    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_not_eligible_fails_twice(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=14
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?code=UserAgeNotValid&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert not user.is_beneficiary

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})
        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?code=UserAgeNotValid&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

    @pytest.mark.parametrize(
        "age",
        [15, 16, 17, 18, 19],
    )
    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_connection_updates_user_birth_date(self, mock_get_educonnect_user, client, app, age):
        user, request_id = self.connect_to_educonnect(client, app)
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})
        assert user.dateOfBirth == datetime.datetime.combine(
            datetime.date.today() - relativedelta(years=age, months=1), datetime.time(0, 0)
        )


class PerformanceTest:
    @override_settings(IS_PERFORMANCE_TESTS=True)
    @override_features(ENABLE_INE_WHITELIST_FILTER=False)
    def test_performance_tests(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.date.today() - relativedelta(years=15))

        response = client.post("/saml/acs", form={"SAMLResponse": str(user.id)})

        assert response.status_code == 302
        assert fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.EDUCONNECT, status=fraud_models.FraudCheckStatus.OK
        ).one()
