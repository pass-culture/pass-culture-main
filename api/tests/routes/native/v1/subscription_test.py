import datetime

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi import settings
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.subscription.models import SubscriptionStepCompletionState
import pcapi.core.subscription.ubble.models as ubble_models
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.notifications.push import testing as push_testing
import pcapi.repository
from pcapi.utils.string import u_nbsp


pytestmark = pytest.mark.usefixtures("db_session")


class NextStepTest:
    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_next_subscription(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "phone-validation"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_next_subscription_test_profile_completion(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert not response.json["hasIdentityCheckPending"]
        assert response.json["subscriptionMessage"] is None

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=True,
    )
    @time_machine.travel("2022-09-08 11:54:22")
    def test_next_subscription_maintenance_page(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=15, months=5),
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        # User completed profile
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "maintenance"
        assert response.json["allowedIdentityCheckMethods"] == []
        assert response.json["maintenancePageType"] == "with-dms"
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] == {
            "callToAction": None,
            "popOverIcon": "CLOCK",
            "updatedAt": None,
            "userMessage": "La vérification d'identité est "
            "momentanément indisponible. L'équipe "
            "du pass Culture met tout en oeuvre "
            "pour la rétablir au plus vite.",
        }

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    @pytest.mark.parametrize(
        "fraud_check_status,reason_code,ubble_status,next_step,pending_idcheck,subscription_message",
        [
            (
                fraud_models.FraudCheckStatus.STARTED,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.INITIATED,
                "identity-check",
                False,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.PENDING,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSING,
                "honor-statement",
                True,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.OK,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                "honor-statement",
                False,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.KO,
                fraud_models.FraudReasonCode.AGE_TOO_OLD,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                None,
                False,
                {
                    "callToAction": None,
                    "popOverIcon": "ERROR",
                    "userMessage": "Ton dossier a été refusé\xa0: tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
                },
            ),
            (
                fraud_models.FraudCheckStatus.CANCELED,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
                "identity-check",
                False,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.SUSPICIOUS,
                fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                "identity-check",  # User can retry
                False,
                {
                    "callToAction": {
                        "callToActionIcon": "RETRY",
                        "callToActionLink": "passculture://verification-identite",
                        "callToActionTitle": "Réessayer la vérification de mon identité",
                    },
                    "popOverIcon": None,
                    "userMessage": "Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarches-simplifiees.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité.",
                },
            ),
        ],
    )
    @override_features(ENABLE_UBBLE=True)
    @time_machine.travel("2022-09-08 12:01:12")
    def test_next_subscription_test_ubble(
        self, client, fraud_check_status, reason_code, ubble_status, next_step, pending_idcheck, subscription_message
    ):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            activity="Étudiant",
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "phone-validation"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform phone validation
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform profile completion
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform first id check with Ubble
        ubble_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_check_status,
            reasonCodes=[reason_code],
            resultContent=fraud_factories.UbbleContentFactory(status=ubble_status),
        )
        if subscription_message:
            subscription_message["updatedAt"] = ubble_fraud_check.updatedAt.isoformat()

        # Check next step: only a single non-aborted Ubble identification is allowed
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == next_step
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] == pending_idcheck
        assert response.json["subscriptionMessage"] == subscription_message

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=True,
    )
    @time_machine.travel("2022-09-08 12:39:04")
    def test_underage_not_ok_turned_18(self, client):
        # User has already performed id check with Ubble for underage credit (successfully or not), 2 years ago
        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(years=2)):
            user = users_factories.UserFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=16, days=5),
                activity="Employé",
            )
            # 15-17: no phone validation

            # Perform profile completion
            fraud_factories.ProfileCompletionFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            # Perform first id check with Ubble
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.KO,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

        # Now user turned 18, phone validation and profile completion are requested and Ubble identification is requested again
        # Process should not depend on Ubble result performed when underage
        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "phone-validation"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform phone validation
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform profile completion
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform id check with Ubble
        ubble_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSING
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "honor-statement"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is True
        assert response.json["subscriptionMessage"] is None

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] is None
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is True
        assert response.json["subscriptionMessage"]["callToAction"] is None
        assert response.json["subscriptionMessage"]["popOverIcon"] == "CLOCK"
        assert response.json["subscriptionMessage"]["updatedAt"] == ubble_fraud_check.updatedAt.isoformat()
        assert (
            response.json["subscriptionMessage"]["userMessage"]
            == "Ton document d'identité est en cours de vérification."
        )

        # ubble now confirms the status
        ubble_fraud_check.status = fraud_models.FraudCheckStatus.OK
        ubble_fraud_check.resultContent = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSED
        )
        pcapi.repository.repository.save(ubble_fraud_check)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] is None
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=True,
    )
    def test_underage_ubble_ok_turned_18(self, client):
        # User has already performed id check with Ubble for underage credit, 2 years ago
        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(years=2)):
            user = users_factories.UserFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=16, days=5),
                activity="Employé",
            )
            # 15-17: no phone validation

            # Perform profile completion
            fraud_factories.ProfileCompletionFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            # Perform first id check with Ubble
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "honor-statement"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

    @override_features(
        ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=True,
        ENABLE_UBBLE=True,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=False,
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
    )
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    @time_machine.travel("2022-09-08 12:45:13")
    def test_ubble_subscription_limited(self, client, age):
        birth_date = datetime.datetime.utcnow() - relativedelta(years=age + 1)
        birth_date += relativedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS - 1)
        # the user has:
        # 1. Email Validated
        # 2. Phone Validated
        # 3. Profile Completed
        user_approching_birthday = users_factories.UserFactory(
            dateOfBirth=birth_date,
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user_approching_birthday, eligibilityType=user_approching_birthday.eligibility
        )

        client.with_token(user_approching_birthday.email)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        user_not_eligible_for_ubble = users_factories.UserFactory(
            dateOfBirth=birth_date + relativedelta(days=10),
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user_not_eligible_for_ubble, eligibilityType=user_not_eligible_for_ubble.eligibility
        )

        client.with_token(user_not_eligible_for_ubble.email)
        response = client.get("/native/v1/subscription/next_step")
        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "maintenance"
        assert response.json["allowedIdentityCheckMethods"] == []
        assert response.json["maintenancePageType"] == "without-dms"
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] == {
            "callToAction": None,
            "popOverIcon": "CLOCK",
            "updatedAt": None,
            "userMessage": "La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite.",
        }

    @override_features(ENABLE_UBBLE=True)
    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_ubble_restart_workflow(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        ubble_content = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.INITIATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            resultContent=ubble_content,
            status=fraud_models.FraudCheckStatus.STARTED,
        )

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/next_step")
        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None


class StepperTest:
    def setup_method(self):
        self.phone_validation_step = {
            "name": "phone-validation",
            "title": "Numéro de téléphone",
            "subtitle": None,
        }
        self.profile_completion_step = {
            "name": "profile-completion",
            "title": "Profil",
            "subtitle": None,
        }
        self.identity_check_step = {
            "name": "identity-check",
            "title": "Identification",
            "subtitle": None,
        }
        self.honor_statement_step = {
            "name": "honor-statement",
            "title": "Confirmation",
            "subtitle": None,
        }

        self.all_steps = {
            "phone_validation_step": self.phone_validation_step,
            "profile_completion_step": self.profile_completion_step,
            "identity_check_step": self.identity_check_step,
            "honor_statement_step": self.honor_statement_step,
        }

    def get_step(self, step_name, completion_state):
        step = self.all_steps[step_name]
        step["completionState"] = completion_state
        return step

    def should_contain_all_subscription_steps_for_18yo_user(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            isEmailValidated=True,
        )

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["subscriptionStepsToDisplay"] == [
            self.get_step("phone_validation_step", SubscriptionStepCompletionState.CURRENT.value),
            self.get_step("profile_completion_step", SubscriptionStepCompletionState.DISABLED.value),
            self.get_step("identity_check_step", SubscriptionStepCompletionState.DISABLED.value),
            self.get_step("honor_statement_step", SubscriptionStepCompletionState.DISABLED.value),
        ]
        assert response.json["title"] == f"C'est très rapide{u_nbsp}!"
        assert response.json["subtitle"] == f"Pour débloquer tes 300€ tu dois suivre les étapes suivantes{u_nbsp}:"

    def should_contain_all_subscription_steps_for_15yo_user(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=15, months=5),
            isEmailValidated=True,
        )

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200

        assert response.json["subscriptionStepsToDisplay"] == [
            self.get_step("profile_completion_step", SubscriptionStepCompletionState.CURRENT.value),
            self.get_step("identity_check_step", SubscriptionStepCompletionState.DISABLED.value),
            self.get_step("honor_statement_step", SubscriptionStepCompletionState.DISABLED.value),
        ]
        assert response.json["title"] == f"C'est très rapide{u_nbsp}!"
        assert response.json["subtitle"] == f"Pour débloquer tes 20€ tu dois suivre les étapes suivantes{u_nbsp}:"

    def should_not_contain_id_check_in_steps_if_ubble_or_dms_done_for_underage(self, client):
        user = users_factories.UnderageBeneficiaryFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.json["subscriptionStepsToDisplay"] == [
            self.get_step("phone_validation_step", SubscriptionStepCompletionState.CURRENT.value),
            self.get_step("profile_completion_step", SubscriptionStepCompletionState.DISABLED.value),
            self.get_step("honor_statement_step", SubscriptionStepCompletionState.DISABLED.value),
        ]

    def should_contain_id_check_in_steps_if_educonnect_done_for_underage(self, client):
        user = users_factories.ExUnderageBeneficiaryFactory()

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=datetime.datetime.utcnow() - relativedelta(years=1),
        )

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.json["subscriptionStepsToDisplay"] == [
            self.get_step("phone_validation_step", SubscriptionStepCompletionState.CURRENT.value),
            self.get_step("profile_completion_step", SubscriptionStepCompletionState.DISABLED.value),
            self.get_step("identity_check_step", SubscriptionStepCompletionState.DISABLED.value),
            self.get_step("honor_statement_step", SubscriptionStepCompletionState.DISABLED.value),
        ]

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=False,
    )
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def should_contain_maintenance_page_type_without_dms(self, client, age):
        user = users_factories.BaseUserFactory(age=age)

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["allowedIdentityCheckMethods"] == []
        assert response.json["maintenancePageType"] == "without-dms"

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18=True,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=True,
    )
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def should_contain_maintenance_page_type_with_dms(self, client, age):
        user = users_factories.BaseUserFactory(age=age)

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["allowedIdentityCheckMethods"] == []
        assert response.json["maintenancePageType"] == "with-dms"

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=True,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=False,
    )
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def should_not_contain_maintenance_page_type(self, client, age):
        user = users_factories.BaseUserFactory(age=age)

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None

    @pytest.mark.parametrize(
        "reason_code",
        [
            fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
            fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
            fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
            fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
            fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
            fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
            fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY,
            fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA,
            fraud_models.FraudReasonCode.DOCUMENT_DAMAGED,
            fraud_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
            fraud_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
        ],
    )
    def should_have_subtitle_for_id_check_when_ubble_retryable(self, client, reason_code):
        user = fraud_factories.UserEligibleAtIdentityCheckStepFactory()

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.AGE18,
            reasonCodes=[reason_code],
        )

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.json["subscriptionStepsToDisplay"] == [
            self.get_step("phone_validation_step", SubscriptionStepCompletionState.COMPLETED.value),
            self.get_step("profile_completion_step", SubscriptionStepCompletionState.COMPLETED.value),
            {
                "name": "identity-check",
                "title": "Identification",
                "subtitle": ubble_models.UBBLE_CODE_ERROR_MAPPING[reason_code].retryable_action_hint,
                "completionState": SubscriptionStepCompletionState.RETRY.value,
            },
            self.get_step("honor_statement_step", SubscriptionStepCompletionState.DISABLED.value),
        ]

    def should_contain_identity_check_methods(self, client):
        user = users_factories.EligibleUnderageFactory()

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")
        assert "educonnect" in response.json["allowedIdentityCheckMethods"]

    def should_have_subtitle_for_profile_when_autocompleted(self, client):
        # A user was activated at 17 yo and is now 18 yo
        a_year_ago = datetime.datetime.utcnow() - relativedelta(years=1, months=1)
        with time_machine.travel(a_year_ago):
            user = users_factories.BeneficiaryFactory(age=17)

        assert user.age == 18

        # The user has completed the phone validation step
        fraud_factories.PhoneValidationFraudCheckFactory(user=user)
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.json["subscriptionStepsToDisplay"] == [
            self.get_step("phone_validation_step", SubscriptionStepCompletionState.COMPLETED.value),
            {
                "completionState": SubscriptionStepCompletionState.CURRENT.value,
                "name": "profile-completion",
                "title": "Profil",
                "subtitle": "Confirme tes informations",
            },
            self.get_step("honor_statement_step", SubscriptionStepCompletionState.DISABLED.value),
        ]

    def should_not_have_subtitle_for_profile_when_done(self, client):
        # A user was activated at 17 yo and is now 18 yo
        a_year_ago = datetime.datetime.utcnow() - relativedelta(years=1, months=1)
        with time_machine.travel(a_year_ago):
            user = users_factories.BeneficiaryFactory(age=17)

        # The user has completed the phone validation step
        fraud_factories.PhoneValidationFraudCheckFactory(user=user)
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        # The user has completed the profile completion step
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.json["subscriptionStepsToDisplay"] == [
            self.get_step("phone_validation_step", SubscriptionStepCompletionState.COMPLETED.value),
            self.get_step("profile_completion_step", SubscriptionStepCompletionState.COMPLETED.value),
            self.get_step("honor_statement_step", SubscriptionStepCompletionState.CURRENT.value),
        ]

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_next_subscription(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        client.with_token(user.email)

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "phone-validation"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_next_subscription_test_profile_completion(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        client.with_token(user.email)

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert not response.json["hasIdentityCheckPending"]
        assert response.json["subscriptionMessage"] is None

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=True,
    )
    @time_machine.travel("2022-09-08 11:54:22")
    def test_next_subscription_maintenance_page(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=15, months=5),
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        # User completed profile
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        client.with_token(user.email)

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "maintenance"
        assert response.json["allowedIdentityCheckMethods"] == []
        assert response.json["maintenancePageType"] == "with-dms"
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] == {
            "callToAction": None,
            "messageSummary": None,
            "popOverIcon": "CLOCK",
            "updatedAt": None,
            "userMessage": "La vérification d'identité est "
            "momentanément indisponible. L'équipe "
            "du pass Culture met tout en oeuvre "
            "pour la rétablir au plus vite.",
        }

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    @pytest.mark.parametrize(
        "fraud_check_status,reason_code,ubble_status,next_step,pending_idcheck,subscription_message",
        [
            (
                fraud_models.FraudCheckStatus.STARTED,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.INITIATED,
                "identity-check",
                False,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.PENDING,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSING,
                "honor-statement",
                True,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.OK,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                "honor-statement",
                False,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.KO,
                fraud_models.FraudReasonCode.AGE_TOO_OLD,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                None,
                False,
                {
                    "callToAction": None,
                    "messageSummary": None,
                    "popOverIcon": "ERROR",
                    "userMessage": "Ton dossier a été refusé\xa0: tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
                },
            ),
            (
                fraud_models.FraudCheckStatus.CANCELED,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
                "identity-check",
                False,
                None,
            ),
            (
                fraud_models.FraudCheckStatus.SUSPICIOUS,
                fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                "identity-check",  # User can retry
                False,
                {
                    "callToAction": {
                        "callToActionIcon": "RETRY",
                        "callToActionLink": "passculture://verification-identite",
                        "callToActionTitle": "Réessayer la vérification de mon identité",
                    },
                    "messageSummary": "Tu n’as pas déposé le bon type de document.",
                    "popOverIcon": None,
                    "userMessage": "Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarches-simplifiees.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité.",
                },
            ),
        ],
    )
    @override_features(ENABLE_UBBLE=True)
    @time_machine.travel("2022-09-08 12:01:12")
    def test_next_subscription_test_ubble(
        self, client, fraud_check_status, reason_code, ubble_status, next_step, pending_idcheck, subscription_message
    ):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            activity="Étudiant",
        )

        client.with_token(user.email)

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "phone-validation"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform phone validation
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform profile completion
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform first id check with Ubble
        ubble_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_check_status,
            reasonCodes=[reason_code],
            resultContent=fraud_factories.UbbleContentFactory(status=ubble_status),
        )
        if subscription_message:
            subscription_message["updatedAt"] = ubble_fraud_check.updatedAt.isoformat()

        # Check next step: only a single non-aborted Ubble identification is allowed
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == next_step
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] == pending_idcheck
        assert response.json["subscriptionMessage"] == subscription_message

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=True,
    )
    @time_machine.travel("2022-09-08 12:39:04")
    def test_underage_not_ok_turned_18(self, client):
        # User has already performed id check with Ubble for underage credit (successfully or not), 2 years ago
        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(years=2)):
            user = users_factories.UserFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=16, days=5),
                activity="Employé",
            )
            # 15-17: no phone validation

            # Perform profile completion
            fraud_factories.ProfileCompletionFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            # Perform first id check with Ubble
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.KO,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

        # Now user turned 18, phone validation and profile completion are requested and Ubble identification is requested again
        # Process should not depend on Ubble result performed when underage
        client.with_token(user.email)

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "phone-validation"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform phone validation
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "profile-completion"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform profile completion
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        # Perform id check with Ubble
        ubble_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSING
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "honor-statement"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is True
        assert response.json["subscriptionMessage"] is None

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] is None
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is True
        assert response.json["subscriptionMessage"]["callToAction"] is None
        assert response.json["subscriptionMessage"]["popOverIcon"] == "CLOCK"
        assert response.json["subscriptionMessage"]["updatedAt"] == ubble_fraud_check.updatedAt.isoformat()
        assert (
            response.json["subscriptionMessage"]["userMessage"]
            == "Ton document d'identité est en cours de vérification."
        )

        # ubble now confirms the status
        ubble_fraud_check.status = fraud_models.FraudCheckStatus.OK
        ubble_fraud_check.resultContent = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSED
        )
        pcapi.repository.repository.save(ubble_fraud_check)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] is None
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=True,
    )
    def test_underage_ubble_ok_turned_18(self, client):
        # User has already performed id check with Ubble for underage credit, 2 years ago
        with time_machine.travel(datetime.datetime.utcnow() - relativedelta(years=2)):
            user = users_factories.UserFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=16, days=5),
                activity="Employé",
            )
            # 15-17: no phone validation

            # Perform profile completion
            fraud_factories.ProfileCompletionFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            # Perform first id check with Ubble
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "honor-statement"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

    @override_features(
        ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=True,
        ENABLE_UBBLE=True,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=False,
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
    )
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    @time_machine.travel("2022-09-08 12:45:13")
    def test_ubble_subscription_limited(self, client, age):
        birth_date = datetime.datetime.utcnow() - relativedelta(years=age + 1)
        birth_date += relativedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS - 1)
        # the user has:
        # 1. Email Validated
        # 2. Phone Validated
        # 3. Profile Completed
        user_approching_birthday = users_factories.UserFactory(
            dateOfBirth=birth_date,
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user_approching_birthday, eligibilityType=user_approching_birthday.eligibility
        )

        client.with_token(user_approching_birthday.email)
        response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None

        user_not_eligible_for_ubble = users_factories.UserFactory(
            dateOfBirth=birth_date + relativedelta(days=10),
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user_not_eligible_for_ubble, eligibilityType=user_not_eligible_for_ubble.eligibility
        )

        client.with_token(user_not_eligible_for_ubble.email)
        response = client.get("/native/v2/subscription/stepper")
        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "maintenance"
        assert response.json["allowedIdentityCheckMethods"] == []
        assert response.json["maintenancePageType"] == "without-dms"
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] == {
            "callToAction": None,
            "messageSummary": None,
            "popOverIcon": "CLOCK",
            "updatedAt": None,
            "userMessage": "La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite.",
        }

    @override_features(ENABLE_UBBLE=True)
    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_ubble_restart_workflow(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        ubble_content = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.INITIATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            resultContent=ubble_content,
            status=fraud_models.FraudCheckStatus.STARTED,
        )

        client.with_token(user.email)
        response = client.get("/native/v2/subscription/stepper")
        assert response.status_code == 200
        assert response.json["nextSubscriptionStep"] == "identity-check"
        assert response.json["allowedIdentityCheckMethods"] == ["ubble"]
        assert response.json["maintenancePageType"] is None
        assert response.json["hasIdentityCheckPending"] is False
        assert response.json["subscriptionMessage"] is None


class GetProfileTest:
    def test_get_profile(self, client):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check = fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/profile")

        content: fraud_models.ProfileCompletionContent = fraud_check.source_data()
        profile_content = response.json["profile"]

        assert response.status_code == 200
        assert profile_content["firstName"] == content.first_name
        assert profile_content["lastName"] == content.last_name
        assert profile_content["address"] == content.address
        assert profile_content["city"] == content.city
        assert profile_content["postalCode"] == content.postal_code
        assert profile_content["activity"] == content.activity
        assert profile_content["schoolType"] == content.school_type

    def test_get_profile_with_no_fraud_check(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/profile")

        assert response.status_code == 404

    def test_get_profile_with_obsolete_profile_info(self, client):
        user = users_factories.BeneficiaryGrant18Factory()
        content = fraud_factories.ProfileCompletionContentFactory()
        fraud_check = fraud_factories.ProfileCompletionFraudCheckFactory(
            resultContent=content, user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        fraud_check.resultContent["activity"] = "NOT_AN_ACTIVITY"

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/profile")

        assert response.status_code == 200
        assert response.json["profile"] is None

    def test_post_profile_then_get(self, client):
        user = users_factories.EligibleGrant18Factory()
        profile_data = {
            "firstName": "Lucy",
            "lastName": "Ellingson",
            "address": "Chez ma maman",
            "city": "Kennet",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        with time_machine.travel(datetime.datetime.utcnow() - datetime.timedelta(days=365)):
            client.with_token(user.email)
            client.post("/native/v1/subscription/profile", profile_data)

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/profile")

        assert response.status_code == 200
        assert response.json["profile"]["firstName"] == profile_data["firstName"]
        assert response.json["profile"]["lastName"] == profile_data["lastName"]
        assert response.json["profile"]["address"] == profile_data["address"]
        assert response.json["profile"]["city"] == profile_data["city"]
        assert response.json["profile"]["postalCode"] == profile_data["postalCode"]
        assert response.json["profile"]["activity"] == users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value
        assert response.json["profile"]["schoolType"] == users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL.value


class UpdateProfileTest:
    @override_features(ENABLE_UBBLE=True)
    def test_fulfill_profile(self, client):
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
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = users_models.User.query.get(user.id)
        assert not user.is_beneficiary
        assert user.firstName == "John"
        assert user.lastName == "Doe"
        assert user.address == "1 rue des rues"
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.schoolType == users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL
        assert user.phoneNumber == "+33609080706"

        assert len(push_testing.requests) == 2
        notification = push_testing.requests[0]

        assert notification["user_id"] == user.id
        assert not notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "77000"

        # Check that a PROFILE_COMPLETION fraud check is created
        profile_completion_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        ]
        assert len(profile_completion_fraud_checks) == 1
        profile_completion_fraud_check = profile_completion_fraud_checks[0]
        assert profile_completion_fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert profile_completion_fraud_check.reason == "Completed in application step"

    @override_features(ENABLE_UBBLE=True)
    def test_fulfill_profile_invalid_character(self, client):
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
            "firstName": "ჯონ",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 400

    @override_features(ENABLE_UBBLE=True)
    def test_fulfill_profile_empty_field(self, client):
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
            "firstName": " ",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 400

    @override_features(ENABLE_UBBLE=True)
    def test_fulfill_profile_missing_mandatory_field(self, client):
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
            "firstName": " ",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 400

    @override_features(ENABLE_UBBLE=True)
    def test_fulfill_profile_valid_character(self, client):
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
            "lastName": "àâçéèêîôœùûÀÂÇÉÈÊÎÔŒÙÛ-' ",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

    @override_features(ENABLE_UBBLE=True)
    def test_fulfill_profile_activation(self, client):
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=fraud_factories.DMSContentFactory(
                first_name="Alexandra", last_name="Stan", postal_code="75008"
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        profile_data = {
            "firstName": "John",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = users_models.User.query.get(user.id)
        assert user.firstName == "Alexandra"
        assert user.lastName == "Stan"
        assert user.has_beneficiary_role

        assert len(push_testing.requests) == 3
        notification = push_testing.requests[0]
        assert notification["user_id"] == user.id
        assert notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "75008"


class ActivityTypesTest:
    @pytest.mark.parametrize("age", (15, 16, 17, 18))
    def test_get_activity_types(self, client, age):
        user = users_factories.BaseUserFactory(age=age)
        client.with_token(user.email)
        response = client.get("/native/v1/subscription/activity_types")

        expected_response = {
            "activities": [
                {
                    "id": "HIGH_SCHOOL_STUDENT",
                    "label": "Lycéen",
                    "description": None,
                },
                {"id": "STUDENT", "label": "Étudiant", "description": None},
                {"id": "EMPLOYEE", "label": "Employé", "description": None},
                {"id": "APPRENTICE", "label": "Apprenti", "description": None},
                {"id": "APPRENTICE_STUDENT", "label": "Alternant", "description": None},
                {
                    "id": "VOLUNTEER",
                    "label": "Volontaire",
                    "description": "En service civique",
                },
                {
                    "id": "INACTIVE",
                    "label": "Inactif",
                    "description": "En incapacité de travailler",
                },
                {
                    "id": "UNEMPLOYED",
                    "label": "Demandeur d'emploi",
                    "description": "En recherche d'emploi",
                },
            ],
        }
        if age < 18:
            expected_response["activities"].insert(
                0,
                {
                    "id": "MIDDLE_SCHOOL_STUDENT",
                    "label": "Collégien",
                    "description": None,
                },
            )
        assert response.status_code == 200
        assert response.json == expected_response


class HonorStatementTest:
    @pytest.mark.parametrize(
        "age,eligibility_type",
        [
            (15, users_models.EligibilityType.UNDERAGE),
            (16, users_models.EligibilityType.UNDERAGE),
            (17, users_models.EligibilityType.UNDERAGE),
            (18, users_models.EligibilityType.AGE18),
        ],
    )
    def test_create_honor_statement_fraud_check(self, client, age, eligibility_type):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age, days=10))

        client.with_token(user.email)

        response = client.post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT
        ).first()

        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.reason == "statement from /subscription/honor_statement endpoint"
        assert fraud_check.eligibilityType == eligibility_type
        assert fraud_check.eligibilityType == eligibility_type
