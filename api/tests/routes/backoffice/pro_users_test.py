import datetime
from unittest.mock import patch

from flask import url_for
import pytest

import pcapi.core.history.factories as history_factories
import pcapi.core.history.models as history_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.routes.backoffice.filters import format_date
from pcapi.utils import email as email_utils

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetProUserTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro_user.get"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class EmailValidationButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Valider l&#39;adresse email"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory(user__isEmailValidated=False).user
            return url_for("backoffice_web.pro_user.get", user_id=user.id)

        def test_button_when_can_add_one(self, authenticated_client):
            user = offerers_factories.UserOffererFactory(user__isEmailValidated=False).user
            response = authenticated_client.get(url_for("backoffice_web.pro_user.get", user_id=user.id))
            assert response.status_code == 200

            assert self.button_label in response.data.decode("utf-8")

            url = url_for("backoffice_web.pro_user.validate_pro_user_email", user_id=user.id)
            assert url in response.data.decode("utf-8")

        def test_no_button_if_validated_email(self, authenticated_client):
            user = offerers_factories.UserOffererFactory(
                user__isEmailValidated=True, user__validationToken="AZERTY1234"
            ).user
            response = authenticated_client.get(url_for("backoffice_web.pro_user.get", user_id=user.id))
            assert response.status_code == 200

            assert self.button_label not in response.data.decode("utf-8")

    class DeleteUserButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Supprimer le compte"

        @property
        def path(self):
            user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
            return url_for("backoffice_web.pro_user.get", user_id=user.id)

        def test_button_when_can_be_deleted(self, authenticated_client):
            user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
            url = url_for("backoffice_web.pro_user.delete", user_id=user.id)

            response = authenticated_client.get(url_for("backoffice_web.pro_user.get", user_id=user.id))

            assert response.status_code == 200
            assert self.button_label in response.data.decode("utf-8")
            assert url in response.data.decode("utf-8")

        def test_button_when_cannot_be_deleted_role(self, authenticated_client):
            user = users_factories.UserFactory(roles=[users_models.UserRole.PRO])
            url = url_for("backoffice_web.pro_user.delete", user_id=user.id)

            response = authenticated_client.get(url_for("backoffice_web.pro_user.get", user_id=user.id))

            assert response.status_code == 200
            assert self.button_label not in response.data.decode("utf-8")
            assert url not in response.data.decode("utf-8")

        def test_button_when_cannot_be_deleted_user_offerer(self, authenticated_client):
            user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
            offerers_factories.UserOffererFactory(user=user)
            url = url_for("backoffice_web.pro_user.delete", user_id=user.id)

            response = authenticated_client.get(url_for("backoffice_web.pro_user.get", user_id=user.id))

            assert response.status_code == 200
            assert self.button_label not in response.data.decode("utf-8")
            assert url not in response.data.decode("utf-8")

    class SuspendButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
        button_label = "Suspendre le compte"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory().user
            return url_for("backoffice_web.pro_user.get", user_id=user.id)

    class UnsuspendButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
        button_label = "Réactiver le compte"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory(user__isActive=False).user
            return url_for("backoffice_web.pro_user.get", user_id=user.id)

    def test_get_pro_user(self, authenticated_client):
        user = offerers_factories.UserOffererFactory(user__phoneNumber="+33638656565", user__postalCode="29000").user
        url = url_for(self.endpoint, user_id=user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)

        assert f"User ID : {str(user.id)} " in content
        assert user.firstName in content
        assert user.lastName.upper() in content
        assert user.email in content
        assert f"Tél : {user.phoneNumber} " in content
        assert f"Code postal : {user.postalCode} " in content
        assert f"Département : {user.departementCode} " in content
        assert "Email validé : Oui" in content

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Pro" in badges
        assert "Validé" in badges
        assert "Suspendu" not in badges

    def test_get_not_pro_user(self, authenticated_client):
        user = users_factories.BeneficiaryGrant18Factory()
        url = url_for(self.endpoint, user_id=user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.search_pro", _external=True)
        assert response.location == expected_url


class UpdateProUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.update_pro_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_update_pro_user(self, authenticated_client, legit_user):
        user_to_edit = offerers_factories.UserOffererFactory(user__postalCode="74000").user

        old_last_name = user_to_edit.lastName
        new_last_name = "La Fripouille"
        old_email = user_to_edit.email
        new_email = old_email + ".UPDATE  "
        expected_new_email = email_utils.sanitize_email(new_email)
        old_postal_code = user_to_edit.postalCode
        expected_new_postal_code = "75000"

        base_form = {
            "first_name": user_to_edit.firstName,
            "last_name": new_last_name,
            "email": new_email,
            "postal_code": expected_new_postal_code,
            "phone_number": user_to_edit.phoneNumber,
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.pro_user.get", user_id=user_to_edit.id, _external=True)
        assert response.location == expected_url

        history_url = url_for("backoffice_web.pro_user.get_details", user_id=user_to_edit.id)
        response = authenticated_client.get(history_url)

        user_to_edit = users_models.User.query.get(user_to_edit.id)
        assert user_to_edit.lastName == new_last_name
        assert user_to_edit.email == expected_new_email
        assert user_to_edit.postalCode == expected_new_postal_code

        content = html_parser.content_as_text(response.data)

        assert history_models.ActionType.INFO_MODIFIED.value in content
        assert f"{old_last_name} => {user_to_edit.lastName}" in content
        assert f"{old_email} => {user_to_edit.email}" in content
        assert f"{old_postal_code} => {user_to_edit.postalCode}" in content


class GetProUserHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro_user.get_details"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory().user
            return url_for("backoffice_web.pro_user.get_details", user_id=user.id)

    def test_get_history(self, authenticated_client, pro_user):
        action1 = history_factories.ActionHistoryFactory(
            user=pro_user, actionDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        )
        action2 = history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=2),
            actionType=history_models.ActionType.USER_SUSPENDED,
            user=pro_user,
            comment="Test de suspension",
            extraData={"reason": users_constants.SuspensionReason.FRAUD_USURPATION_PRO.value},
        )
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(rows) == 2

        assert rows[0]["Type"] == history_models.ActionType.USER_SUSPENDED.value
        assert rows[0]["Date/Heure"] == format_date(action2.actionDate, "Le %d/%m/%Y à %Hh%M")
        assert (
            rows[0]["Commentaire"]
            == f"{users_constants.SUSPENSION_REASON_CHOICES[users_constants.SuspensionReason.FRAUD_USURPATION_PRO]} {action2.comment}"
        )
        assert rows[0]["Auteur"] == action2.authorUser.full_name

        assert rows[1]["Type"] == history_models.ActionType.COMMENT.value
        assert rows[1]["Date/Heure"] == format_date(action1.actionDate, "Le %d/%m/%Y à %Hh%M")
        assert rows[1]["Commentaire"] == action1.comment
        assert rows[1]["Auteur"] == action1.authorUser.full_name

    def test_no_history(self, authenticated_client, pro_user):
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data, parent_class="history-tab-pane") == 0


class CommentProUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.comment_pro_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_add_comment(self, authenticated_client, legit_user, pro_user):
        comment = "J'aime les commentaires en français !"
        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id, form={"comment": comment})

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.pro_user.get", user_id=pro_user.id, _external=True)
        assert response.location == expected_url

        assert len(pro_user.action_history) == 1
        assert pro_user.action_history[0].user == pro_user
        assert pro_user.action_history[0].authorUser == legit_user
        assert pro_user.action_history[0].comment == comment

    def test_add_invalid_comment(self, authenticated_client, pro_user):
        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id, form={"comment": ""})

        assert response.status_code == 302
        assert not pro_user.action_history


class GetProUserOfferersTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro_user.get_details"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_get_user_offerers(self, authenticated_client, pro_user):
        user_offerer_validated = offerers_factories.UserOffererFactory(user=pro_user)
        user_offerer_new = offerers_factories.NotValidatedUserOffererFactory(user=pro_user)
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 200

        content = response.data.decode("utf-8")

        offerer_1 = user_offerer_validated.offerer
        offerer_2 = user_offerer_new.offerer

        assert str(offerer_1.id) in content
        assert offerer_1.name in content
        assert offerer_1.siren in content

        assert str(offerer_2.id) in content
        assert offerer_2.name in content
        assert offerer_2.siren in content

    def test_no_user_offerers(self, authenticated_client, pro_user):
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 200


class ValidateProEmailTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.validate_pro_user_email"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_validate_pro_user_email_ff_on(self, authenticated_client):
        pro_user = offerers_factories.NotValidatedUserOffererFactory(
            user__validationToken=False, user__isEmailValidated=False
        ).user
        assert not pro_user.isEmailValidated

        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id)
        assert response.status_code == 303
        assert pro_user.isEmailValidated

        response_redirect = authenticated_client.get(response.location)
        assert f"L&#39;email {pro_user.email} est validé !" in response_redirect.data.decode("utf-8")
        assert len(mails_testing.outbox) == 0


class DeleteProUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.delete"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
        history_factories.SuspendedUserActionHistoryFactory(user=user)
        user_id = user.id
        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.search_pro", _external=True)

        mails_api.delete_contact.called_once_with(user.email)
        DeleteBatchUserAttributesRequest.assert_called_once_with(user_id=user_id)
        delete_user_attributes_task.delay.assert_called_once_with("canary")
        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 0
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.userId == user_id).count() == 0

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_and_keep_email_in_mailing_List(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
        offerers_factories.VenueFactory(bookingEmail=user.email)
        history_factories.SuspendedUserActionHistoryFactory(user=user)
        user_id = user.id
        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.search_pro", _external=True)

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_called_once_with(user_id=user_id)
        delete_user_attributes_task.delay.assert_called_once_with("canary")
        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 0
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.userId == user_id).count() == 0

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_mismatch_email(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
        user_id = user.id
        history_factories.SuspendedUserActionHistoryFactory(user=user)

        form = {"email": "wrong_email@example.com"}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id, _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data) == "L'email saisi ne correspond pas à celui du compte"
        )

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_not_called()
        delete_user_attributes_task.delay.assert_not_called()
        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 1
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.userId == user_id).count() == 1

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_with_user_offerer(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
        offerers_factories.UserOffererFactory(user=user)
        user_id = user.id
        history_factories.SuspendedUserActionHistoryFactory(user=user)

        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id, _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(redirected_response.data) == "Le compte est rattaché à une structure"

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_not_called()
        delete_user_attributes_task.delay.assert_not_called()
        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 1
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.userId == user_id).count() == 1

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_with_wrong_role(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.UserFactory(roles=[users_models.UserRole.BENEFICIARY])
        user_id = user.id
        history_factories.SuspendedUserActionHistoryFactory(user=user)

        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id, _external=True)

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_not_called()
        delete_user_attributes_task.delay.assert_not_called()
        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 1
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.userId == user_id).count() == 1

    def test_delete_pro_user_with_related_objects(self, authenticated_client):
        user = users_factories.NonAttachedProFactory()
        offers_factories.MediationFactory(author=user)

        user_id = user.id

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form={"email": user.email})

        # ensure that it does not crash
        assert response.status_code == 303

        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 0
        assert offers_models.Mediation.query.one().authorId is None
