import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in_and_has_no_deposit(self, app):
        user = users_factories.BeneficiaryGrant18Factory(
            civility=users_models.GenderEnum.M.value,
            address=None,
            city=None,
            needsToFillCulturalSurvey=False,
            email="toto@example.com",
            firstName="Jean",
            lastName="Smisse",
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18),
            phoneNumber="0612345678",
            publicName="Toto",
            isEmailValidated=True,
        )

        # When
        response = TestClient(app.test_client()).with_session_auth(email="toto@example.com").get("/users/current")

        # Then
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
            "email": "toto@example.com",
            "externalIds": {},
            "firstName": "Jean",
            "hasPhysicalVenues": False,
            "hasSeenProTutorials": True,
            "hasSeenProRgs": False,
            "id": humanize(user.id),
            "nonHumanizedId": str(user.id),
            "idPieceNumber": None,
            "isAdmin": False,
            "isEmailValidated": True,
            "lastConnectionDate": None,
            "lastName": "Smisse",
            "needsToFillCulturalSurvey": False,
            "notificationSubscriptions": {"marketing_email": True, "marketing_push": True},
            "phoneNumber": "+33612345678",
            "phoneValidationStatus": None,
            "postalCode": None,
            "publicName": "Toto",
            "roles": ["BENEFICIARY"],
        }


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, app):
        # When
        response = TestClient(app.test_client()).get("/users/current")

        # Then
        assert response.status_code == 401
