import datetime

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_account_is_known(self, client):
        # given
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
            publicName="Toto",
            lastConnectionDate=datetime.datetime(2019, 1, 1),
        )

        data = {"identifier": user.email, "password": user.clearTextPassword}

        # when
        response = client.post("/users/signin", json=data)

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
            "hasPhysicalVenues": False,
            "hasSeenProTutorials": True,
            "hasSeenProRgs": False,
            "id": humanize(user.id),
            "nonHumanizedId": str(user.id),
            "isAdmin": False,
            "isEmailValidated": True,
            "lastConnectionDate": format_into_utc_date(user.lastConnectionDate),
            "lastName": "Smisse",
            "needsToFillCulturalSurvey": False,
            "phoneNumber": "+33612345678",
            "postalCode": "93020",
            "publicName": "Toto",
            "roles": ["BENEFICIARY"],
        }

    @pytest.mark.usefixtures("db_session")
    def when_user_has_no_departement_code(self, client):
        # given
        user = users_factories.UserFactory(email="USER@example.COM")
        data = {"identifier": user.email, "password": user.clearTextPassword}

        # when
        response = client.post("/users/signin", json=data)

        # then
        assert response.status_code == 200

    @pytest.mark.usefixtures("db_session")
    def when_account_is_known_with_mixed_case_email(self, client):
        # given
        user = users_factories.UserFactory(email="USER@example.COM")
        data = {"identifier": "uSeR@EXAmplE.cOm", "password": user.clearTextPassword}

        # when
        response = client.post("/users/signin", json=data)

        # then
        assert response.status_code == 200

    @pytest.mark.usefixtures("db_session")
    def when_account_is_known_with_trailing_spaces_in_email(self, client):
        # given
        user = users_factories.UserFactory(email="user@example.com")
        data = {"identifier": "  user@example.com  ", "password": user.clearTextPassword}

        # when
        response = client.post("/users/signin", json=data)

        # then
        assert response.status_code == 200

    @pytest.mark.usefixtures("db_session")
    def expect_a_new_user_session_to_be_recorded(self, client):
        # given
        user = users_factories.UserFactory(email="user@example.com")
        data = {"identifier": user.email, "password": user.clearTextPassword}

        # when
        response = client.post("/users/signin", json=data)

        # then
        assert response.status_code == 200

        session = users_models.UserSession.query.filter_by(userId=user.id).first()
        assert session is not None


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_identifier_is_missing(self, client):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": None, "password": user.clearTextPassword}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["identifier"] == ["none is not an allowed value"]

    @pytest.mark.usefixtures("db_session")
    def when_identifier_is_incorrect(self, client):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": "random.email@test.com", "password": user.clearTextPassword}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant ou mot de passe incorrect"]

    @pytest.mark.usefixtures("db_session")
    def when_password_is_missing(self, client):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": None}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["password"] == ["none is not an allowed value"]

    @pytest.mark.usefixtures("db_session")
    def when_password_is_incorrect(self, client):
        # Given
        user = users_factories.UserFactory()
        data = {"identifier": user.email, "password": "wr0ng_p455w0rd"}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant ou mot de passe incorrect"]

    @pytest.mark.usefixtures("db_session")
    def when_account_is_not_validated(self, client):
        # Given
        user = users_factories.UserFactory.build()
        user.generate_validation_token()
        repository.save(user)
        data = {"identifier": user.email, "password": user.clearTextPassword}

        # When
        response = client.post("/users/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Ce compte n'est pas validé."]
