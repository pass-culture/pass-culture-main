import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.factories import BeneficiaryImportFactory
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.notifications.push import testing as push_testing


pytestmark = pytest.mark.usefixtures("db_session")


class NextStepTest:
    def test_next_subscription_test(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "phone-validation",
            "allowedIdentityCheckMethods": ["jouve"],
            "maintenancePageType": None,
        }

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ALLOW_IDCHECK_UNDERAGE_REGISTRATION=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=True,
    )
    def test_next_subscription_maintenance_page_test(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=15, months=5),
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "maintenance",
            "allowedIdentityCheckMethods": [],
            "maintenancePageType": "with-dms",
        }


class UpdateProfileTest:
    @override_features(ENABLE_UBBLE=True)
    def test_update_profile(self, client):
        """
        Test that valid request:
            * updates the user's profile information;
            * send a request to Batch to update the user's information
        """

        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            firstName=None,
            lastName=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        profile_data = {
            "firstName": "John",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = users_models.User.query.get(user.id)
        assert user.firstName == "John"
        assert user.lastName == "Doe"
        assert user.address == "1 rue des rues"
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.phoneNumber == "+33609080706"

    def test_update_profile_when_fraud_check_done(self, client):
        """
        Test that valid request:
            * updates the user's profile information;
            * sets the user to beneficiary;
            * send a request to Batch to update the user's information
        """
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.JOUVE)
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        profile_data = {
            "firstName": "John",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
            "schoolType": "Lycée public",
        }

        client.with_token(email=user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = users_models.User.query.get(user.id)
        assert user.firstName != "John"
        assert user.lastName != "Doe"
        assert user.address == "1 rue des rues"
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.schoolType == users_models.SchoolType.PUBLIC_HIGH_SCHOOL

        assert user.has_beneficiary_role
        assert user.deposit

        assert len(push_testing.requests) == 1
        notification = push_testing.requests[0]

        assert notification["user_id"] == user.id
        assert notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "77000"

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_update_beneficiary_underage(self, client, app):
        """
        Test that valid request:
            * updates the user's profile information;
            * sets the user to beneficiary;
            * send a request to Batch to update the user's information
        """
        user = users_factories.UserFactory(
            address=None,
            city=None,
            dateOfBirth=datetime.datetime.now() - relativedelta(years=15, months=4),
            postalCode=None,
            activity=None,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.EDUCONNECT)
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)

        beneficiary_import = BeneficiaryImportFactory(
            beneficiary=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        beneficiary_import.setStatus(ImportStatus.CREATED)

        profile_data = {
            "address": None,
            "firstName": "John",
            "lastName": "Doe",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
            "schoolType": "Lycée militaire",
        }

        client.with_token(email=user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = users_models.User.query.get(user.id)
        assert user.address is None
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.phoneNumber is None
        assert user.schoolType == users_models.SchoolType.MILITARY_HIGH_SCHOOL

        assert user.roles == [users_models.UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20

        assert len(push_testing.requests) == 1
