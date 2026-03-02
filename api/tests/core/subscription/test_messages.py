import datetime

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.utils import date as date_utils
from pcapi.utils.string import u_nbsp


@pytest.mark.usefixtures("db_session")
class SubscriptionMessagesTest:
    def test_build_duplicate_error_message_duplicate_user_ine(self):
        # Duplicate user
        users_factories.UserFactory(ineHash="some_HASH", email="lucille.ellingson@example.com")

        user = users_factories.UserFactory()
        content = subscription_factories.EduconnectContentFactory(ine_hash="some_HASH")
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.EDUCONNECT, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé aux identifiants ÉduConnect que tu as fournis. "
            "Connecte-toi avec l’adresse mail luc***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.subscription_models.FraudReasonCode.DUPLICATE_INE, content
        )

        assert message == expected_message

    def test_build_duplicate_error_message_duplicate_user_name_and_birth_date(self):
        # Duplicate user
        users_factories.BeneficiaryGrant18Factory(
            firstName="Lucille",
            lastName="Ellingson",
            email="lucille.ellingson@example.com",
            validatedBirthDate=datetime.date(year=2003, month=10, day=3),
        )

        user = users_factories.UserFactory()
        content = subscription_factories.UbbleContentFactory(
            birth_date="2003-10-03",
            first_name="Lucille",
            last_name="Ellingson",
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.UBBLE, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom. "
            "Connecte-toi avec l’adresse mail luc***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.subscription_models.FraudReasonCode.DUPLICATE_USER, content
        )

        assert message == expected_message

    def test_build_duplicate_error_message_duplicate_user_id_piece_number(self):
        # Duplicate user
        users_factories.BeneficiaryGrant18Factory(email="lucille.ellingson@example.com", idPieceNumber="123456789")

        user = users_factories.UserFactory()
        content = subscription_factories.DMSContentFactory(id_piece_number="123456789")
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.DMS, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé à ce numéro de pièce d’identité. "
            "Connecte-toi avec l’adresse mail luc***@example.com ou contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER, content
        )

        assert message == expected_message

    def test_build_duplicate_error_message_duplicate_user_not_found(self):
        user = users_factories.UserFactory()
        content = subscription_factories.DMSContentFactory(id_piece_number="123456789")
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.DMS, resultContent=content
        )

        expected_message = (
            "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé à ce numéro de pièce d’identité. "
            "Contacte le support si tu penses qu’il s’agit d’une erreur. "
            "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
        )

        message = messages.build_duplicate_error_message(
            user, messages.subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER, content
        )

        assert message == expected_message


@pytest.mark.usefixtures("db_session")
class StepperTest:
    def get_step(
        self,
        step: subscription_schemas.SubscriptionStep,
        step_completion_state: subscription_schemas.SubscriptionStepCompletionState,
        subtitle: str | None = None,
    ):
        return subscription_schemas.SubscriptionStepDetails(
            name=step,
            title=subscription_schemas.SubscriptionStepTitle[step.name],
            subtitle=subtitle,
            completion_state=step_completion_state,
        )

    def test_get_stepper_title_18_yo(self):
        user = users_factories.EligibleGrant18Factory()
        assert messages.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        ) == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    @time_machine.travel("2025-03-03")
    def test_get_stepper_title_pre_decree_18_yo(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=18)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        title_and_subtitle = messages.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert title_and_subtitle == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 300€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    def test_get_stepper_title_underage_user(self):
        user = users_factories.EligibleUnderageFactory(age=17)
        assert messages.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        ) == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 50€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    @time_machine.travel("2025-03-03")
    def test_get_stepper_title_pre_decree_17_yo(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=17)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        title_and_subtitle = messages.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert title_and_subtitle == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 30€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    def test_get_stepper_title_18_yo_retrying_ubble(self):
        user = users_factories.EligibleGrant18Factory(
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE],
        )

        assert messages.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        ) == subscription_schemas.SubscriptionStepperDetails(
            title="La vérification de ton identité a échoué",
            subtitle=None,
        )

    def test_get_subscription_steps_to_display_for_18yo_has_not_started(self):
        user = users_factories.EligibleGrant18Factory()

        steps = messages.get_subscription_steps_to_display(user, subscription_api.get_user_subscription_state(user))

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_validated_phone(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )

        steps = messages.get_subscription_steps_to_display(user, subscription_api.get_user_subscription_state(user))

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_completed_profile(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )

        steps = messages.get_subscription_steps_to_display(user, subscription_api.get_user_subscription_state(user))

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_ubble_issue(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_EXPIRED],
        )

        steps = messages.get_subscription_steps_to_display(user, subscription_api.get_user_subscription_state(user))

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.RETRY,
                subtitle="Réessaie avec un autre document d’identité valide",
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_completed_id_check(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
        )

        steps = messages.get_subscription_steps_to_display(user, subscription_api.get_user_subscription_state(user))

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_completed_everything(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
        )

        steps = messages.get_subscription_steps_to_display(user, subscription_api.get_user_subscription_state(user))

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_with_15_17_profile(self):
        user = users_factories.EligibleGrant18Factory()
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE, dateCreated=year_when_user_was_17
        )

        steps = messages.get_subscription_steps_to_display(user, subscription_api.get_user_subscription_state(user))

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
                subtitle=subscription_schemas.PROFILE_COMPLETION_STEP_EXISTING_DATA_SUBTITLE,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]
