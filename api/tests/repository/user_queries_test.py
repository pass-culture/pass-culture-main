import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.repository.user_queries import find_pro_users_by_email_provider


class FindProUsersByEmailProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_pro_users_with_matching_email_provider(self):
        pro_user_with_matching_email = users_factories.ProFactory(email="pro_user@suspect.com", isActive=True)
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user_with_matching_email, offerer=offerer)

        pro_user_with_not_matching_email = users_factories.ProFactory(email="pro_user@example.com", isActive=True)
        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user_with_not_matching_email, offerer=offerer2)

        users = find_pro_users_by_email_provider("suspect.com")

        assert len(users) == 1
        assert users[0] == pro_user_with_matching_email

    @pytest.mark.usefixtures("db_session")
    def test_returns_only_pro_users_with_matching_email_provider(self):
        pro_user_with_matching_email = users_factories.ProFactory(
            email="pro_user_with_matching_email@suspect.com", isActive=True
        )
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user_with_matching_email, offerer=offerer)

        users_factories.UserFactory(email="not_pro_with_matching_email@suspect.com", isActive=True)

        users = find_pro_users_by_email_provider("suspect.com")

        assert len(users) == 1
        assert users[0] == pro_user_with_matching_email
