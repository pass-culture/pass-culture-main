import datetime
from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.core.finance import models as finance_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date
from pcapi.utils import date as date_utils
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

    # session + pro user data
    expected_num_queries = 2

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
            user = offerers_factories.UserOffererFactory(user__isEmailValidated=True).user
            response = authenticated_client.get(url_for("backoffice_web.pro_user.get", user_id=user.id))
            assert response.status_code == 200

            assert self.button_label not in response.data.decode("utf-8")

    class DeleteUserButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Supprimer le compte"

        @property
        def path(self):
            user = users_factories.NonAttachedProFactory()
            return url_for("backoffice_web.pro_user.get", user_id=user.id)

        def test_button_when_can_be_deleted(self, authenticated_client):
            user = users_factories.NonAttachedProFactory()
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
            user = users_factories.NonAttachedProFactory()
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

        with assert_num_queries(self.expected_num_queries):
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
        assert url_for("backoffice_web.users.redirect_to_brevo_user_page", user_id=user.id).encode() in response.data

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Pro" in badges
        assert "Validé" in badges
        assert "Suspendu" not in badges

    def test_get_not_pro_user(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()
        url = url_for(self.endpoint, user_id=user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        expected_url = url_for("backoffice_web.pro.search_pro")
        assert response.location == expected_url

    def test_get_pro_user_with_null_names(self, authenticated_client, db_session):
        pro_user = users_factories.ProFactory(firstName=None, lastName=None)
        url = url_for("backoffice_web.pro_user.get", user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200
            # does not crash


class UpdateProUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.update_pro_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_update_pro_user(self, authenticated_client, legit_user):
        pro_user = offerers_factories.UserOffererFactory(
            user__postalCode="74000",
            user__notificationSubscriptions={"marketing_push": False, "marketing_email": False},
        ).user

        old_last_name = pro_user.lastName
        new_last_name = "La Fripouille"
        old_email = pro_user.email
        new_email = old_email + ".UPDATE  "
        expected_new_email = email_utils.sanitize_email(new_email)
        old_postal_code = pro_user.postalCode
        new_postal_code = "75000"

        form_data = {
            "first_name": pro_user.firstName,
            "last_name": new_last_name,
            "email": new_email,
            "postal_code": new_postal_code,
            "phone_number": pro_user.phoneNumber,
            "marketing_email_subscription": "on",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id, form=form_data)
        assert response.status_code == 303

        db.session.refresh(pro_user)
        assert pro_user.lastName == new_last_name
        assert pro_user.email == expected_new_email
        assert pro_user.postalCode == new_postal_code
        assert pro_user.notificationSubscriptions["marketing_email"] is True
        assert pro_user.notificationSubscriptions["marketing_push"] is False

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.user == pro_user
        assert action.offererId is None
        assert action.extraData == {
            "modified_info": {
                "lastName": {"old_info": old_last_name, "new_info": pro_user.lastName},
                "email": {"old_info": old_email, "new_info": pro_user.email},
                "postalCode": {"old_info": old_postal_code, "new_info": pro_user.postalCode},
                "notificationSubscriptions.marketing_email": {"old_info": False, "new_info": True},
            }
        }

    def test_unsubscribe_from_marketing_emails(self, authenticated_client, legit_user):
        pro_user = offerers_factories.UserOffererFactory().user

        form_data = {
            "first_name": pro_user.firstName,
            "last_name": pro_user.lastName,
            "email": pro_user.email,
            "postal_code": pro_user.postalCode,
            "phone_number": pro_user.phoneNumber,
            # "marketing_email_subscription" not sent by the browser when not checked
        }

        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id, form=form_data)
        assert response.status_code == 303

        db.session.refresh(pro_user)
        assert pro_user.notificationSubscriptions["marketing_email"] is False

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.user == pro_user
        assert action.offererId is None
        assert action.extraData == {
            "modified_info": {"notificationSubscriptions.marketing_email": {"old_info": True, "new_info": False}}
        }

    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryFactory, users_factories.AdminFactory])
    def test_update_non_pro_user(self, authenticated_client, user_factory):
        user = user_factory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user.id,
            form={
                "first_name": "Hacked",
                "last_name": "Hacked",
                "email": user.email,
                "postal_code": user.postalCode,
                "phone_number": user.phoneNumber,
            },
        )
        assert response.status_code == 404
        assert "Hacked" not in user.full_name
        assert db.session.query(history_models.ActionHistory).count() == 0


class GetProUserHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro_user.get_details"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # session + user + actions + former user_offerer
    expected_num_queries = 4

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory().user
            return url_for("backoffice_web.pro_user.get_details", user_id=user.id)

    def test_get_history(self, authenticated_client, pro_user):
        action1 = history_factories.ActionHistoryFactory(
            user=pro_user, actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=5)
        )
        action2 = history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(minutes=2),
            actionType=history_models.ActionType.USER_SUSPENDED,
            user=pro_user,
            comment="Test de suspension",
            extraData={"reason": users_constants.SuspensionReason.FRAUD_USURPATION_PRO.value},
        )
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(rows) == 2

        assert rows[0]["Type"] == "Compte suspendu"
        assert rows[0]["Date/Heure"] == format_date(action2.actionDate, "%d/%m/%Y à %Hh%M")
        assert (
            rows[0]["Commentaire"]
            == f"{users_constants.SUSPENSION_REASON_CHOICES[users_constants.SuspensionReason.FRAUD_USURPATION_PRO]} {action2.comment}"
        )
        assert rows[0]["Auteur"] == action2.authorUser.full_name

        assert rows[1]["Type"] == "Commentaire interne"
        assert rows[1]["Date/Heure"] == format_date(action1.actionDate, "%d/%m/%Y à %Hh%M")
        assert rows[1]["Commentaire"] == action1.comment
        assert rows[1]["Auteur"] == action1.authorUser.full_name

    def test_no_history(self, authenticated_client, pro_user):
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data, parent_class="history-tab-pane") == 0

    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryFactory, users_factories.AdminFactory])
    def test_non_pro_user_history(self, authenticated_client, user_factory):
        user = user_factory()
        response = authenticated_client.get(url_for(self.endpoint, user_id=user.id))
        assert response.status_code == 404


class CommentProUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.comment_pro_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_add_comment(self, authenticated_client, legit_user, pro_user):
        comment = "J'aime les commentaires en français !"
        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id, form={"comment": comment})

        assert response.status_code == 303

        expected_url = url_for("backoffice_web.pro_user.get", user_id=pro_user.id)
        assert response.location == expected_url

        assert len(pro_user.action_history) == 1
        assert pro_user.action_history[0].user == pro_user
        assert pro_user.action_history[0].authorUser == legit_user
        assert pro_user.action_history[0].comment == comment

    def test_add_invalid_comment(self, authenticated_client, pro_user):
        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id, form={"comment": ""})

        assert response.status_code == 303
        assert not pro_user.action_history

    def test_add_comment_to_non_pro_user(self, authenticated_client):
        user = users_factories.UserFactory()

        response = self.post_to_endpoint(
            authenticated_client, user_id=user.id, form={"comment": "Commentaire interdit"}
        )

        assert response.status_code == 404
        assert len(user.action_history) == 0


class GetProUserOfferersTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro_user.get_details"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # session + user + actions + user_offerer objects
    expected_num_queries = 4

    def test_get_user_offerers(self, authenticated_client):
        pro_user = users_factories.ProFactory()
        offerer_1 = offerers_factories.UserOffererFactory(
            user=pro_user, dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=1)
        ).offerer
        offerer_2 = offerers_factories.NewUserOffererFactory(user=pro_user).offerer
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="user_offerers-tab-pane")
        assert len(rows) == 2

        assert rows[0]["ID de l'entité juridique"] == str(offerer_1.id)
        assert rows[0]["Statut du rattachement"] == "Validé"
        assert rows[0]["Statut entité juridique"] == "Validée"
        assert rows[0]["Nom"] == offerer_1.name
        assert rows[0]["SIREN"] == offerer_1.siren

        assert rows[1]["ID de l'entité juridique"] == str(offerer_2.id)
        assert rows[1]["Statut du rattachement"] == "Nouveau"
        assert rows[1]["Statut entité juridique"] == "Validée"
        assert rows[1]["Nom"] == offerer_2.name
        assert rows[1]["SIREN"] == offerer_2.siren

    def test_get_caledonian_user_offerers(self, authenticated_client):
        nc_offerer = offerers_factories.CaledonianOffererFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=nc_offerer).user
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="user_offerers-tab-pane")
        assert len(rows) == 1

        assert rows[0]["ID de l'entité juridique"] == str(nc_offerer.id)
        assert rows[0]["Statut du rattachement"] == "Validé"
        assert rows[0]["Statut entité juridique"] == "Validée"
        assert rows[0]["Nom"] == nc_offerer.name
        assert rows[0]["SIREN / RID7"] == nc_offerer.rid7

    def test_no_user_offerers(self, authenticated_client):
        pro_user = users_factories.ProFactory()
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data, parent_class="user_offerers-tab-pane") == 0

    def test_get_user_offerers_in_different_offerer_status(self, authenticated_client, pro_user):
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerers_factories.PendingOffererFactory())
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="user_offerers-tab-pane")
        assert len(rows) == 2

        assert rows[0]["Statut entité juridique"] == "Validée"
        assert rows[1]["Statut entité juridique"] == "En attente"


class ValidateProEmailTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.validate_pro_user_email"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_validate_pro_user_email_ff_on(self, authenticated_client):
        pro_user = offerers_factories.NewUserOffererFactory(user__isEmailValidated=False).user
        assert not pro_user.isEmailValidated

        response = self.post_to_endpoint(authenticated_client, user_id=pro_user.id)
        assert response.status_code == 303
        assert pro_user.isEmailValidated

        response_redirect = authenticated_client.get(response.location)
        assert f"L'email {pro_user.email} est validé !" in html_parser.content_as_text(response_redirect.data)
        assert len(mails_testing.outbox) == 0

    def test_validate_non_pro_user_email(self, authenticated_client):
        user = users_factories.UserFactory(isEmailValidated=False)
        assert not user.isEmailValidated

        response = self.post_to_endpoint(authenticated_client, user_id=user.id)
        assert response.status_code == 404
        assert not user.isEmailValidated


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
        user = users_factories.NonAttachedProFactory()
        history_factories.SuspendedUserActionHistoryFactory(user=user)
        user_id = user.id
        user_email = user.email
        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro.search_pro")

        mails_api.delete_contact.assert_called_once_with(user_email, True)
        DeleteBatchUserAttributesRequest.assert_called_once_with(user_id=user_id)
        delete_user_attributes_task.delay.assert_called_once_with("canary")
        assert db.session.query(users_models.User).filter(users_models.User.id == user_id).count() == 0
        assert (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.userId == user_id)
            .count()
            == 0
        )

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_and_keep_email_in_mailing_List(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.NonAttachedProFactory()
        offerers_factories.VenueFactory(bookingEmail=user.email)
        history_factories.SuspendedUserActionHistoryFactory(user=user)
        user_id = user.id
        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro.search_pro")

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_called_once_with(user_id=user_id)
        delete_user_attributes_task.delay.assert_called_once_with("canary")
        assert db.session.query(users_models.User).filter(users_models.User.id == user_id).count() == 0
        assert (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.userId == user_id)
            .count()
            == 0
        )

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_mismatch_email(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.NonAttachedProFactory()
        user_id = user.id
        history_factories.SuspendedUserActionHistoryFactory(user=user)

        form = {"email": "wrong_email@example.com"}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data) == "L'email saisi ne correspond pas à celui du compte"
        )

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_not_called()
        delete_user_attributes_task.delay.assert_not_called()
        assert db.session.query(users_models.User).filter(users_models.User.id == user_id).count() == 1
        assert (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.userId == user_id)
            .count()
            == 1
        )

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_with_user_offerer(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.NonAttachedProFactory()
        offerers_factories.UserOffererFactory(user=user)
        user_id = user.id
        history_factories.SuspendedUserActionHistoryFactory(user=user)

        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id)
        redirected_response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(redirected_response.data) == "Le compte est rattaché à une entité juridique"

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_not_called()
        delete_user_attributes_task.delay.assert_not_called()
        assert db.session.query(users_models.User).filter(users_models.User.id == user_id).count() == 1
        assert (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.userId == user_id)
            .count()
            == 1
        )

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryFactory, users_factories.AdminFactory])
    def test_delete_pro_user_with_wrong_role(
        self,
        delete_user_attributes_task,
        DeleteBatchUserAttributesRequest,
        mails_api,
        authenticated_client,
        user_factory,
    ):
        user = user_factory()
        user_id = user.id
        history_factories.SuspendedUserActionHistoryFactory(user=user)

        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user.id, form=form)

        assert response.status_code == 404

        mails_api.delete_contact.assert_not_called()
        DeleteBatchUserAttributesRequest.assert_not_called()
        delete_user_attributes_task.delay.assert_not_called()
        assert db.session.query(users_models.User).filter(users_models.User.id == user_id).count() == 1
        assert (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.userId == user_id)
            .count()
            == 1
        )

    def test_delete_pro_user_with_related_objects(self, authenticated_client):
        user = users_factories.NonAttachedProFactory()
        users_factories.FavoriteFactory(user=user)
        offers_factories.MediationFactory(author=user)

        user_id = user.id

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form={"email": user.email})

        # ensure that it does not crash
        assert response.status_code == 303

        assert db.session.query(users_models.User).filter(users_models.User.id == user_id).count() == 0
        assert db.session.query(users_models.Favorite).filter(users_models.Favorite.userId == user_id).count() == 0
        assert db.session.query(offers_models.Mediation).one().authorId is None

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_with_beneficiary_dependencies(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.BeneficiaryFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
        history_factories.SuspendedUserActionHistoryFactory(user=user)
        uaur_id = users_factories.LostCredentialsUpdateRequestFactory(user=user).id
        user_id = user.id
        deposit_id = user.deposits[0].id
        beneficiary_fraud_check_id = user.beneficiaryFraudChecks[0].id
        user_email = user.email
        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form, follow_redirects=True)

        assert response.status_code == 200

        mails_api.delete_contact.assert_called_once_with(user_email, True)
        DeleteBatchUserAttributesRequest.assert_called_once_with(user_id=user_id)
        delete_user_attributes_task.delay.assert_called_once_with("canary")
        assert db.session.query(users_models.User).filter(users_models.User.id == user_id).count() == 0
        assert db.session.query(finance_models.Deposit).filter(finance_models.Deposit.id == deposit_id).count() == 0
        assert (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter(subscription_models.BeneficiaryFraudCheck.id == beneficiary_fraud_check_id)
            .count()
            == 0
        )
        assert (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.userId == user_id)
            .count()
            == 0
        )
        assert (
            db.session.query(users_models.UserAccountUpdateRequest)
            .filter(users_models.UserAccountUpdateRequest.id == uaur_id)
            .one()
            .userId
            is None
        )
