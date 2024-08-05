import datetime
import logging

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.repository import db
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_account_is_known(self, client, caplog):
        # given
        now = datetime.datetime.utcnow()
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

        # when
        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        db.session.refresh(user)
        # then
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
            "hasPartnerPage": False,
            "hasSeenProTutorials": True,
            "hasSeenProRgs": False,
            "hasUserOfferer": False,
            "id": user.id,
            "isAdmin": False,
            "isEmailValidated": True,
            "lastConnectionDate": format_into_utc_date(user.lastConnectionDate),
            "lastName": "Smisse",
            "needsToFillCulturalSurvey": False,
            "phoneNumber": "+33612345678",
            "postalCode": "93020",
            "roles": ["BENEFICIARY"],
            "navState": {"eligibilityDate": None, "newNavDate": None},
        }
        assert user.lastConnectionDate > now
        assert "Failed authentication attempt" not in caplog.messages

    @pytest.mark.usefixtures("db_session")
    def when_previous_account_still_logged_and_new_user_is_known(self, client, caplog):
        # given
        user1 = users_factories.ProFactory()
        user2 = users_factories.BeneficiaryGrant18Factory()

        data = {"identifier": user2.email, "password": user2.clearTextPassword, "captchaToken": "token"}

        client.with_session_auth(email=user1.email)
        assert users_models.UserSession.query.filter_by(userId=user1.id).count() == 1

        # when
        response = client.post("/users/signin", json=data)

        # then
        assert response.status_code == 200
        assert users_models.UserSession.query.filter_by(userId=user1.id).count() == 0

    @pytest.mark.usefixtures("db_session")
    def when_user_has_no_departement_code(self, client):
        # given
        user = users_factories.UserFactory(email="USER@example.COM")
        data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}

        # when
        response = client.post("/users/signin", json=data)

        # then
        assert response.status_code == 200

        session = users_models.UserSession.query.filter_by(userId=user.id).first()
        assert session is not None

    @pytest.mark.usefixtures("db_session")
    def when_account_is_known_with_trailing_spaces_in_email(self, client):
        # given
        user = users_factories.UserFactory(email="user@example.com")
        data = {"identifier": "  user@example.com  ", "password": user.clearTextPassword, "captchaToken": "token"}

        # when
        response = client.post("/users/signin", json=data)

        # then
        assert response.status_code == 200

    # Fixme : (mageoffray, 2023-12-14)
    # Remove this test - https://passculture.atlassian.net/browse/PC-26462
    @override_settings(RECAPTCHA_WHITELIST=["whitelisted@email.com", "alsoWithelisted@test.com"])
    @pytest.mark.usefixtures("db_session")
    def when_account_is_whitelisted_for_recaptcha(self, client):
        # Given
        user = users_factories.UserFactory(email="whitelisted@email.com")
        data = {"identifier": user.email, "password": user.clearTextPassword}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 200

    @pytest.mark.usefixtures("db_session")
    def when_missing_recaptcha_token(self, client):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": user.clearTextPassword}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"captchaToken": "Ce champ est obligatoire"}

    @pytest.mark.usefixtures("db_session")
    def test_whith_user_offerer_and_nav_state(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=datetime.datetime.utcnow(),
        )
        navState = users_factories.UserProNewNavStateFactory(user=user_offerer.user)
        data = {
            "identifier": user_offerer.user.email,
            "password": user_offerer.user.clearTextPassword,
            "captchaToken": "token",
        }

        # When
        # 1. fetch user
        # 2. stamp session
        # 3. fetch user for serialization
        # 4. fetch user offerer
        # 5. fetch user pro nav state
        # 6. fetch user offerer for discard_session
        # 7 fetch user_session for discard_session
        # 8 fetch user has partner page

        with assert_num_queries(8):
            response = client.post("/users/signin", json=data)

        # Then
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
            "hasPartnerPage": False,
            "hasSeenProTutorials": True,
            "hasSeenProRgs": False,
            "hasUserOfferer": True,
            "id": user_offerer.user.id,
            "isAdmin": False,
            "isEmailValidated": True,
            "lastConnectionDate": format_into_utc_date(user_offerer.user.lastConnectionDate),
            "lastName": "Coty",
            "needsToFillCulturalSurvey": True,
            "phoneNumber": None,
            "postalCode": None,
            "roles": ["PRO"],
            "navState": {
                "eligibilityDate": format_into_utc_date(navState.eligibilityDate),
                "newNavDate": format_into_utc_date(navState.newNavDate),
            },
        }


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_identifier_is_missing(self, client, caplog):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": None, "password": user.clearTextPassword, "captchaToken": "token"}

        # When
        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["identifier"] == ["Ce champ ne peut pas être nul"]
        assert "Failed authentication attempt" not in caplog.messages

    @pytest.mark.usefixtures("db_session")
    def when_identifier_is_incorrect(self, client, caplog):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": "random.email@test.com", "password": user.clearTextPassword, "captchaToken": "token"}

        # When
        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant ou mot de passe incorrect"]
        assert "Failed authentication attempt" in caplog.messages

    @pytest.mark.usefixtures("db_session")
    def when_password_is_missing(self, client):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": None, "captchaToken": "token"}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["password"] == ["Ce champ ne peut pas être nul"]

    @pytest.mark.usefixtures("db_session")
    def when_password_is_incorrect(self, client, caplog):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": "wr0ng_p455w0rd", "captchaToken": "token"}

        # When
        with caplog.at_level(logging.INFO):
            response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant ou mot de passe incorrect"]
        assert "Failed authentication attempt" in caplog.messages

    @pytest.mark.usefixtures("db_session")
    def when_account_is_not_validated(self, client):
        # Given
        user = users_factories.UserFactory(isEmailValidated=False)
        repository.save(user)
        data = {"identifier": user.email, "password": user.clearTextPassword, "captchaToken": "token"}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Ce compte n'est pas validé."]

    @pytest.mark.usefixtures("db_session")
    def test_session_timeout(self, client):
        from dateutil.relativedelta import relativedelta
        import time_machine

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
