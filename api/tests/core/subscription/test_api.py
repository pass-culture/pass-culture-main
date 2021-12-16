from datetime import datetime
import json
from unittest.mock import MagicMock
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import override_features
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import api_errors
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
import pcapi.notifications.push.testing as push_testing

from tests.core.subscription.test_factories import IdentificationState
from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.test_utils import json_default


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "import_status",
    [
        ImportStatus.DRAFT,
        ImportStatus.ONGOING,
        ImportStatus.REJECTED,
    ],
)
class AttachBenerificaryImportDetailsTest:
    def test_user_application(self, import_status):
        user = users_factories.UserFactory()
        subscription_api.attach_beneficiary_import_details(
            user,
            42,
            21,
            BeneficiaryImportSources.demarches_simplifiees,
            users_models.EligibilityType.AGE18,
            "random_details",
            import_status,
        )

        beneficiary_import = BeneficiaryImport.query.one()
        assert beneficiary_import.source == BeneficiaryImportSources.demarches_simplifiees.value
        assert beneficiary_import.beneficiary == user
        assert len(beneficiary_import.statuses) == 1

        status = beneficiary_import.statuses[0]
        assert status.detail == "random_details"
        assert status.status == import_status
        assert status.author == None

    def test_user_already_have_jouve_applications(self, import_status):
        user = users_factories.UserFactory()
        users_factories.BeneficiaryImportFactory(beneficiary=user, source=BeneficiaryImportSources.jouve.value)

        subscription_api.attach_beneficiary_import_details(
            user,
            42,
            21,
            BeneficiaryImportSources.demarches_simplifiees,
            users_models.EligibilityType.AGE18,
            "random_details",
            import_status,
        )

        beneficiary_import = BeneficiaryImport.query.all()
        assert len(beneficiary_import) == 2

    def test_user_application_already_have_dms_statuses(self, import_status):
        user = users_factories.UserFactory(dateOfBirth=datetime.now() - relativedelta(years=18))
        application_id = 42
        procedure_id = 21
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            applicationId=application_id,
            sourceId=procedure_id,
        )
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import)

        subscription_api.attach_beneficiary_import_details(
            user,
            application_id,
            procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            users_models.EligibilityType.AGE18,
            "random details",
            import_status,
        )
        beneficiary_import = BeneficiaryImport.query.filter(BeneficiaryImport.beneficiaryId == user.id).one()
        assert len(beneficiary_import.statuses) == 2

    def test_user_application_already_have_another_dms_application(self, import_status):
        user = users_factories.UserFactory()
        application_id = 42
        procedure_id = 21
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            applicationId=143,
            sourceId=procedure_id,
        )
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import)

        subscription_api.attach_beneficiary_import_details(
            user,
            application_id,
            procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            users_models.EligibilityType.AGE18,
            "random details",
            import_status,
        )
        assert BeneficiaryImport.query.count() == 2


@pytest.mark.usefixtures("db_session")
class EduconnectFlowTest:
    @freeze_time("2021-10-10")
    @patch("pcapi.core.users.external.educonnect.api.get_saml_client")
    def test_legacy_educonnect_subscription(self, mock_get_educonnect_saml_client, client, app):
        # TODO (viconnex): remove this journey after app native mandatory version is >= 164
        ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
        fraud_factories.IneHashWhitelistFactory(ine_hash=ine_hash)
        user = users_factories.UserFactory(dateOfBirth=datetime(2004, 1, 1))
        access_token = create_access_token(identity=user.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        mock_saml_client = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.prepare_for_authenticate.return_value = (
            "request_id_123",
            {"headers": [("Location", "https://pr4.educonnect.phm.education.gouv.fr/idp")]},
        )

        # Get educonnect login form with saml protocol
        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")

        prefixed_request_id = app.redis_client.keys("educonnect-saml-request-*")[0]
        request_id = prefixed_request_id[len("educonnect-saml-request-") :]

        mock_saml_response = MagicMock()
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Max"],
            "sn": ["SENS"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": [ine_hash],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["eleve1d"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
        }
        mock_saml_response.in_response_to = request_id

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/idcheck/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert len(user.beneficiaryFraudResults) == 1
        assert user.beneficiaryFraudResults[0].status == fraud_models.FraudStatus.OK

        beneficiary_import = BeneficiaryImport.query.filter_by(beneficiaryId=user.id).one_or_none()
        assert beneficiary_import is not None
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert user.firstName == "Max"
        assert user.lastName == "SENS"
        assert user.dateOfBirth == datetime(2006, 8, 18, 0, 0)
        assert user.ineHash == ine_hash

        profile_data = {
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
        }

        response = client.patch("/native/v1/beneficiary_information", profile_data)

        assert response.status_code == 204
        assert user.roles == [users_models.UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20

    @freeze_time("2021-10-10")
    @patch("pcapi.core.users.external.educonnect.api.get_saml_client")
    @override_features(IS_HONOR_STATEMENT_MANDATORY_TO_ACTIVATE_BENEFICIARY=True, ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_educonnect_subscription(self, mock_get_educonnect_saml_client, client, app):
        ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
        fraud_factories.IneHashWhitelistFactory(ine_hash=ine_hash)
        user = users_factories.UserFactory(dateOfBirth=datetime(2004, 1, 1))
        access_token = create_access_token(identity=user.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        mock_saml_client = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.prepare_for_authenticate.return_value = (
            "request_id_123",
            {"headers": [("Location", "https://pr4.educonnect.phm.education.gouv.fr/idp")]},
        )

        profile_data = {
            "activity": "Lycéen",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
            "address": "1 rue des rues",
            "city": "Uneville",
            "firstName": "WrongFirstName",
            "lastName": "Wrong Lastname",
            "postalCode": "77000",
        }

        response = client.post("/native/v1/subscription/profile", profile_data)

        assert user.city == "Uneville"
        assert subscription_api.has_completed_profile(user)
        assert not user.hasCompletedIdCheck

        # Get educonnect login form with saml protocol
        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")

        prefixed_request_id = app.redis_client.keys("educonnect-saml-request-*")[0]
        request_id = prefixed_request_id[len("educonnect-saml-request-") :]

        mock_saml_response = MagicMock()
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Max"],
            "sn": ["SENS"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": [ine_hash],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["eleve1d"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
        }
        mock_saml_response.in_response_to = request_id

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/idcheck/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert len(user.beneficiaryFraudResults) == 1
        assert user.beneficiaryFraudResults[0].status == fraud_models.FraudStatus.OK

        beneficiary_import = BeneficiaryImport.query.filter_by(beneficiaryId=user.id).one_or_none()
        assert beneficiary_import is not None
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert user.firstName == "Max"
        assert user.lastName == "SENS"
        assert user.dateOfBirth == datetime(2006, 8, 18, 0, 0)
        assert user.ineHash == ine_hash

        assert not user.is_beneficiary
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

        response = client.post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204
        assert user.roles == [users_models.UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20


@pytest.mark.usefixtures("db_session")
class UbbleWorkflowTest:
    def test_start_ubble_workflow(self, ubble_mock):
        user = users_factories.UserFactory()
        redirect_url = subscription_api.start_ubble_workflow(user, redirect_url="https://example.com")
        assert redirect_url == "https://id.ubble.ai/29d9eca4-dce6-49ed-b1b5-8bb0179493a8"

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId is not None
        assert fraud_check.resultContent is not None
        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING

        ubble_request = ubble_mock.last_request.json()
        assert ubble_request["data"]["attributes"]["webhook"] == "http://localhost/webhooks/ubble/application_status"

    @pytest.mark.parametrize(
        "state, status, fraud_check_status",
        [
            (
                IdentificationState.INITIATED,
                fraud_models.ubble.UbbleIdentificationStatus.INITIATED,
                fraud_models.FraudCheckStatus.PENDING,
            ),
            (
                IdentificationState.PROCESSING,
                fraud_models.ubble.UbbleIdentificationStatus.PROCESSING,
                fraud_models.FraudCheckStatus.PENDING,
            ),
            (
                IdentificationState.VALID,
                fraud_models.ubble.UbbleIdentificationStatus.PROCESSED,
                fraud_models.FraudCheckStatus.OK,
            ),
            (
                IdentificationState.INVALID,
                fraud_models.ubble.UbbleIdentificationStatus.PROCESSED,
                fraud_models.FraudCheckStatus.KO,
            ),
            (
                IdentificationState.UNPROCESSABLE,
                fraud_models.ubble.UbbleIdentificationStatus.PROCESSED,
                fraud_models.FraudCheckStatus.KO,
            ),
            (
                IdentificationState.ABORTED,
                fraud_models.ubble.UbbleIdentificationStatus.ABORTED,
                fraud_models.FraudCheckStatus.CANCELED,
            ),
        ],
    )
    def test_update_ubble_workflow(self, ubble_mocker, state, status, fraud_check_status):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.UBBLE, user=user)
        ubble_response = UbbleIdentificationResponseFactory(identification_state=state)

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)

        ubble_content = fraud_check.resultContent
        assert ubble_content["status"] == status.value
        assert fraud_check.status == fraud_check_status

    def test_ubble_workflow_processing_add_inapp_message(self, ubble_mocker):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.PENDING, user=user
        )
        ubble_response = UbbleIdentificationResponseFactory(identification_state=IdentificationState.PROCESSING)
        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)
            message = subscription_models.SubscriptionMessage.query.one()
            assert message.userMessage == "Ton document d'identité est en cours de vérification."
            assert message.popOverIcon == subscription_models.PopOverIcon.CLOCK

    def test_ubble_workflow_rejected_add_inapp_message(self, ubble_mocker):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.PENDING, user=user
        )
        ubble_response = UbbleIdentificationResponseFactory(identification_state=IdentificationState.INVALID)
        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)
            message = subscription_models.SubscriptionMessage.query.one()
            assert (
                message.userMessage
                == "Désolé, la vérification de ton identité n'a pas pu aboutir. Nous t'invitons à passer par le site Démarches-Simplifiées."
            )
            assert message.callToActionLink == "passculture://verification-identite/demarches-simplifiees"
            assert message.callToActionIcon == subscription_models.CallToActionIcon.EXTERNAL
            assert message.callToActionTitle == "Accéder au site Démarches-Simplifiées"


@pytest.mark.usefixtures("db_session")
class NextSubscriptionStepTest:
    eighteen_years_ago = datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=1)
    fifteen_years_ago = datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=15, months=1)

    def test_next_subscription_step_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()
        assert subscription_api.get_next_subscription_step(user) == None

    def test_next_subscription_step_phone_validation(self):
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PHONE_VALIDATION
        )

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_next_subscription_step_underage_profile_completion(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.fifteen_years_ago,
            city=None,
        )
        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_next_subscription_step_underage_honor_statement(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.fifteen_years_ago,
            city="Zanzibar",
            hasCompletedIdCheck=True,
        )
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_next_subscription_step_underage_finished(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.fifteen_years_ago,
            city="Zanzibar",
            hasCompletedIdCheck=True,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            resultContent=None,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        assert subscription_api.get_next_subscription_step(user) == None

    def test_next_subscription_step_user_profiling(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.USER_PROFILING

    def test_next_subscription_step_user_profiling_ko(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="high")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING, resultContent=content, user=user
        )

        assert subscription_api.get_next_subscription_step(user) == None

    def test_next_subscription_step_profile_completion(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING, resultContent=content, user=user
        )

        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    def test_next_subscription_step_identity_check(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Zanzibar",
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING, resultContent=content, user=user
        )

        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.IDENTITY_CHECK

    def test_next_subscription_step_honor_statement(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Zanzibar",
            hasCompletedIdCheck=True,
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING, resultContent=content, user=user
        )

        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

    def test_next_subscription_step_finished(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            address="3 rue du quai",
            hasCompletedIdCheck=True,
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING, resultContent=content, user=user
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            resultContent=None,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert subscription_api.get_next_subscription_step(user) == None

    @pytest.mark.parametrize(
        "feature_flags,user_age,user_school_type,expected_result",
        [
            # User 18
            (
                {"ALLOW_IDCHECK_REGISTRATION": True, "ENABLE_UBBLE": False},
                18,
                None,
                [subscription_models.IdentityCheckMethod.JOUVE],
            ),
            (
                {"ALLOW_IDCHECK_REGISTRATION": True, "ENABLE_UBBLE": True},
                18,
                None,
                [subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {"ALLOW_IDCHECK_REGISTRATION": False},
                18,
                None,
                [],
            ),
            # User 15 - 17
            # Public schools -> force EDUCONNECT when possible
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": True,
                    "ENABLE_UBBLE": True,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
                [subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
                [],
            ),
            # Other schools
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": False,
                    "ENABLE_UBBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PRIVATE_HIGH_SCHOOL,
                [subscription_models.IdentityCheckMethod.JOUVE],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ENABLE_UBBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PRIVATE_HIGH_SCHOOL,
                [subscription_models.IdentityCheckMethod.EDUCONNECT, subscription_models.IdentityCheckMethod.JOUVE],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ENABLE_UBBLE": True,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.EDUCONNECT, subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": False,
                    "ENABLE_UBBLE": True,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ENABLE_UBBLE": True,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": True,
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": False,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
            (
                {
                    "ENABLE_NATIVE_EAC_INDIVIDUAL": False,
                },
                15,
                None,
                [],
            ),
        ],
    )
    def test_get_allowed_identity_check_methods(self, feature_flags, user_age, user_school_type, expected_result):
        dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, schoolType=user_school_type)
        with override_features(**feature_flags):
            assert subscription_api.get_allowed_identity_check_methods(user) == expected_result

    @pytest.mark.parametrize(
        "feature_flags,user_age,expected_result",
        [
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18": True},
                18,
                subscription_models.MaintenancePageType.WITH_DMS,
            ),
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18": False},
                18,
                subscription_models.MaintenancePageType.WITHOUT_DMS,
            ),
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE": True},
                15,
                subscription_models.MaintenancePageType.WITH_DMS,
            ),
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE": False},
                15,
                subscription_models.MaintenancePageType.WITHOUT_DMS,
            ),
        ],
    )
    @patch("pcapi.core.subscription.api.get_allowed_identity_check_methods", return_value=[])
    def test_get_maintenance_page_type(self, _, feature_flags, user_age, expected_result):
        dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)
        with override_features(**feature_flags):
            assert subscription_api.get_maintenance_page_type(user) == expected_result


@pytest.mark.usefixtures("db_session")
class OnSucessfulDMSApplicationTest:
    @override_features(FORCE_PHONE_VALIDATION=False)
    def test_new_beneficiaries_are_recorded_with_deposit(self):
        # given
        information = fraud_models.DMSContent(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=datetime.utcnow() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18),
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            address="11 Rue du Test",
            application_id=123,
            procedure_id=123456,
            civility="Mme",
            activity="Étudiant",
            registration_datetime=datetime.today(),
        )
        applicant = users_factories.UserFactory(email=information.email)
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=applicant, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        # when

        subscription_api.on_successful_application(
            user=applicant,
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_data=information,
            eligibility_type=check.eligibilityType,
            application_id=123,
            source_id=123456,
        )

        # then
        first = users_models.User.query.first()
        assert first.email == "jane.doe@example.com"
        assert first.wallet_balance == 300
        assert first.civility == "Mme"
        assert first.activity == "Étudiant"
        assert first.has_beneficiary_role
        assert len(push_testing.requests) == 2
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2016025

    def test_an_import_status_is_saved_if_beneficiary_is_created(self):
        # given
        information = fraud_models.DMSContent(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=datetime.utcnow() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18),
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            address="11 Rue du Test",
            application_id=123,
            procedure_id=123456,
            civility="Mme",
            activity="Étudiant",
            registration_datetime=datetime.today(),
        )
        applicant = users_factories.UserFactory(email=information.email)
        # when
        subscription_api.on_successful_application(
            user=applicant,
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_data=information,
            eligibility_type=users_models.EligibilityType.AGE18,
            application_id=123,
            source_id=123456,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.beneficiary.email == "jane.doe@example.com"
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert beneficiary_import.applicationId == 123

    @patch("pcapi.repository.repository")
    @patch("pcapi.domain.user_emails.send_activation_email")
    def test_error_is_collected_if_beneficiary_could_not_be_saved(self, send_activation_email, mock_repository):
        # given
        information = fraud_factories.DMSContentFactory(application_id=123)
        applicant = users_factories.UserFactory(email=information.email)

        mock_repository.save.side_effect = [api_errors.ApiErrors({"postalCode": ["baaaaad value"]})]

        # when
        with pytest.raises(api_errors.ApiErrors):
            subscription_api.on_successful_application(
                user=applicant,
                source=BeneficiaryImportSources.demarches_simplifiees,
                source_data=information,
                eligibility_type=users_models.EligibilityType.AGE18,
                application_id=123,
                source_id=123456,
            )

        # then
        send_activation_email.assert_not_called()
        assert len(push_testing.requests) == 0

    def test_activate_beneficiary_when_confirmation_happens_after_18_birthday(self):
        with freeze_time("2020-01-01"):
            applicant = users_factories.UserFactory()
            eighteen_years_and_one_month_ago = datetime.today() - relativedelta(years=18, months=1)

            # the user deposited their DMS application before turning 18
            information = fraud_models.DMSContent(
                department="93",
                last_name="Doe",
                first_name="Jane",
                birth_date=eighteen_years_and_one_month_ago,
                email="jane.doe@example.com",
                phone="0612345678",
                postal_code="93130",
                address="11 Rue du Test",
                application_id=123,
                procedure_id=123456,
                civility="Mme",
                activity="Étudiant",
                registration_datetime=datetime.today(),
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=applicant,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
            )

        assert applicant.has_beneficiary_role is False

        with freeze_time("2020-03-01"):
            # the DMS application is confirmed after the user turns 18
            subscription_api.on_successful_application(
                user=applicant,
                source=BeneficiaryImportSources.demarches_simplifiees,
                source_data=information,
                eligibility_type=users_models.EligibilityType.AGE18,
                application_id=123,
                source_id=123456,
            )
        assert applicant.has_beneficiary_role


@pytest.mark.usefixtures("db_session")
class DMSSubscriptionTest:
    def test_dms_subscription(self):
        user = users_factories.UserFactory(subscriptionState=users_models.SubscriptionState.phone_validated)
        application_id = 12
        content = fraud_factories.DMSContentFactory()
        fraud_check = subscription_api.start_workflow(user, thirdparty_id=str(application_id), content=content)

        assert user.subscriptionState == users_models.SubscriptionState.identity_check_pending
        assert fraud_check.user == user
        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18


@pytest.mark.usefixtures("db_session")
class OverflowSubscriptionLimitationTest:
    @override_features(ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=True)
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def test_is_ubble_allowed_if_subscription_overflow(self, age):
        # user birthday is in settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS days
        birth_date = datetime.utcnow() - relativedelta(years=age + 1)
        birth_date += relativedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS - 1)

        # the user has:
        # email v
        user_approching_birthday = users_factories.UserFactory(dateOfBirth=birth_date)

        users_utils.get_age_from_birth_date(user_approching_birthday.dateOfBirth)
        user_not_allowed = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow()
            - relativedelta(years=age, days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS + 10)
        )

        assert subscription_api.is_ubble_allowed_if_subscription_overflow(user_approching_birthday)
        assert not subscription_api.is_ubble_allowed_if_subscription_overflow(user_not_allowed)

    @override_features(ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=False)
    def test_subscription_is_possible_if_flag_is_false(self):
        user = users_factories.UserFactory()
        assert subscription_api.is_ubble_allowed_if_subscription_overflow(user)
