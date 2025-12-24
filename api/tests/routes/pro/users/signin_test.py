import datetime
import logging

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def when_account_is_known(self, client, caplog):
        now = date_utils.get_naive_utc_now()
        user = users_factories.BeneficiaryGrant18Factory(
            civility=users_models.GenderEnum.M.value,
            city=None,
            address=None,
            needsToFillCulturalSurvey=False,
            email="user@example.com",
            firstName="Jean",
            lastName="Smisse",
            phoneNumber="0612345678",
            postalCode="93020",
            lastConnectionDate=now - datetime.timedelta(minutes=20),
        )

        data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}

        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        db.session.refresh(user)

        assert response.status_code == 200
        assert not any("password" in field.lower() for field in response.json)
        assert response.json == {
            "activity": None,
            "address": None,
            "city": None,
            "civility": "M.",
            "dateCreated": format_into_utc_date(user.dateCreated),
            "dateOfBirth": format_into_utc_date(user.dateOfBirth),
            "departementCode": None,
            "email": "user@example.com",
            "firstName": "Jean",
            "hasSeenProTutorials": True,
            "hasUserOfferer": False,
            "id": user.id,
            "isEmailValidated": True,
            "lastConnectionDate": format_into_utc_date(user.lastConnectionDate),
            "lastName": "Smisse",
            "needsToFillCulturalSurvey": False,
            "phoneNumber": "+33612345678",
            "postalCode": "93020",
            "roles": ["BENEFICIARY"],
        }
        assert user.lastConnectionDate > now
        assert "Failed authentication attempt" not in caplog.messages

    def when_previous_account_still_logged_and_new_user_is_known(self, client, caplog):
        user1 = users_factories.ProFactory()
        user2 = users_factories.BeneficiaryGrant18Factory()

        data = {"identifier": user2.email, "password": user2.clearTextPassword, "captchaToken": "token"}

        client.with_session_auth(email=user1.email)
        assert db.session.query(users_models.UserSession).filter_by(userId=user1.id).count() == 1

        response = client.post("/users/signin", json=data)

        assert response.status_code == 200
        assert db.session.query(users_models.UserSession).filter_by(userId=user1.id).count() == 0

    def when_user_has_no_departement_code(self, client):
        user = users_factories.UserFactory(email="USER@example.COM")
        data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}

        response = client.post("/users/signin", json=data)

        assert response.status_code == 200

        session = db.session.query(users_models.UserSession).filter_by(userId=user.id).first()
        assert session is not None

    def when_account_is_known_with_trailing_spaces_in_email(self, client):
        user = users_factories.UserFactory(email="user@example.com")
        data = {"identifier": "  user@example.com  ", "password": user.clearTextPassword, "captchaToken": "token"}

        response = client.post("/users/signin", json=data)

        assert response.status_code == 200

    def when_missing_recaptcha_token(self, client):
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": user.clearTextPassword}

        response = client.post("/users/signin", json=data)

        assert response.status_code == 400
        assert response.json == {"captchaToken": "Ce champ est obligatoire"}

    def test_with_user_offerer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=date_utils.get_naive_utc_now(),
        )
        data = {
            "identifier": user_offerer.user.email,
            "password": user_offerer.user.clearTextPassword,
            "captchaToken": "token",
        }

        # 1. fetch user by email (authentication)
        # 2. fetch user by id (login_user)
        # 3. stamp session
        # 4. fetch user for serialization
        # 5. fetch user offerer
        with assert_num_queries(5):
            response = client.post("/users/signin", json=data)

        assert response.status_code == 200
        assert response.json == {
            "activity": None,
            "address": user_offerer.user.address,
            "city": "Toulouse",
            "civility": None,
            "dateCreated": format_into_utc_date(user_offerer.user.dateCreated),
            "dateOfBirth": None,
            "departementCode": "31",
            "email": user_offerer.user.email,
            "firstName": "René",
            "hasSeenProTutorials": True,
            "hasUserOfferer": True,
            "id": user_offerer.user.id,
            "isEmailValidated": True,
            "lastConnectionDate": format_into_utc_date(user_offerer.user.lastConnectionDate),
            "lastName": "Coty",
            "needsToFillCulturalSurvey": True,
            "phoneNumber": None,
            "postalCode": None,
            "roles": ["PRO"],
        }


class Returns401Test:
    def when_identifier_is_missing(self, client, caplog):
        user = users_factories.UserFactory()
        data = {"identifier": None, "password": user.clearTextPassword, "captchaToken": "token"}

        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        assert response.status_code == 400
        assert response.json["identifier"] == ["Saisissez une chaîne de caractères valide"]
        assert "Failed authentication attempt" not in caplog.messages

    def when_identifier_is_incorrect(self, client, caplog):
        user = users_factories.UserFactory()
        data = {"identifier": "random.email@test.com", "password": user.clearTextPassword, "captchaToken": "token"}

        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant ou mot de passe incorrect"]
        assert "Failed authentication attempt" in caplog.messages

    def when_password_is_missing(self, client):
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": None, "captchaToken": "token"}

        response = client.post("/users/signin", json=data)

        assert response.status_code == 400
        assert response.json["password"] == ["Saisissez une chaîne de caractères valide"]

    def when_password_is_incorrect(self, client, caplog):
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": "wr0ng_p455w0rd", "captchaToken": "token"}

        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant ou mot de passe incorrect"]
        assert "Failed authentication attempt" in caplog.messages

    def when_account_is_not_validated(self, client):
        user = users_factories.UserFactory(isEmailValidated=False)
        data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}

        response = client.post("/users/signin", json=data)

        assert response.status_code == 401
        assert response.json["identifier"] == ["Ce compte n'est pas validé."]

    def when_account_is_an_admin_account(self, client):
        user = users_factories.AdminFactory()
        data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}

        response = client.post("/users/signin", json=data)

        assert response.status_code == 401
        assert response.json["identifier"] == ["Vous ne pouvez pas vous connecter avec un compte ADMIN."]

    def test_session_timeout(self, client):
        import time_machine
        from dateutil.relativedelta import relativedelta

        educational_factories.EducationalInstitutionFactory()

        with time_machine.travel(datetime.datetime.today() - relativedelta(years=2)):
            user = users_factories.BeneficiaryGrant18Factory()
            data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}
            response = client.post("/users/signin", json=data)
            assert response.status_code == 200
            response = client.get("/educational_institutions")
            assert response.status_code == 200

        response = client.get("/educational_institutions")
        assert response.status_code == 401
