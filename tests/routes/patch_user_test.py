import pytest

from pcapi.model_creators.generic_creators import create_user
from pcapi.models import UserSQLEntity
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Patch:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_changes_are_allowed(self, app):
            # given
            user = create_user()
            repository.save(user)
            user_id = user.id
            data = {
                "publicName": "plop",
                "email": "new@email.com",
                "postalCode": "93020",
                "phoneNumber": "0612345678",
                "departementCode": "97",
                "hasSeenTutorials": True,
            }

            # when
            response = TestClient(app.test_client()).with_auth(email=user.email).patch("/users/current", json=data)

            # then
            user = UserSQLEntity.query.get(user_id)
            assert user.publicName == "plop"
            assert user.email == "new@email.com"
            assert user.postalCode == "93020"
            assert user.departementCode == "97"
            assert user.phoneNumber == "0612345678"
            assert user.hasSeenTutorials

            assert response.json == {
                "activity": None,
                "address": None,
                "canBookFreeOffers": True,
                "city": None,
                "civility": None,
                "dateCreated": format_into_utc_date(user.dateCreated),
                "dateOfBirth": None,
                "departementCode": "97",
                "email": "new@email.com",
                "firstName": None,
                "hasOffers": False,
                "hasPhysicalVenues": False,
                "id": humanize(user.id),
                "isAdmin": False,
                "lastConnectionDate": None,
                "lastName": None,
                "needsToFillCulturalSurvey": False,
                "phoneNumber": "0612345678",
                "postalCode": "93020",
                "publicName": "plop",
            }

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_changes_are_forbidden(self, app):
            # given
            user = create_user(can_book_free_offers=True, is_admin=False)
            repository.save(user)
            user_id = user.id

            data = {
                # Changing this field is allowed...
                "publicName": "plop",
                # ... but none of the following fields.
                "isAdmin": True,
                "canBookFreeOffers": False,
                "firstName": "Jean",
                "lastName": "Martin",
                "dateCreated": "2018-08-01 12:00:00",
                "resetPasswordToken": "abc",
                "resetPasswordTokenValidityLimit": "2020-07-01 12:00:00",
            }

            # when
            response = TestClient(app.test_client()).with_auth(email=user.email).patch("/users/current", json=data)

            # then
            user = UserSQLEntity.query.get(user_id)
            assert user.publicName != "plop"  # not updated
            assert response.status_code == 400
            assert "publicName" not in response.json
            data.pop("publicName")
            for key in data:
                assert response.json[key] == ["Vous ne pouvez pas changer cette information"]
