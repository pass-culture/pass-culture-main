import datetime
from typing import Any

import pytest

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class PostUserNewProNavTest:
    def test_post_user_new_pro_nav(self, client: Any) -> None:
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(
            eligibilityDate=datetime.datetime.utcnow() - datetime.timedelta(days=1), newNavDate=None
        )
        user = pro_new_nav_state.user

        client = client.with_session_auth(user.email)

        response = client.post("/users/new-pro-nav")

        assert response.status_code == 204
        assert pro_new_nav_state.newNavDate

    def test_post_user_new_pro_nav_not_eligible_user(self, client: Any) -> None:
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(eligibilityDate=None, newNavDate=None)
        user = pro_new_nav_state.user

        client = client.with_session_auth(user.email)

        response = client.post("/users/new-pro-nav")

        assert response.status_code == 400
        assert not pro_new_nav_state.newNavDate
