from unittest import mock

import pytest
from flask import url_for

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(scope="function", name="beneficiary_fraud_admin")
def beneficiary_fraud_admin_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.UserFactory(roles=["ADMIN"])
    backoffice_api.upsert_roles(user, {perm_models.Roles.FRAUDE_JEUNES})
    db.session.flush()
    return user


@pytest.fixture(scope="function", name="fraude_jeunes_admin")
def fraude_jeunes_admin_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.UserFactory(roles=["ADMIN"])
    backoffice_api.upsert_roles(user, {perm_models.Roles.FRAUDE_JEUNES})
    db.session.flush()
    return user


@pytest.fixture(scope="function", name="support_n2_admin")
def support_n2_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.UserFactory(roles=["ADMIN"])
    backoffice_api.upsert_roles(user, {perm_models.Roles.SUPPORT_N2})
    db.session.flush()
    return user


@pytest.fixture(scope="function", name="super_admin")
def super_admin_fixture(roles_with_permissions: None) -> users_models.User:
    user = users_factories.UserFactory(roles=["ADMIN"])
    backoffice_api.upsert_roles(user, {perm_models.Roles.ADMIN})
    db.session.flush()
    return user


class SuspendUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.users.suspend_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = {
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
    }

    def test_suspend_beneficiary_user(self, client, beneficiary_fraud_admin):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(
            client.with_bo_session_auth(beneficiary_fraud_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT.name,
                "comment": "Le jeune a mis en ligne des annonces de vente le lendemain",
                "clear_email": "",
            },
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

        assert not user.isActive
        assert "email.supprime" not in user.email
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_SUSPENDED
        assert user.action_history[0].authorUser == beneficiary_fraud_admin
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].extraData["reason"] == users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT.value
        assert user.action_history[0].comment == "Le jeune a mis en ligne des annonces de vente le lendemain"

    @pytest.mark.parametrize(
        "reason,cancel_bookings,cancel_event",
        [
            (users_constants.SuspensionReason.FRAUD_HACK, True, False),
            (users_constants.SuspensionReason.FRAUD_RESELL_PASS, True, True),
            (users_constants.SuspensionReason.FRAUD_RESELL_PRODUCT, True, True),
            (users_constants.SuspensionReason.FRAUD_SUSPICION, True, False),
            (users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER, True, True),
            (users_constants.SuspensionReason.UPON_USER_REQUEST, True, True),
            (users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP, False, False),
        ],
    )
    def test_cancel_booking_on_suspend(self, client, beneficiary_fraud_admin, reason, cancel_bookings, cancel_event):
        user = users_factories.BeneficiaryFactory()
        confirmed_booking = bookings_factories.BookingFactory(user=user)
        used_booking = bookings_factories.UsedBookingFactory(user=user)
        reimbursed_booking = bookings_factories.ReimbursedBookingFactory(user=user)
        event_booking = bookings_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        )

        response = self.post_to_endpoint(
            client.with_bo_session_auth(beneficiary_fraud_admin),
            user_id=user.id,
            form={
                "reason": reason.name,
                "comment": "Le jeune a mis en ligne des annonces de vente le lendemain",
                "clear_email": "",
            },
        )
        db.session.refresh(confirmed_booking)
        db.session.refresh(used_booking)
        db.session.refresh(reimbursed_booking)
        db.session.refresh(event_booking)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)
        assert used_booking.status == bookings_models.BookingStatus.USED
        assert reimbursed_booking.status == bookings_models.BookingStatus.REIMBURSED
        if cancel_bookings:
            assert confirmed_booking.status == bookings_models.BookingStatus.CANCELLED
        else:
            assert confirmed_booking.status == bookings_models.BookingStatus.CONFIRMED
        if cancel_event:
            assert event_booking.status == bookings_models.BookingStatus.CANCELLED
        else:
            assert event_booking.status == bookings_models.BookingStatus.CONFIRMED

    def test_suspend_public_user_and_clear_email(self, client, beneficiary_fraud_admin):
        user = users_factories.UserFactory()

        response = self.post_to_endpoint(
            client.with_bo_session_auth(beneficiary_fraud_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.UPON_USER_REQUEST.name,
                "comment": "Doublon",
                "clear_email": "on",
            },
        )

        assert response.status_code == 303

        assert not user.isActive
        assert user.email == f"{user.id}@email.supprime"
        assert len(user.action_history) == 1
        assert len(user.email_history) == 1

    def test_suspend_pro_user(self, client, pro_fraud_admin):
        user = offerers_factories.UserOffererFactory().user

        response = self.post_to_endpoint(
            client.with_bo_session_auth(pro_fraud_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_USURPATION_PRO.name,
                "comment": "",  # optional, keep empty
            },
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id)

        assert not user.isActive
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_SUSPENDED
        assert user.action_history[0].authorUser == pro_fraud_admin
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].extraData["reason"] == users_constants.SuspensionReason.FRAUD_USURPATION_PRO.value
        assert user.action_history[0].comment is None

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.UNDERAGE_BENEFICIARY],
            [users_models.UserRole.BENEFICIARY],
            [users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.BENEFICIARY],
            [users_models.UserRole.PRO, users_models.UserRole.BENEFICIARY],
        ],
    )
    def test_suspend_beneficiary_user_as_beneficiary_fraud(self, client, fraude_jeunes_admin, roles):
        user = users_factories.UserFactory(roles=roles)

        response = self.post_to_endpoint(
            client.with_bo_session_auth(fraude_jeunes_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_HACK.name,
                "comment": "",  # optional, keep empty
                "clear_email": "",
            },
        )

        assert response.status_code == 303
        assert not user.isActive

    def test_suspend_beneficiary_user_as_support_n2(self, client, support_n2_admin):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(
            client.with_bo_session_auth(support_n2_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_HACK.name,
                "comment": "",  # optional, keep empty
                "clear_email": "",
            },
        )

        assert response.status_code == 303
        assert not user.isActive

    def test_suspend_beneficiary_user_as_pro_fraud(self, client, pro_fraud_admin):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(
            client.with_bo_session_auth(pro_fraud_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_HACK.name,
                "comment": "",  # optional, keep empty
                "clear_email": "",
            },
        )

        assert response.status_code == 403

    def test_suspend_pro_user_as_beneficiary_fraud(self, client, beneficiary_fraud_admin):
        user = offerers_factories.UserOffererFactory().user

        response = self.post_to_endpoint(
            client.with_bo_session_auth(beneficiary_fraud_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_USURPATION_PRO.name,
                "comment": "",  # optional, keep empty
            },
        )

        assert response.status_code == 403

    def test_suspend_without_reason(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user.id,
            form={
                "reason": "",
                "comment": "",
                "clear_email": "",
            },
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

        redirected_response = authenticated_client.get(response.location)
        assert "Les données envoyées sont invalides" in html_parser.extract_alert(redirected_response.data)

        assert user.isActive
        assert len(user.action_history) == 0

    def test_suspend_admin_user(self, client, roles_with_permissions, super_admin):
        user = users_factories.AdminFactory(
            backoffice_profile__roles=[
                role
                for role in roles_with_permissions
                if role.name in (perm_models.Roles.SUPPORT_PRO.value, perm_models.Roles.SUPPORT_PRO_N2.value)
            ]
        )

        referer = url_for("backoffice_web.bo_users.get_bo_user", user_id=user.id)

        response = self.post_to_endpoint(
            client.with_bo_session_auth(super_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.END_OF_CONTRACT.name,
                "comment": "",  # optional, keep empty
            },
            headers={"referer": referer},
        )

        assert response.status_code == 303
        assert response.location == referer

        db.session.refresh(user)
        assert not user.isActive
        assert user.backoffice_profile
        assert not user.backoffice_profile.roles

        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_SUSPENDED
        assert user.action_history[0].authorUser == super_admin
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].extraData["reason"] == users_constants.SuspensionReason.END_OF_CONTRACT.value
        assert user.action_history[0].comment is None

        # ensure that admin page still does not crash
        assert client.with_bo_session_auth(super_admin).get(response.location).status_code == 200

    def test_suspend_admin_user_as_beneficiary_fraud_admin(
        self, client, roles_with_permissions, beneficiary_fraud_admin
    ):
        user = users_factories.AdminFactory(
            backoffice_profile__roles=[
                role for role in roles_with_permissions if role.name in (perm_models.Roles.FRAUDE_JEUNES.value,)
            ]
        )

        referer = url_for("backoffice_web.bo_users.get_bo_user", user_id=user.id)

        response = self.post_to_endpoint(
            client.with_bo_session_auth(beneficiary_fraud_admin),
            user_id=user.id,
            form={
                "reason": users_constants.SuspensionReason.END_OF_CONTRACT.name,
                "comment": "",  # optional, keep empty
            },
            headers={"referer": referer},
        )

        assert response.status_code == 403

        db.session.refresh(user)
        assert user.isActive
        assert user.backoffice_profile
        assert user.backoffice_profile.roles
        assert len(user.action_history) == 0

    def test_no_injection_in_flash_message(self, authenticated_client):
        # email should be filtered in POST endpoints but is still valid in database
        email = "<script>alert('coucou')</script>@example.com"
        user_id = users_factories.UserFactory(email=email).id

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user_id,
            form={
                "reason": users_constants.SuspensionReason.FRAUD_HACK.name,
                "comment": "Hacker",
            },
        )

        assert response.status_code == 303
        assert (
            # check that tags are escaped properly, since real tags are stripped in this helper
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"Le compte de l'utilisateur {email} ({user_id}) a été suspendu"
        )


class UnsuspendUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.users.unsuspend_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = {
        perm_models.Permissions.UNSUSPEND_USER,
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
    }

    def test_unsuspend_beneficiary_user(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory(isActive=False)

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form={"comment": ""})

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.public_accounts.get_public_account", user_id=user.id)

        assert user.isActive
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_UNSUSPENDED
        assert user.action_history[0].authorUser == legit_user
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].comment is None

    def test_unsuspend_beneficiary_to_anonymize(self, authenticated_client, legit_user):
        user = users_factories.BeneficiaryFactory(isActive=False)
        users_factories.GdprUserAnonymizationFactory(user=user)

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, form={"comment": ""}, follow_redirects=True
        )

        assert response.status_code == 200
        assert user.isActive
        assert len(user.action_history) == 1
        assert db.session.query(users_models.GdprUserAnonymization).count() == 0

    def test_unsuspend_pro_user(self, authenticated_client, legit_user):
        user = users_factories.ProFactory(isActive=False)
        offerers_factories.UserOffererFactory(user=user)

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, form={"comment": "Réactivé suite à contact avec l'AC"}
        )

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id)

        assert user.isActive
        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_UNSUSPENDED
        assert user.action_history[0].authorUser == legit_user
        assert user.action_history[0].user == user
        assert user.action_history[0].offererId is None
        assert user.action_history[0].venueId is None
        assert user.action_history[0].comment == "Réactivé suite à contact avec l'AC"

    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.UNDERAGE_BENEFICIARY],
            [users_models.UserRole.BENEFICIARY],
            [users_models.UserRole.NON_ATTACHED_PRO, users_models.UserRole.BENEFICIARY],
            [users_models.UserRole.PRO, users_models.UserRole.BENEFICIARY],
        ],
    )
    def test_unsuspend_beneficiary_user_as_beneficiary_fraud(self, client, fraude_jeunes_admin, roles):
        user = users_factories.UserFactory(isActive=False, roles=roles)

        response = self.post_to_endpoint(
            client.with_bo_session_auth(fraude_jeunes_admin),
            user_id=user.id,
            form={"comment": "Réactivé par la fraude jeunes"},
        )

        assert response.status_code == 303
        assert user.isActive

    def test_unsuspend_beneficiary_user_as_support_n2(self, client, support_n2_admin):
        user = users_factories.BeneficiaryFactory(isActive=False)

        response = self.post_to_endpoint(
            client.with_bo_session_auth(support_n2_admin),
            user_id=user.id,
            form={"comment": "Réactivé par le support N2"},
        )

        assert response.status_code == 403
        assert not user.isActive

    # When suspended, admin user loses ADMIN role
    @pytest.mark.parametrize("user_roles", [[users_models.UserRole.ADMIN], []])
    def test_unsuspend_admin_user(self, client, super_admin, user_roles):
        user = users_factories.AdminFactory(roles=user_roles, backoffice_profile__roles=[], isActive=False)

        response = self.post_to_endpoint(
            client.with_bo_session_auth(super_admin),
            user_id=user.id,
            form={"comment": "Test"},
        )

        assert response.status_code == 303

        db.session.refresh(user)
        assert user.isActive
        assert user.backoffice_profile
        assert not user.backoffice_profile.roles

        assert len(user.action_history) == 1
        assert user.action_history[0].actionType == history_models.ActionType.USER_UNSUSPENDED
        assert user.action_history[0].authorUser == super_admin
        assert user.action_history[0].user == user
        assert user.action_history[0].comment == "Test"


class GetBatchSuspendUsersFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.users.get_batch_suspend_users_form"
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    def test_get_batch_suspend_users_form(self, authenticated_client):
        with assert_num_queries(1):  # session
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
    endpoint = "backoffice_web.users.batch_suspend_users"
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    @pytest.mark.parametrize("separator", [",", ", ", "\n"])
    def test_batch_suspend_users(self, authenticated_client, separator):
        users = [
            users_factories.BeneficiaryFactory(age=17),
            users_factories.BeneficiaryFactory(),
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
        users = users_factories.BeneficiaryFactory.create_batch(2)
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
    endpoint = "backoffice_web.users.confirm_batch_suspend_users"
    needed_permission = perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS

    def test_confirm_batch_suspend_users(self, authenticated_client, legit_user):
        users = [
            users_factories.BeneficiaryFactory(age=17),
            users_factories.BeneficiaryFactory(),
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

        assert response.status_code == 303

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
        users = users_factories.BeneficiaryFactory.create_batch(2)
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

        assert response.status_code == 303
        redirected_response = authenticated_client.get(response.location)
        assert "2 comptes d'utilisateurs ont été suspendus" in html_parser.extract_alert(redirected_response.data)

        for booking in non_cancellable_bookings:
            assert booking.status != bookings_models.BookingStatus.CANCELLED
        for booking in cancellable_bookings:
            assert booking.status == bookings_models.BookingStatus.CANCELLED


class GetRedirectToBrevoUserPageTest(GetEndpointHelper):
    endpoint = "backoffice_web.users.redirect_to_brevo_user_page"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
    ]

    @mock.patch(
        "pcapi.core.mails.backends.testing.TestingBackend.get_contact_url", return_value="https://url/to/contact/12345"
    )
    def test_beneficiary_in_brevo(self, mocked_get_contact_url, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        user_id = user.id
        with assert_num_queries(2):  # session + get_user
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 302

        assert response.location == "https://url/to/contact/12345"

        mocked_get_contact_url.assert_called_once_with(user.email)

    def test_beneficiary_not_in_brevo(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        user_id = user.id
        with assert_num_queries(2):  # session + get_user
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 303

        assert response.location == url_for("backoffice_web.public_accounts.get_public_account", user_id=user_id)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"L'adresse {user.email} n'existe pas dans Brevo"
        )

    def test_user_does_not_exists(self, authenticated_client):
        with assert_num_queries(3):  # session + get_user + rollback
            response = authenticated_client.get(url_for(self.endpoint, user_id=0))
            assert response.status_code == 404

    @mock.patch(
        "pcapi.core.mails.backends.testing.TestingBackend.get_contact_url", return_value="https://url/to/contact/67890"
    )
    def test_pro_in_brevo(self, mocked_get_contact_url, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        user_id = user_offerer.user.id
        with assert_num_queries(2):  # session + get_user
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 302

        assert response.location == "https://url/to/contact/67890"

        mocked_get_contact_url.assert_called_once_with(user_offerer.user.email)

    def test_pro_not_in_brevo(self, authenticated_client):
        user_offerer = offerers_factories.UserOffererFactory()
        user_id = user_offerer.user.id
        with assert_num_queries(2):  # session + get_user
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 303

        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user_id)
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == f"L'adresse {user_offerer.user.email} n'existe pas dans Brevo"
        )
