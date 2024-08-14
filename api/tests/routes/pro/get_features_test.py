import pytest

from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


class Returns200Test:
    # 1. user
    # 2. session
    # 3. DELETE from user_session
    # 4. user
    # 5. INSERT INTO user
    # 6. user
    # 7. user
    # 8. UPDATE user
    # 9. user
    # 10. booking
    # 11. favorite
    # 12. deposit
    # 13. beneficiary_fraud_review
    # 14. action_history
    # 15. user_offerer
    # 16. user_pro_new_nav_state
    # 17. SELECT EXISTS user_offerer
    # 18. user_session
    # 19. user
    # 20. feature
    expected_num_queries = 20

    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in(self, client):
        # given
        user = users_factories.UserFactory()

        # when
        with assert_num_queries(self.expected_num_queries):
            response = client.with_session_auth(user.email).get("/features")
            assert response.status_code == 200

        # then
        feature_name_keys = [feature_dict["nameKey"] for feature_dict in response.json]
        assert "SYNCHRONIZE_ALLOCINE" in feature_name_keys

    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, client):
        # when
        with assert_num_queries(1):  # feature
            response = client.get("/features")
            assert response.status_code == 200
