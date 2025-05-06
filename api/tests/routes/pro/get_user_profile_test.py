import datetime

from dateutil.relativedelta import relativedelta
import flask
import pytest

from pcapi.core import testing
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    num_queries = testing.AUTHENTICATION_QUERIES

    def test_is_impersonated(self, client):
        user = users_factories.BaseUserFactory(
            isEmailValidated=True,
            roles=[users_models.UserRole.PRO],
            hasSeenProTutorials=True,
        )

        url = flask.url_for("pro_private_api.get_profile")
        client = client.with_session_auth(email=user.email)

        with client.client.session_transaction() as session:
            session["internal_admin_email"] = user.email

        with testing.assert_num_queries(self.num_queries):
            response = client.get(url)
            assert response.status_code == 200

        assert response.json["isImpersonated"]

    def when_user_is_logged_in_and_has_no_deposit(self, client):
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
            isEmailValidated=True,
        )

        client = client.with_session_auth(email="toto@example.com")
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/users/current")
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
            "hasSeenProTutorials": True,
            "hasUserOfferer": False,
            "id": user.id,
            "idPieceNumber": None,
            "isAdmin": False,
            "isEmailValidated": True,
            "lastConnectionDate": format_into_utc_date(user.lastConnectionDate),
            "lastName": "Smisse",
            "needsToFillCulturalSurvey": False,
            "notificationSubscriptions": {"marketing_email": True, "marketing_push": True, "subscribed_themes": []},
            "phoneNumber": "+33612345678",
            "phoneValidationStatus": None,
            "postalCode": None,
            "roles": ["BENEFICIARY"],
            "isImpersonated": False,
        }


class Returns401Test:
    def when_user_is_not_logged_in(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/users/current")
            assert response.status_code == 401
