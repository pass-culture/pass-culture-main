import datetime
import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import time_machine
from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token

import pcapi.core.mails.testing as mails_testing
import pcapi.core.subscription.models as subscription_models
import pcapi.notifications.push.testing as push_testing
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def build_date_of_birth_from_age(age: int | None) -> datetime.datetime:
    return datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0)) - relativedelta(years=age, months=1)


class EduconnectTest:
    email = "lucy.ellingson@example.com"
    request_id = "id-XXMmsDBrJGm1N0761"
    request_id_key_prefix = "educonnect-saml-request-"
    default_underage_user_age = 17

    def connect_to_educonnect(self, client, app):
        user = users_factories.UserFactory(email=self.email, activity="Collégien")
        access_token = create_access_token(user.email, additional_claims={"user_claims": {"user_id": user.id}})
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
        user = users_factories.UserFactory(email=self.email)
        access_token = create_access_token(user.email, additional_claims={"user_claims": {"user_id": user.id}})
        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/saml/educonnect/login?redirect=false")

        assert response.status_code == 204
        assert response.headers["educonnect-redirect"].startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")
        assert response.headers["Access-Control-Expose-Headers"] == "educonnect-redirect"

    @pytest.mark.settings(
        API_URL_FOR_EDUCONNECT="https://backend.passculture.app",
        EDUCONNECT_METADATA_FILE="educonnect.production.metadata.xml",
    )
    def test_get_educonnect_login_production(self, client, app):
        user = users_factories.UserFactory(email=self.email)
        access_token = create_access_token(user.email, additional_claims={"user_claims": {"user_id": user.id}})
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
        signup_birth_date = datetime.datetime(2000, 1, 1)
        ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
        user = users_factories.UserFactory(
            email=self.email, firstName="ProfileFirstName", lastName="ProfileLastName", dateOfBirth=signup_birth_date
        )
        app.redis_client.set(f"{self.request_id_key_prefix}{self.request_id}", user.id)

        # even if the user has failed educonnect
        already_done_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.KO,
            eligibilityType=user_models.EligibilityType.UNDERAGE,
        )

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
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.76": ["Mme"],
        }
        mock_saml_response.in_response_to = self.request_id

        with caplog.at_level(logging.INFO):
            with time_machine.travel("2021-10-10", tick=False):
                response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/educonnect/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert caplog.records[0].extra == {
            "civility": "Mme",
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

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=subscription_models.FraudCheckType.EDUCONNECT)
            .filter(subscription_models.BeneficiaryFraudCheck.id != already_done_check.id)
            .one()
        )

        assert fraud_check.resultContent == {
            "birth_date": "2006-08-18",
            "civility": "Mme",
            "educonnect_id": "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875",
            "first_name": "Max",
            "ine_hash": ine_hash,
            "last_name": "SENS",
            "registration_datetime": "2021-10-10T00:00:00",
            "school_uai": "school_uai",
            "student_level": "2212",
        }
        assert (
            subscription_api.get_identity_check_fraud_status(user, user_models.EligibilityType.UNDERAGE, fraud_check)
            == subscription_schemas.SubscriptionItemStatus.OK
        )
        assert user.firstName == "ProfileFirstName"
        assert user.lastName == "ProfileLastName"
        assert user.dateOfBirth == signup_birth_date
        assert user.validatedBirthDate == datetime.date(2006, 8, 18)
        assert user.ineHash is None

        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "event_name": "user_identity_check_started",
            "event_payload": {"type": "educonnect"},
            "user_id": user.id,
        }

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    def test_connexion_date_missing(self, mock_get_educonnect_saml_client, client, caplog, app):
        # set user_id in redis as if /saml/educonnect/login was called
        user = users_factories.UserFactory(email=self.email)
        app.redis_client.set(f"{self.request_id_key_prefix}{self.request_id}", user.id)
        birth_date = (datetime.date.today() - relativedelta(years=17, months=1)).strftime("%Y-%m-%d")

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
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": [birth_date],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": ["ine_hash"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.76": ["Mme"],
        }
        mock_saml_response.in_response_to = self.request_id

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == f"https://webapp-v2.example.com/educonnect/validation?firstName=Max&lastName=SENS&dateOfBirth={birth_date}&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                user=user,
                type=subscription_models.FraudCheckType.EDUCONNECT,
                status=subscription_models.FraudCheckStatus.OK,
            )
            .one()
        )

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
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=subscription_models.FraudCheckType.EDUCONNECT)
            .first()
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

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    def test_user_type_not_defined(self, mock_get_educonnect_saml_client, client, caplog, app):
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
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": ["educonnect_id"],
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
    def test_duplicate_beneficiary(self, mock_get_educonnect_user, client, app):
        duplicate_user, request_id = self.connect_to_educonnect(client, app)
        educonnect_user = users_factories.EduconnectUserFactory(saml_request_id=request_id, age=17)
        mock_get_educonnect_user.return_value = educonnect_user

        users_factories.UserFactory(
            firstName=educonnect_user.first_name,
            lastName=educonnect_user.last_name,
            email="titus@quartier-latin.com",
            validatedBirthDate=build_date_of_birth_from_age(self.default_underage_user_age).date(),
            roles=[user_models.UserRole.UNDERAGE_BENEFICIARY],
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout&code=DuplicateUser"
        )

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {"DUPLICATE_BENEFICIARY_EMAIL": "tit***@quartier-latin.com"}
        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=duplicate_user.id).one()
        )
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.DUPLICATE_USER]

        message = educonnect_subscription_api.get_educonnect_subscription_message(fraud_check)
        assert message.user_message == (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom. "
            "Connecte-toi avec l’adresse mail tit***@quartier-latin.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_duplicate_ine(self, mock_get_educonnect_user, client, app):
        duplicate_user, request_id = self.connect_to_educonnect(client, app)
        educonnect_user = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, ine_hash="shotgun_ine", age=17
        )
        mock_get_educonnect_user.return_value = educonnect_user

        users_factories.UserFactory(ineHash="shotgun_ine", email="shotgun@ine.com")

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout&code=DuplicateINE"
        )

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=duplicate_user.id).one()
        )
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.DUPLICATE_INE]

        message = educonnect_subscription_api.get_educonnect_subscription_message(fraud_check)
        assert message.user_message == (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé aux identifiants ÉduConnect que tu as fournis. "
            "Connecte-toi avec l’adresse mail sho***@ine.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @time_machine.travel("2021-12-21")
    def test_educonnect_redirects_to_error_page_too_young(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 14
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout&code=UserAgeNotValid"
        )

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        message = educonnect_subscription_api.get_educonnect_subscription_message(fraud_check)
        assert (
            message.user_message
            == "Ton dossier a été refusé. La date de naissance sur ton compte Éduconnect (21/11/2007) indique que tu n'as pas entre 15 et 17 ans."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @time_machine.travel("2021-12-21")
    def test_educonnect_redirects_to_error_page_18_years_old(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 18
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout&code=UserAgeNotValid18YearsOld"
        )

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        message = educonnect_subscription_api.get_educonnect_subscription_message(fraud_check)
        assert (
            message.user_message
            == "Ton dossier a été refusé. La date de naissance sur ton compte Éduconnect (21/11/2003) indique que tu n'as pas entre 15 et 17 ans."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    @time_machine.travel("2021-12-21")
    def test_educonnect_redirects_to_error_page_too_old(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 20
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=age
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout&code=UserAgeNotValid"
        )
        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        message = educonnect_subscription_api.get_educonnect_subscription_message(fraud_check)
        assert (
            message.user_message
            == "Ton dossier a été refusé. La date de naissance sur ton compte Éduconnect (21/11/2001) indique que tu n'as pas entre 15 et 17 ans."
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_connection_synchronizes_validated_birth_date(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        age = 15

        first_name = user.firstName
        last_name = user.lastName
        signup_birth_date = user.dateOfBirth
        educonnect_birth_date = datetime.date(2000, 1, 1)

        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id,
            age=age,
            last_name="Hayward",
            first_name="Verona",
            birth_date=educonnect_birth_date,
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert user.firstName == first_name
        assert user.lastName == last_name
        assert user.validatedBirthDate == educonnect_birth_date
        assert user.dateOfBirth == signup_birth_date

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_not_eligible_fails_twice(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, age=14
        )

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout&code=UserAgeNotValid"
        )

        assert not user.is_beneficiary

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})
        assert response.status_code == 302
        assert response.location == (
            "https://webapp-v2.example.com/educonnect/erreur?logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout&code=UserAgeNotValid"
        )

    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_educonnect_user")
    def test_educonnect_connection_updates_validated_birth_date(self, mock_get_educonnect_user, client, app):
        user, request_id = self.connect_to_educonnect(client, app)
        birth_date = datetime.date.today() - relativedelta(years=17, months=1)
        mock_get_educonnect_user.return_value = users_factories.EduconnectUserFactory(
            saml_request_id=request_id, birth_date=birth_date
        )

        client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})
        assert user.validatedBirthDate == birth_date


class PerformanceTest:
    @pytest.mark.settings(IS_PERFORMANCE_TESTS=True)
    def test_performance_tests(self, client):
        user = users_factories.UserFactory(age=17)

        response = client.post("/saml/acs", form={"SAMLResponse": str(user.id)})

        assert response.status_code == 302
        assert (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                user=user,
                type=subscription_models.FraudCheckType.EDUCONNECT,
                status=subscription_models.FraudCheckStatus.OK,
            )
            .one()
        )
