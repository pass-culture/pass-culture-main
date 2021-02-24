from datetime import datetime

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Patch:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_changes_are_allowed(self, app):
            # given
            now = datetime.now()
            beneficiary = users_factories.UserFactory(dateOfBirth=now, lastConnectionDate=now)
            data = {
                "publicName": "publicName",
                "firstName": "firstName",
                "lastName": "lastName",
                "email": "new@example.com",
                "postalCode": "93020",
                "phoneNumber": "0612345678",
                "departementCode": "97",
                "hasSeenTutorials": True,
            }

            # when
            response = (
                TestClient(app.test_client()).with_auth(email=beneficiary.email).patch("/users/current", json=data)
            )

            # then
            user = User.query.get(beneficiary.id)
            assert user.publicName == "publicName"
            assert user.firstName == "firstName"
            assert user.lastName == "lastName"
            assert user.email == "new@example.com"
            assert user.postalCode == "93020"
            assert user.departementCode == "97"
            assert user.phoneNumber == "0612345678"
            assert user.hasSeenTutorials

            assert response.json == {
                "activity": beneficiary.activity,
                "address": beneficiary.address,
                "isBeneficiary": True,
                "city": beneficiary.city,
                "civility": beneficiary.civility,
                "dateCreated": format_into_utc_date(user.dateCreated),
                "dateOfBirth": format_into_utc_date(now),
                "departementCode": beneficiary.departementCode,
                "email": "new@example.com",
                "firstName": "firstName",
                "hasOffers": False,
                "hasPhysicalVenues": False,
                "id": humanize(beneficiary.id),
                "isAdmin": False,
                "lastConnectionDate": format_into_utc_date(now),
                "lastName": "lastName",
                "needsToFillCulturalSurvey": beneficiary.needsToFillCulturalSurvey,
                "phoneNumber": "0612345678",
                "postalCode": beneficiary.postalCode,
                "publicName": "publicName",
            }

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_changes_are_forbidden(self, app):
            # given
            beneficiary = users_factories.UserFactory()

            data = {
                # Changing this field is allowed...
                "publicName": "plop",
                "firstName": "Jean",
                "lastName": "Martin",
                # ... but none of the following fields.
                "isAdmin": True,
                "isBeneficiary": False,
                "dateCreated": "2018-08-01 12:00:00",
                "resetPasswordToken": "abc",
                "resetPasswordTokenValidityLimit": "2020-07-01 12:00:00",
            }

            # when
            response = (
                TestClient(app.test_client()).with_auth(email=beneficiary.email).patch("/users/current", json=data)
            )

            # then
            user = User.query.get(beneficiary.id)
            assert user.publicName != "plop"  # not updated
            assert response.status_code == 400
            assert "publicName" not in response.json
            assert "firstName" not in response.json
            assert "lastName" not in response.json
            data.pop("publicName")
            data.pop("firstName")
            data.pop("lastName")
            for key in data:
                assert response.json[key] == ["Vous ne pouvez pas changer cette information"]

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_optional_fields_are_provided_but_emtpy(self, app):
            # given
            pro = users_factories.UserFactory(isBeneficiary=False)
            data = {
                "firstName": "",
                "lastName": "",
                "email": "",
            }

            # when
            response = TestClient(app.test_client()).with_auth(email=pro.email).patch("/users/current", json=data)

            # then
            user = User.query.get(pro.id)
            assert user.firstName == pro.firstName
            assert user.lastName == pro.lastName
            assert user.email == pro.email

            assert response.json == {
                "email": ["Ce champ est obligatoire"],
                "firstName": ["Ce champ est obligatoire"],
                "lastName": ["Ce champ est obligatoire"],
            }
