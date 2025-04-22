import enum

import transitions

from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud import repository as fraud_repository
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import eligibility_api
from pcapi.core.users import models as users_models


class SubscriptionStates(enum.Enum):
    EMAIL_VALIDATION = enum.auto()
    ADMIN_KO_REVIEW = enum.auto()
    BENEFICIARY = enum.auto()
    EX_BENEFICIARY = enum.auto()
    NOT_ELIGIBLE = enum.auto()
    PHONE_VALIDATION = enum.auto()
    FAILED_PHONE_VALIDATION = enum.auto()
    PROFILE_COMPLETION = enum.auto()
    IDENTITY_CHECK = enum.auto()
    IDENTITY_CHECK_RETRY = enum.auto()
    FAILED_IDENTITY_CHECK = enum.auto()
    HONOR_STATEMENT = enum.auto()
    WAITING_FOR_IDENTITY_CHECK = enum.auto()
    WAITING_FOR_MANUAL_REVIEW = enum.auto()
    SUBSCRIPTION_COMPLETED_BUT_NOT_BENEFICIARY_YET = enum.auto()


FINAL_STATES = [
    SubscriptionStates.ADMIN_KO_REVIEW,
    SubscriptionStates.BENEFICIARY,
    SubscriptionStates.EX_BENEFICIARY,
    SubscriptionStates.NOT_ELIGIBLE,
    SubscriptionStates.FAILED_PHONE_VALIDATION,
    SubscriptionStates.IDENTITY_CHECK_RETRY,
    SubscriptionStates.FAILED_IDENTITY_CHECK,
    SubscriptionStates.WAITING_FOR_IDENTITY_CHECK,
    SubscriptionStates.WAITING_FOR_MANUAL_REVIEW,
    SubscriptionStates.SUBSCRIPTION_COMPLETED_BUT_NOT_BENEFICIARY_YET,
]


class SubscriptionStateMachineTemplate:
    state: SubscriptionStates
    phone_validation_status: subscription_models.SubscriptionItemStatus | None = None
    identity_fraud_check: fraud_models.BeneficiaryFraudCheck | None = None
    identity_fraud_check_status: subscription_models.SubscriptionItemStatus | None = None

    def __init__(self, user: users_models.User):
        self.user = user
        self.eligibility = user.eligibility

    def set_phone_validation_status(self) -> None:
        from pcapi.core.subscription import api as subscription_api

        self.phone_validation_status = subscription_api.get_phone_validation_subscription_item(
            self.user, self.eligibility
        ).status

    def set_identity_fraud_check(self) -> None:
        from pcapi.core.subscription import api as subscription_api

        self.identity_fraud_check = fraud_repository.get_relevant_identity_fraud_check(self.user, self.eligibility)
        self.identity_fraud_check_status = subscription_api.get_identity_check_fraud_status(
            self.user, self.eligibility, self.identity_fraud_check
        )

    def is_eligible(self) -> bool:
        return bool(self.eligibility)

    def is_eligible_for_next_recredit_activation_steps(self) -> bool:
        return eligibility_api.is_eligible_for_next_recredit_activation_steps(self.user)

    def is_beneficiary(self) -> bool:
        return self.user.is_beneficiary

    def has_active_deposit(self) -> bool:
        return self.user.has_active_deposit

    def has_failed_phone_validation(self) -> bool:
        if not self.phone_validation_status:
            raise ValueError(f"Phone validation status of {self.user = } should not be None at {self.state = }")

        return self.phone_validation_status == subscription_models.SubscriptionItemStatus.KO

    def has_validated_phone_number(self) -> bool:
        if not self.phone_validation_status:
            raise ValueError(f"Phone validation status of {self.user = } should not be None at {self.state = }")

        return self.phone_validation_status not in [
            subscription_models.SubscriptionItemStatus.TODO,
            subscription_models.SubscriptionItemStatus.KO,
        ]

    def has_validated_email(self) -> bool:
        return bool(self.user.isEmailValidated)

    def has_admin_ko_review(self) -> bool:
        return fraud_repository.has_admin_ko_review(self.user)

    def has_completed_profile(self) -> bool:
        from pcapi.core.subscription import api as subscription_api

        if not self.eligibility:
            raise ValueError(f"Eligibility of {self.user = } should not be None at {self.state = }")

        return subscription_api.has_completed_profile_for_given_eligibility(self.user, self.eligibility)

    def is_identity_check_ok(self) -> bool:
        return self.identity_fraud_check_status == subscription_models.SubscriptionItemStatus.OK

    def is_identity_check_pending(self) -> bool:
        return self.identity_fraud_check_status == subscription_models.SubscriptionItemStatus.PENDING

    def has_failed_identity_check(self) -> bool:
        return self.identity_fraud_check_status in [
            subscription_models.SubscriptionItemStatus.KO,
            subscription_models.SubscriptionItemStatus.SUSPICIOUS,
        ]

    def can_retry_identity_check(self) -> bool:
        from pcapi.core.subscription import api as subscription_api

        if not self.identity_fraud_check:
            raise ValueError(f"Identity fraud check of {self.user = } should not be None at {self.state = }")

        return subscription_api.can_retry_identity_fraud_check(self.identity_fraud_check)

    def has_completed_honor_statement(self) -> bool:
        if not self.eligibility:
            raise ValueError(f"Eligibility of {self.user = } should not be None at {self.state = }")

        return bool(fraud_repository.get_completed_honor_statement(self.user, self.eligibility))

    def requires_manual_review_before_activation(self) -> bool:
        from pcapi.core.subscription import api as subscription_api

        if not self.identity_fraud_check:
            raise ValueError(f"Identity fraud check of {self.user = } should not be None at {self.state = }")

        return subscription_api.requires_manual_review_before_activation(self.user, self.identity_fraud_check)

    def proceed(self) -> bool:
        # see https://github.com/pytransitions/transitions#typing-support
        raise RuntimeError("function should be overridden by transitions.Machine")

    def proceed_to_current_state(self) -> SubscriptionStates:
        while self.state not in FINAL_STATES:
            went_to_next_state = self.proceed()
            if not went_to_next_state:
                break

        return self.state


class FreeSubscriptionStateMachine(SubscriptionStateMachineTemplate):
    excluded_states = [
        SubscriptionStates.PHONE_VALIDATION,
        SubscriptionStates.FAILED_PHONE_VALIDATION,
        SubscriptionStates.IDENTITY_CHECK,
        SubscriptionStates.IDENTITY_CHECK_RETRY,
        SubscriptionStates.FAILED_IDENTITY_CHECK,
        SubscriptionStates.WAITING_FOR_IDENTITY_CHECK,
        SubscriptionStates.WAITING_FOR_MANUAL_REVIEW,
        SubscriptionStates.HONOR_STATEMENT,
    ]

    def __init__(self, user: users_models.User):
        super().__init__(user)

        self.machine = transitions.Machine(
            model=self,
            states=[state for state in SubscriptionStates if state not in FreeSubscriptionStateMachine.excluded_states],
            initial=SubscriptionStates.EMAIL_VALIDATION,
            model_override=True,
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.BENEFICIARY,
            conditions=["has_validated_email", "is_beneficiary", "has_active_deposit"],
            unless="is_eligible_for_next_recredit_activation_steps",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.EX_BENEFICIARY,
            conditions=["has_validated_email", "is_beneficiary"],
            unless=["has_active_deposit", "is_eligible_for_next_recredit_activation_steps"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.NOT_ELIGIBLE,
            conditions="has_validated_email",
            unless="is_eligible",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.ADMIN_KO_REVIEW,
            conditions=["has_validated_email", "has_admin_ko_review"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.PROFILE_COMPLETION,
            conditions=["has_validated_email", "is_eligible"],
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.PROFILE_COMPLETION,
            SubscriptionStates.SUBSCRIPTION_COMPLETED_BUT_NOT_BENEFICIARY_YET,
            conditions="has_completed_profile",
        )


class UnderageSubscriptionStateMachine(SubscriptionStateMachineTemplate):
    excluded_states = [SubscriptionStates.PHONE_VALIDATION, SubscriptionStates.FAILED_PHONE_VALIDATION]

    def __init__(self, user: users_models.User):
        super().__init__(user)

        self.machine = transitions.Machine(
            model=self,
            states=[
                state for state in SubscriptionStates if state not in UnderageSubscriptionStateMachine.excluded_states
            ],
            initial=SubscriptionStates.EMAIL_VALIDATION,
            model_override=True,
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.BENEFICIARY,
            conditions=["has_validated_email", "is_beneficiary", "has_active_deposit"],
            unless="is_eligible_for_next_recredit_activation_steps",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.EX_BENEFICIARY,
            conditions=["has_validated_email", "is_beneficiary"],
            unless=["has_active_deposit", "is_eligible_for_next_recredit_activation_steps"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.NOT_ELIGIBLE,
            conditions="has_validated_email",
            unless="is_eligible",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.ADMIN_KO_REVIEW,
            conditions=["has_validated_email", "has_admin_ko_review"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.PROFILE_COMPLETION,
            conditions=["has_validated_email", "is_eligible"],
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.PROFILE_COMPLETION,
            SubscriptionStates.IDENTITY_CHECK,
            conditions="has_completed_profile",
            after="set_identity_fraud_check",
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.FAILED_IDENTITY_CHECK,
            conditions="has_failed_identity_check",
            unless="can_retry_identity_check",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.IDENTITY_CHECK_RETRY,
            conditions=["has_failed_identity_check", "can_retry_identity_check"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.HONOR_STATEMENT,
            conditions="is_identity_check_ok",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.HONOR_STATEMENT,
            conditions="is_identity_check_pending",
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.HONOR_STATEMENT,
            SubscriptionStates.WAITING_FOR_IDENTITY_CHECK,
            conditions=["has_completed_honor_statement", "is_identity_check_pending"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.HONOR_STATEMENT,
            SubscriptionStates.WAITING_FOR_MANUAL_REVIEW,
            conditions=[
                "has_completed_honor_statement",
                "is_identity_check_ok",
                "requires_manual_review_before_activation",
            ],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.HONOR_STATEMENT,
            SubscriptionStates.SUBSCRIPTION_COMPLETED_BUT_NOT_BENEFICIARY_YET,
            conditions=["has_completed_honor_statement", "is_identity_check_ok"],
        )


class EighteenSubscriptionStateMachine(SubscriptionStateMachineTemplate):
    def __init__(self, user: users_models.User):
        super().__init__(user)

        self.machine = transitions.Machine(
            model=self, states=SubscriptionStates, initial=SubscriptionStates.EMAIL_VALIDATION, model_override=True
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.BENEFICIARY,
            conditions=["has_validated_email", "is_beneficiary", "has_active_deposit"],
            unless="is_eligible_for_next_recredit_activation_steps",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.EX_BENEFICIARY,
            conditions=["has_validated_email", "is_beneficiary"],
            unless=["has_active_deposit", "is_eligible_for_next_recredit_activation_steps"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.NOT_ELIGIBLE,
            conditions="has_validated_email",
            unless="is_eligible",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.ADMIN_KO_REVIEW,
            conditions=["has_validated_email", "has_admin_ko_review"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.EMAIL_VALIDATION,
            SubscriptionStates.PHONE_VALIDATION,
            conditions=["has_validated_email", "is_eligible"],
            after="set_phone_validation_status",
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.PHONE_VALIDATION,
            SubscriptionStates.FAILED_PHONE_VALIDATION,
            conditions="has_failed_phone_validation",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.PHONE_VALIDATION,
            SubscriptionStates.PROFILE_COMPLETION,
            conditions="has_validated_phone_number",
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.PROFILE_COMPLETION,
            SubscriptionStates.IDENTITY_CHECK,
            conditions="has_completed_profile",
            after="set_identity_fraud_check",
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.FAILED_IDENTITY_CHECK,
            conditions="has_failed_identity_check",
            unless="can_retry_identity_check",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.IDENTITY_CHECK_RETRY,
            conditions=["has_failed_identity_check", "can_retry_identity_check"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.HONOR_STATEMENT,
            conditions="is_identity_check_ok",
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.IDENTITY_CHECK,
            SubscriptionStates.HONOR_STATEMENT,
            conditions="is_identity_check_pending",
        )

        self.machine.add_transition(
            "proceed",
            SubscriptionStates.HONOR_STATEMENT,
            SubscriptionStates.WAITING_FOR_IDENTITY_CHECK,
            conditions=["has_completed_honor_statement", "is_identity_check_pending"],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.HONOR_STATEMENT,
            SubscriptionStates.WAITING_FOR_MANUAL_REVIEW,
            conditions=[
                "has_completed_honor_statement",
                "is_identity_check_ok",
                "requires_manual_review_before_activation",
            ],
        )
        self.machine.add_transition(
            "proceed",
            SubscriptionStates.HONOR_STATEMENT,
            SubscriptionStates.SUBSCRIPTION_COMPLETED_BUT_NOT_BENEFICIARY_YET,
            conditions=["has_completed_honor_statement", "is_identity_check_ok"],
            unless="requires_manual_review_before_activation",
        )


def create_state_machine_to_current_state(user: users_models.User) -> SubscriptionStateMachineTemplate:
    state_machine = _create_user_relevant_state_machine(user)
    state_machine.proceed_to_current_state()
    return state_machine


def _create_user_relevant_state_machine(user: users_models.User) -> SubscriptionStateMachineTemplate:
    if user.is_18_or_above_eligible:
        return EighteenSubscriptionStateMachine(user)
    if user.is_underage_eligible:
        return UnderageSubscriptionStateMachine(user)
    return FreeSubscriptionStateMachine(user)
