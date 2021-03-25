import pytest

from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_user
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Patch:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_changes_are_allowed(self, app):
            # given
            user = UserFactory()
            user_id = user.id
            data = {
                "publicName": "Anne",
                "email": "new@example.com",
                "postalCode": "93020",
                "phoneNumber": "1234567890",
                "departementCode": "97",
                "hasSeenTutorials": True,
            }

            # when
            response = (
                TestClient(app.test_client()).with_auth(email=user.email).patch("/beneficiaries/current", json=data)
            )

            # then
            user = User.query.get(user_id)
            assert response.status_code == 200
            assert response.json["id"] == humanize(user.id)
            assert response.json["publicName"] == user.publicName
            assert user.publicName == data["publicName"]
            assert response.json["email"] == user.email
            assert user.email == data["email"]
            assert response.json["postalCode"] == user.postalCode
            assert user.postalCode == data["postalCode"]
            assert response.json["phoneNumber"] == user.phoneNumber
            assert user.phoneNumber == data["phoneNumber"]
            assert response.json["departementCode"] == user.departementCode
            assert user.departementCode == data["departementCode"]

        @pytest.mark.usefixtures("db_session")
        def when_returning_serialized_beneficiary(self, app):
            # given
            user = UserFactory(address="1 rue des machines")
            data = {
                "publicName": "Anne",
                "email": "new@example.com",
                "postalCode": "93020",
                "phoneNumber": "1234567890",
                "departementCode": "97",
                "hasSeenTutorials": True,
            }

            # when
            response = (
                TestClient(app.test_client()).with_auth(email=user.email).patch("/beneficiaries/current", json=data)
            )

            # then
            assert response.json == {
                "pk": user.id,
                "activity": None,
                "address": "1 rue des machines",
                "city": "Paris",
                "civility": None,
                "domainsCredit": {
                    "all": {"initial": 500.0, "remaining": 500.0},
                    "digital": {"initial": 200.0, "remaining": 200.0},
                    "physical": {"initial": 200.0, "remaining": 200.0},
                },
                "dateCreated": format_into_utc_date(user.dateCreated),
                "dateOfBirth": "2000-01-01T00:00:00Z",
                "departementCode": "97",
                "deposit_version": 1,
                "email": "new@example.com",
                "expenses": [
                    {"current": 0.0, "domain": "all", "limit": 500.0},
                    {"current": 0.0, "domain": "digital", "limit": 200.0},
                    {"current": 0.0, "domain": "physical", "limit": 200.0},
                ],
                "firstName": "Jeanne",
                "hasPhysicalVenues": False,
                "id": humanize(user.id),
                "isActive": True,
                "isAdmin": False,
                "isBeneficiary": True,
                "isEmailValidated": True,
                "lastName": "Doux",
                "needsToFillCulturalSurvey": True,
                "needsToSeeTutorials": False,
                "phoneNumber": "1234567890",
                "postalCode": "93020",
                "publicName": "Anne",
                "suspensionReason": "",
                "wallet_balance": 500.0,
                "deposit_expiration_date": format_into_utc_date(user.deposit_expiration_date),
                "wallet_is_activated": True,
            }

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_changes_are_forbidden(self, app):
            # given
            user = create_user(is_beneficiary=True, is_admin=False)
            repository.save(user)
            user_id = user.id

            data = {
                "isAdmin": True,
                "isBeneficiary": False,
                "firstName": "Jean",
                "lastName": "Martin",
                "dateCreated": "2018-08-01 12:00:00",
                "resetPasswordToken": "abc",
                "resetPasswordTokenValidityLimit": "2020-07-01 12:00:00",
            }

            # when
            response = (
                TestClient(app.test_client()).with_auth(email=user.email).patch("/beneficiaries/current", json=data)
            )

            # then
            user = User.query.get(user_id)
            assert response.status_code == 400
            for key in data:
                assert response.json[key] == ["Vous ne pouvez pas changer cette information"]
