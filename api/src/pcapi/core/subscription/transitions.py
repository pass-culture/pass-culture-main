import flask
import transitions

from pcapi.core.users import models as users_models


TRANSITIONS = [
    ["validate_email", users_models.SubscriptionState.account_created, users_models.SubscriptionState.email_validated],
    ["validate_phone", users_models.SubscriptionState.email_validated, users_models.SubscriptionState.phone_validated],
    [
        "validate_phone_failed",
        users_models.SubscriptionState.email_validated,
        users_models.SubscriptionState.phone_validation_ko,
    ],
    [
        "validate_profiling",
        users_models.SubscriptionState.phone_validated,
        users_models.SubscriptionState.user_profiling_validated,
    ],
    [
        "validate_profiling_failed",
        users_models.SubscriptionState.phone_validated,
        users_models.SubscriptionState.user_profiling_ko,
    ],
    [
        "submit_user_identity",
        [users_models.SubscriptionState.user_profiling_validated, users_models.SubscriptionState.phone_validated],
        users_models.SubscriptionState.identity_check_pending,
    ],
    [
        "validate_user_identity_15_17",
        users_models.SubscriptionState.identity_check_pending,
        users_models.SubscriptionState.beneficiary_15_17,
    ],
    [
        "validate_user_identity_18",
        users_models.SubscriptionState.identity_check_pending,
        users_models.SubscriptionState.beneficiary_18,
    ],
    ["admin_rejection", "*", users_models.SubscriptionState.rejected_by_admin],
]


def install_machine():
    flask.g.subscription_machine = transitions.Machine(  # pylint: disable=assigning-non-slot
        states=users_models.SubscriptionState,
        transitions=TRANSITIONS,
        model_attribute="subscriptionState",
        ignore_invalid_triggers=True,
    )
