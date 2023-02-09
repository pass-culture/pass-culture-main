import datetime

from flask import g
from flask import url_for
import pytest

from pcapi import settings
import pcapi.core.history.factories as history_factories
import pcapi.core.history.models as history_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.testing import assert_no_duplicated_queries
import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.routes.backoffice_v3.filters import format_date
import pcapi.utils.email as email_utils

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetProUserTest:
    endpoint = "backoffice_v3_web.pro_user.get"

    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.pro_user.get"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class EmailValidationButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Valider l'email"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory(user__isEmailValidated=False).user
            return url_for("backoffice_v3_web.pro_user.get", user_id=user.id)

        def test_button_when_can_add_one(self, authenticated_client):
            user = offerers_factories.UserOffererFactory(user__isEmailValidated=False).user
            response = authenticated_client.get(url_for("backoffice_v3_web.pro_user.get", user_id=user.id))
            assert response.status_code == 200

            assert self.button_label in response.data.decode("utf-8")
            print(response.data)
            assert f"{settings.PRO_URL}/inscription/validation/{user.validationToken}" in response.data.decode("utf-8")

        def test_no_button_if_validated_email(self, authenticated_client):
            user = offerers_factories.UserOffererFactory(
                user__isEmailValidated=True, user__validationToken="AZERTY1234"
            ).user
            response = authenticated_client.get(url_for("backoffice_v3_web.pro_user.get", user_id=user.id))
            assert response.status_code == 200

            assert self.button_label not in response.data.decode("utf-8")

    class SuspendButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.SUSPEND_USER
        button_label = "Suspendre le compte"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory().user
            return url_for("backoffice_v3_web.pro_user.get", user_id=user.id)

    class UnsuspendButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.SUSPEND_USER
        button_label = "Réactiver le compte"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory(user__isActive=False).user
            return url_for("backoffice_v3_web.pro_user.get", user_id=user.id)

    def test_get_pro_user(self, authenticated_client):  # type: ignore
        user = offerers_factories.UserOffererFactory(user__phoneNumber="+33638656565", user__postalCode="29000").user
        url = url_for("backoffice_v3_web.pro_user.get", user_id=user.id)

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

    def test_get_not_pro_user(self, authenticated_client):  # type: ignore
        user = users_factories.BeneficiaryGrant18Factory()
        url = url_for("backoffice_v3_web.pro_user.get", user_id=user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.search_pro", _external=True)
        assert response.location == expected_url


class UpdateProUserTest:
    class UnauthorizedTest(unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.pro_user.update_pro_user"
        endpoint_kwargs = {"user_id": 1}
        method = "post"
        form = {"first_name": "aaaaaaaaaaaaaaaaaaa"}

    def test_update_pro_user(self, client, legit_user):
        user_to_edit = offerers_factories.UserOffererFactory().user

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

        response = self.update_account(client, legit_user, user_to_edit, base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.pro_user.get", user_id=user_to_edit.id, _external=True)
        assert response.location == expected_url

        client.with_bo_session_auth(legit_user).get(expected_url)
        history_url = url_for("backoffice_v3_web.pro_user.get_details", user_id=user_to_edit.id)
        response = client.with_bo_session_auth(legit_user).get(history_url)

        user_to_edit = users_models.User.query.get(user_to_edit.id)
        assert user_to_edit.lastName == new_last_name
        assert user_to_edit.email == expected_new_email
        assert user_to_edit.postalCode == expected_new_postal_code

        content = response.data.decode("utf-8")

        assert history_models.ActionType.INFO_MODIFIED.value in content
        assert f"{old_last_name} =&gt; {user_to_edit.lastName}" in content
        assert f"{old_email} =&gt; {user_to_edit.email}" in content
        assert f"{old_postal_code} =&gt; {user_to_edit.postalCode}" in content

    def update_account(self, client, legit_user, user_to_edit, form):
        # generate csrf token
        edit_url = url_for("backoffice_v3_web.pro_user.get", user_id=user_to_edit.id)
        client.with_bo_session_auth(legit_user).get(edit_url)

        url = url_for("backoffice_v3_web.pro_user.update_pro_user", user_id=user_to_edit.id)

        form["csrf_token"] = g.get("csrf_token", "")
        return client.with_bo_session_auth(legit_user).post(url, form=form)


class GetProUserHistoryTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.pro_user.get_details"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    class CommentButtonTest(button_helpers.ButtonHelper):
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY
        button_label = "Ajouter un commentaire"

        @property
        def path(self):
            user = offerers_factories.UserOffererFactory().user
            return url_for("backoffice_v3_web.pro_user.get_details", user_id=user.id)

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
        url = url_for("backoffice_v3_web.pro_user.get_details", user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data, parent_id="history-tab-pane")
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
        url = url_for("backoffice_v3_web.pro_user.get_details", user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)

        assert response.status_code == 200
        assert html_parser.count_table_rows(response.data, parent_id="history-tab-pane") == 0


class CommentProUserTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf, unauthorized_helpers.MissingCSRFHelper):
        endpoint = "backoffice_v3_web.pro_user.comment_pro_user"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_add_comment(self, client, legit_user, pro_user):
        comment = "J'aime les commentaires en français !"
        response = self.send_comment_pro_user_request(client, legit_user, pro_user, comment)

        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.pro_user.get", user_id=pro_user.id, _external=True)
        assert response.location == expected_url

        assert len(pro_user.action_history) == 1
        assert pro_user.action_history[0].user == pro_user
        assert pro_user.action_history[0].authorUser == legit_user
        assert pro_user.action_history[0].comment == comment

    def test_add_invalid_comment(self, client, legit_user, pro_user):
        response = self.send_comment_pro_user_request(client, legit_user, pro_user, "")

        assert response.status_code == 302
        assert not pro_user.action_history

    def send_comment_pro_user_request(self, client, legit_user, pro_user, comment):
        authenticated_client = client.with_bo_session_auth(legit_user)

        # generate and fetch (inside g) csrf token
        pro_user_detail_url = url_for("backoffice_v3_web.pro_user.get", user_id=pro_user.id)
        authenticated_client.get(pro_user_detail_url)

        url = url_for("backoffice_v3_web.pro_user.comment_pro_user", user_id=pro_user.id)
        form = {"comment": comment, "csrf_token": g.get("csrf_token", "")}

        return authenticated_client.post(url, form=form)


class GetProUserOfferersTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
        endpoint = "backoffice_v3_web.pro_user.get_details"
        endpoint_kwargs = {"user_id": 1}
        needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    def test_get_user_offerers(self, authenticated_client, pro_user):
        user_offerer_validated = offerers_factories.UserOffererFactory(user=pro_user)
        user_offerer_new = offerers_factories.NotValidatedUserOffererFactory(user=pro_user)
        url = url_for("backoffice_v3_web.pro_user.get_details", user_id=pro_user.id)

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
        url = url_for("backoffice_v3_web.pro_user.get_details", user_id=pro_user.id)

        with assert_no_duplicated_queries():
            response = authenticated_client.get(url)
        assert response.status_code == 200
