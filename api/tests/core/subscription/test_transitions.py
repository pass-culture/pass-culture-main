import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


@pytest.mark.usefixtures("db_session")
class SubscriptionTransitionTest:
    def test_ensure_user_has_transitions_default_state(self):
        user = users_factories.UserFactory()
        user.validate_email()

        assert user.subscriptionState == users_models.SubscriptionState.email_validated
        assert user.is_subscriptionState_email_validated

    def test_ensure_factory_support_state(self):
        user = users_factories.UserFactory(subscriptionState=users_models.SubscriptionState.email_validated)
        user.validate_phone()

        assert user.subscriptionState == users_models.SubscriptionState.phone_validated
        assert user.is_subscriptionState_phone_validated()
