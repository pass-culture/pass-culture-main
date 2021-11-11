from datetime import datetime

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.users.factories import AdminFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import ProFactory
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def when_user_is_logged_in_and_has_no_deposit(self, app):
        # Given
        user = BeneficiaryGrant18Factory(
            email="toto@example.com",
            postalCode="93020",
        )
        repository.delete(*user.deposits)

        # When
        response = (
            TestClient(app.test_client()).with_session_auth(email="toto@example.com").get("/beneficiaries/current")
        )

        # Then
        assert response.status_code == 200
        assert response.json == {
            "activity": user.activity,
            "address": user.address,
            "city": user.city,
            "civility": user.civility,
            "dateCreated": format_into_utc_date(user.dateCreated),
            "dateOfBirth": format_into_utc_date(user.dateOfBirth),
            "departementCode": user.departementCode,
            "deposit_expiration_date": None,
            "deposit_version": None,
            "domainsCredit": None,
            "email": "toto@example.com",
            "firstName": user.firstName,
            "hasPhysicalVenues": user.hasPhysicalVenues,
            "id": humanize(user.id),
            "isActive": True,
            "isAdmin": False,
            "isBeneficiary": True,
            "isEmailValidated": True,
            "lastName": user.lastName,
            "needsToFillCulturalSurvey": True,
            "needsToSeeTutorials": True,
            "pk": user.id,
            "phoneNumber": user.phoneNumber,
            "postalCode": user.postalCode,
            "publicName": user.publicName,
            "roles": ["BENEFICIARY"],
            "suspensionReason": "",
            "wallet_balance": 0.0,
            "wallet_is_activated": False,
        }

    def when_user_is_logged_in_and_has_a_deposit(self, app):
        # Given
        BeneficiaryGrant18Factory(
            email="wallet_test@email.com",
            postalCode="93020",
            deposit__dateCreated=datetime(2000, 1, 1, 2, 2),
            deposit__expirationDate=datetime(2002, 1, 1, 2, 2),
        )

        # When
        response = (
            TestClient(app.test_client()).with_session_auth("wallet_test@email.com").get("/beneficiaries/current")
        )

        # Then
        assert response.json["wallet_is_activated"] == True
        assert response.json["deposit_expiration_date"] == "2002-01-01T02:02:00Z"

    def when_user_has_booked_some_offers(self, app):
        # Given
        user = BeneficiaryGrant18Factory(email="wallet_test@email.com", postalCode="93020", deposit__version=1)

        IndividualBookingFactory(individualBooking__user=user, amount=5)

        # When
        response = (
            TestClient(app.test_client()).with_session_auth("wallet_test@email.com").get("/beneficiaries/current")
        )

        # Then
        assert response.json["wallet_balance"] == 495.0
        assert response.json["domainsCredit"] == {
            "all": {"initial": 500.0, "remaining": 495.0},
            "digital": {"initial": 200.0, "remaining": 200.0},
            "physical": {"initial": 200.0, "remaining": 195.0},
        }

    def when_user_has_cancelled_some_offers(self, app):
        # Given
        user = BeneficiaryGrant18Factory(email="wallet_test@email.com", postalCode="75130", deposit__version=1)
        booking_factories.CancelledIndividualBookingFactory(individualBooking__user=user)

        # When
        response = (
            TestClient(app.test_client()).with_session_auth("wallet_test@email.com").get("/beneficiaries/current")
        )

        # Then
        assert response.json["wallet_balance"] == 500.0
        assert response.json["domainsCredit"] == {
            "all": {"initial": 500.0, "remaining": 500.0},
            "digital": {"initial": 200.0, "remaining": 200.0},
            "physical": {"initial": 200.0, "remaining": 200.0},
        }

    def when_user_is_created_without_postal_code(self, app):
        # Given
        BeneficiaryGrant18Factory(email="wallet_test@email.com", postalCode=None, departementCode=None)

        # When
        response = (
            TestClient(app.test_client()).with_session_auth("wallet_test@email.com").get("/beneficiaries/current")
        )

        # Then
        assert response.status_code == 200

    def when_user_is_a_pro(self, app):
        # Given
        pro = ProFactory(email="pro@example.com", postalCode=None, dateOfBirth=None)
        pro.suspensionReason = None
        repository.save(pro)

        # When
        response = TestClient(app.test_client()).with_session_auth("pro@example.com").get("/beneficiaries/current")

        # Then
        assert response.status_code == 200
        assert response.json["suspensionReason"] == None

    def when_user_is_an_admin(self, app):
        # Given
        AdminFactory(email="admin@example.com", postalCode=None, dateOfBirth=None)

        # When
        response = TestClient(app.test_client()).with_session_auth("admin@example.com").get("/beneficiaries/current")

        # Then
        assert response.status_code == 200

    def should_return_deposit_version(self, app):
        # Given
        BeneficiaryGrant18Factory(email="wallet_test@email.com", postalCode="93020", deposit__version=1)

        # When
        response = (
            TestClient(app.test_client()).with_session_auth("wallet_test@email.com").get("/beneficiaries/current")
        )

        # Then

        assert response.json["deposit_version"] == 1


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, app):
        # When
        response = TestClient(app.test_client()).get("/beneficiaries/current")

        # Then
        assert response.status_code == 401
