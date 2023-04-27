from flask import url_for
import pytest

from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories

from .helpers import html_parser
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class SuspendUserTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.users.suspend_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.SUSPEND_USER

    def test_suspend_beneficiary_user(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryGrant18Factory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT.name,
                "comment": "Le jeune a mis en ligne des annonces de vente le lendemain",
            },
        )

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_v3_web.public_accounts.get_public_account", user_id=user.id, _external=True
        )

        assert not user.isActive
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_SUSPENDED
        assert user.action_history[0].authorUser == legit_user
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].extraData["reason"] == users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT.value
        assert user.action_history[0].comment == "Le jeune a mis en ligne des annonces de vente le lendemain"

    def test_suspend_pro_user(self, authenticated_client, legit_user):
        user = offerers_factories.UserOffererFactory().user

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_USURPATION_PRO.name,
                "comment": "",  # optional, keep empty
            },
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.pro_user.get", user_id=user.id, _external=True)

        assert not user.isActive
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_SUSPENDED
        assert user.action_history[0].authorUser == legit_user
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].extraData["reason"] == users_constants.SuspensionReason.FRAUD_USURPATION_PRO.value
        assert user.action_history[0].comment is None

    def test_suspend_without_reason(self, authenticated_client, legit_user):
        user = users_factories.UnderageBeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form={"reason": "", "comment": ""})

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_v3_web.public_accounts.get_public_account", user_id=user.id, _external=True
        )

        redirected_response = authenticated_client.get(response.location)
        assert "Les données envoyées sont invalides" in html_parser.extract_alert(redirected_response.data)

        assert user.isActive
        assert len(user.action_history) == 0


class UnsuspendUserTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.users.unsuspend_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.UNSUSPEND_USER

    def test_unsuspend_beneficiary_user(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form={"comment": ""})

        assert response.status_code == 303
        assert response.location == url_for(
            "backoffice_v3_web.public_accounts.get_public_account", user_id=user.id, _external=True
        )

        assert user.isActive
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_UNSUSPENDED
        assert user.action_history[0].authorUser == legit_user
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].comment is None

    def test_unsuspend_pro_user(self, authenticated_client, legit_user):
        user = users_factories.ProFactory(isActive=False)
        offerers_factories.UserOffererFactory(user=user)

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, form={"comment": "Réactivé suite à contact avec l'AC"}
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.pro_user.get", user_id=user.id, _external=True)

        assert user.isActive
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_UNSUSPENDED
        assert user.action_history[0].authorUser == legit_user
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].comment == "Réactivé suite à contact avec l'AC"
