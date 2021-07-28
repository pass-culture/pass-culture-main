from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import jwt
import pytest

from pcapi import settings
import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.core.users.utils import ALGORITHM_HS_256

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    @freeze_time("2020-10-15 09:00:00")
    def when_account_is_known(self, app):
        # given

        user = users_factories.BeneficiaryFactory(email="test@mail.com")
        data = {"new_email": "new@email.com", "password": "user@AZERTY123"}

        # when
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # then
        assert response.status_code == 204
        information_data = {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 2066067,
            "MJ-TemplateLanguage": True,
            "To": user.email,
            "Vars": {
                "beneficiary_name": user.firstName,
                "env": "-development",
            },
        }
        confirmation_data_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjdXJyZW50X2VtYWlsIjo"
            "idGVzdEBtYWlsLmNvbSIsIm5ld19lbWFpbCI6Im5ld0BlbWFpbC5jb20iLCJ"
            "leHAiOjE2MDI4Mzg4MDB9.Q2-583JqPSfDjuMD6ZMhMnb07Rr47iBZFRwlFC"
            "ymSf0"
        )
        confirmation_link = (
            f"{settings.WEBAPP_URL}/changement-email?token={confirmation_data_token}&expiration_timestamp=1602838800"
        )
        confirmation_data = {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 2066065,
            "MJ-TemplateLanguage": True,
            "To": "new@email.com",
            "Vars": {
                "beneficiary_name": "Jeanne",
                "confirmation_link": confirmation_link,
                "env": "-development",
            },
        }

        assert [m.sent_data for m in mails_testing.outbox] == [information_data, confirmation_data]

    @freeze_time("2020-10-15 09:00:00")
    def when_token_is_valid(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="oldemail@mail.com")

        expiration_date = datetime.now() + timedelta(hours=1)
        token_payload = dict(
            exp=int(expiration_date.timestamp()), current_email="oldemail@mail.com", new_email="newemail@mail.com"
        )
        token = jwt.encode(
            token_payload,
            settings.JWT_SECRET_KEY,  # type: ignore # known as str in build assertion
            algorithm=ALGORITHM_HS_256,
        ).decode("ascii")

        data = {"token": token}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email", json=data)

        # Then
        assert response.status_code == 204
        old_email_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_email_user is None
        new_email_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_email_user is not None
        assert new_email_user.id == user.id


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_password_is_missing(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        data = {"new_email": "toto"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["password"] == ["Ce champ est obligatoire"]

    def when_new_email_is_missing(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        data = {"password": "user@AZERTY123"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["new_email"] == ["Ce champ est obligatoire"]


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def when_password_is_incorrect(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        data = {"new_email": "new email", "password": "wrong password"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["password"] == ["Mot de passe incorrect"]

    def when_account_is_not_active(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(isActive=False)
        data = {"new_email": user.email, "password": "user@AZERTY123"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant ou mot de passe incorrect"]

    def when_account_is_not_validated(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        user.generate_validation_token()
        data = {"new_email": user.email, "password": "user@AZERTY123"}

        # When
        client = TestClient(app.test_client()).with_auth(user.email)
        response = client.put("/beneficiaries/change_email_request", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Ce compte n'est pas validé."]
