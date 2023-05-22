from flask import url_for
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.models import db

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
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


class GetBatchSuspendUsersFormTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.users.get_batch_suspend_users_form"
    needed_permission = perm_models.Permissions.SUSPEND_USER

    def test_get_batch_suspend_users_form(self, authenticated_client):
        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class BatchSuspendUsersReturns400Helper(PostEndpointHelper):
    @pytest.mark.parametrize("reason", ["", "UNKNOWN_REASON"])
    @pytest.mark.parametrize("endpoint", ["batch_suspend_users", "confirm_batch_suspend_users"])
    def test_batch_suspend_users_invalid_reason(self, authenticated_client, endpoint, reason):
        user = users_factories.UserFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "reason": reason,
                "comment": "test",
                "user_ids": str(user.id),
            },
        )

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "user_ids,expected_error",
        [
            ("", "Information obligatoire"),
            ("101a", "Seuls les chiffres, espaces, tabulations, retours à la ligne et virgules sont autorisés"),
            ("101-", "Seuls les chiffres, espaces, tabulations, retours à la ligne et virgules sont autorisés"),
            ("101,abc", "Seuls les chiffres, espaces, tabulations, retours à la ligne et virgules sont autorisés"),
            ("101,200", "ID non trouvés : 200"),
            ("101,102", "ID correspondant à un utilisateur admin : 102 (admin@example.com)"),
            ("101,103", "ID correspondant à un utilisateur pro : 103 (pro@example.com)"),
        ],
    )
    @pytest.mark.parametrize("endpoint", ["batch_suspend_users", "confirm_batch_suspend_users"])
    def test_batch_suspend_users_invalid_user_ids(self, authenticated_client, endpoint, user_ids, expected_error):
        users_factories.UserFactory(id=101)
        users_factories.AdminFactory(id=102, email="admin@example.com")
        pro = users_factories.ProFactory(id=103, email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro)

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_SUSPICION.name,
                "comment": "test",
                "user_ids": user_ids,
            },
        )

        assert response.status_code == 400
        assert expected_error in html_parser.extract_warnings(response.data)


class BatchSuspendUsersTest(BatchSuspendUsersReturns400Helper):
    endpoint = "backoffice_v3_web.users.batch_suspend_users"
    needed_permission = perm_models.Permissions.SUSPEND_USER

    @pytest.mark.parametrize("separator", [",", ", ", "\n"])
    def test_batch_suspend_users(self, authenticated_client, separator):
        users = [
            users_factories.UnderageBeneficiaryFactory(),
            users_factories.BeneficiaryGrant18Factory(),
            users_factories.UserFactory(),
        ]

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT.name,
                "comment": "test",
                "user_ids": f"{users[0].id}{separator}{users[2].id}{separator}",
            },
        )

        assert response.status_code == 200
        text = html_parser.content_as_text(response.data)
        assert "2 utilisateurs seront suspendus." in text
        assert "0 réservation sera annulée." in text

    def test_batch_suspend_users_with_bookings(self, authenticated_client):
        users = users_factories.BeneficiaryGrant18Factory.create_batch(2)
        bookings_factories.UsedBookingFactory(user=users[0])
        bookings_factories.BookingFactory.create_batch(2, user=users[0])
        bookings_factories.ReimbursedBookingFactory(user=users[1])
        bookings_factories.BookingFactory(user=users[1])

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_SUSPICION.name,
                "comment": "",
                "user_ids": " ".join(str(user.id) for user in users),
            },
        )

        assert response.status_code == 200
        text = html_parser.content_as_text(response.data)
        assert "2 utilisateurs seront suspendus." in text
        assert "3 réservations seront annulées." in text


class ConfirmBatchSuspendUsersTest(BatchSuspendUsersReturns400Helper):
    endpoint = "backoffice_v3_web.users.confirm_batch_suspend_users"
    needed_permission = perm_models.Permissions.SUSPEND_USER

    def test_confirm_batch_suspend_users(self, authenticated_client, legit_user):
        users = [
            users_factories.UnderageBeneficiaryFactory(),
            users_factories.BeneficiaryGrant18Factory(),
            users_factories.UserFactory(),
        ]

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_HACK.name,
                "comment": "test",
                "user_ids": f"{users[0].id} {users[2].id}",
            },
        )

        assert response.status_code == 302

        for user in users:
            db.session.refresh(user)

        for user in (users[0], users[2]):
            assert not users[0].isActive
            assert users[0].suspension_reason == users_constants.SuspensionReason.FRAUD_HACK

            assert len(user.action_history) == 1
            assert user.action_history[0].actionType == history_models.ActionType.USER_SUSPENDED
            assert user.action_history[0].authorUser == legit_user
            assert user.action_history[0].user == user
            assert user.action_history[0].offererId is None
            assert user.action_history[0].venueId is None
            assert user.action_history[0].extraData["reason"] == users_constants.SuspensionReason.FRAUD_HACK.value
            assert user.action_history[0].comment == "test"

        assert users[1].isActive
        assert not users[1].suspension_reason
        assert not users[1].action_history

    def test_confirm_batch_suspend_users_cancels_bookings(self, authenticated_client):
        users = users_factories.BeneficiaryGrant18Factory.create_batch(2)
        non_cancellable_bookings = [
            bookings_factories.UsedBookingFactory(user=users[0]),
            bookings_factories.ReimbursedBookingFactory(user=users[1]),
        ]
        cancellable_bookings = bookings_factories.BookingFactory.create_batch(2, user=users[0])
        cancellable_bookings.append(bookings_factories.BookingFactory(user=users[1]))

        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_SUSPICION.name,
                "comment": "",
                "user_ids": " ".join(str(user.id) for user in users),
            },
        )

        assert response.status_code == 302
        redirected_response = authenticated_client.get(response.location)
        assert "2 comptes d'utilisateurs ont été suspendus" in html_parser.extract_alert(redirected_response.data)

        for booking in non_cancellable_bookings:
            assert booking.status != bookings_models.BookingStatus.CANCELLED
        for booking in cancellable_bookings:
            assert booking.status == bookings_models.BookingStatus.CANCELLED
