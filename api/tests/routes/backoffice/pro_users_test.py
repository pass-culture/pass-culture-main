import datetime
from unittest.mock import patch

from flask import g
from flask import url_for
import pytest

from pcapi import settings
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.token import SecureToken
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.filters import format_date
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils import urls

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

    # session + current user + pro user data + feature flag
    expected_num_queries = 4

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
        user = users_factories.BeneficiaryGrant18Factory()
        url = url_for(self.endpoint, user_id=user.id)

        with assert_num_queries(self.expected_num_queries - 1):  # -1 because we don't reach the feature flag check
            response = authenticated_client.get(url)
            assert response.status_code == 303

        expected_url = url_for("backoffice_web.pro.search_pro", _external=True)
        assert response.location == expected_url

    @pytest.mark.parametrize("has_new_nav", [True, False])
    def test_get_pro_user_with_new_nav_badges(self, authenticated_client, has_new_nav):
        user = offerers_factories.UserOffererFactory(user__phoneNumber="+33638656565", user__postalCode="29000").user
        if has_new_nav:
            users_factories.UserProNewNavStateFactory(user=user, newNavDate=datetime.datetime.utcnow())
        url = url_for(self.endpoint, user_id=user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        badges = html_parser.extract(response.data, tag="span", class_="badge")
        assert "Pro" in badges
        assert "Validé" in badges
        assert "Suspendu" not in badges

        if has_new_nav:
            assert "Nouvelle interface" in badges
        else:
            assert "Ancienne interface" in badges

    @override_features(ENABLE_PRO_NEW_NAV_MODIFICATION=True)
    def test_form_should_fill_pro_new_nav_state_dates(self, authenticated_client, db_session):
        old_newNavDate = datetime.datetime(2024, 4, 25, 8, 13, 3, 114129)
        old_eligibilityDate = datetime.datetime(2029, 4, 25, 8, 18, 3, 114129)
        user_to_edit = offerers_factories.UserOffererFactory(user__postalCode="74000").user
        user_to_edit.pro_new_nav_state = users_models.UserProNewNavState(
            userId=user_to_edit.id, newNavDate=old_newNavDate, eligibilityDate=old_eligibilityDate
        )
        db_session.flush()
        url = url_for("backoffice_web.pro_user.get", user_id=user_to_edit.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content = html_parser.extract_input_value(response.data, name="new_nav_date")
        assert content == "2024-04-25T10:13"
        content = html_parser.extract_input_value(response.data, name="eligibility_date")
        assert content == "2029-04-25T10:18"

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

        action = history_models.ActionHistory.query.one()
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

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.user == pro_user
        assert action.offererId is None
        assert action.extraData == {
            "modified_info": {"notificationSubscriptions.marketing_email": {"old_info": True, "new_info": False}}
        }

    @override_features(ENABLE_PRO_NEW_NAV_MODIFICATION=True)
    def test_set_new_nav_date(self, legit_user, authenticated_client):
        user_to_edit = offerers_factories.UserOffererFactory(user__postalCode="74000").user

        new_nav_date = datetime.datetime(2025, 6, 7, 8, 9, 10)  # CEST
        eligibility_date = datetime.datetime(2029, 7, 7, 8, 9, 10)  # CEST

        form_data = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "postal_code": user_to_edit.postalCode,
            "phone_number": user_to_edit.phoneNumber,
            "new_nav_date": new_nav_date.strftime(date_utils.DATETIME_FIELD_FORMAT),
            "eligibility_date": eligibility_date.strftime(date_utils.DATETIME_FIELD_FORMAT),
            "marketing_email_subscription": "on",
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=form_data)
        assert response.status_code == 303

        user_to_edit = users_models.User.query.filter_by(id=user_to_edit.id).one()
        assert user_to_edit.pro_new_nav_state.newNavDate == datetime.datetime(2025, 6, 7, 6, 9)
        assert user_to_edit.pro_new_nav_state.eligibilityDate == datetime.datetime(2029, 7, 7, 6, 9)

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUser == legit_user
        assert action.user == user_to_edit
        assert action.actionDate is not None
        assert action.extraData["modified_info"] == {
            "pro_new_nav_state.newNavDate": {"old_info": None, "new_info": "2025-06-07 06:09:00"},
            "pro_new_nav_state.eligibilityDate": {"old_info": None, "new_info": "2029-07-07 06:09:00"},
        }

    @override_features(ENABLE_PRO_NEW_NAV_MODIFICATION=True)
    @pytest.mark.parametrize("new_nav_date", [None, datetime.datetime(2024, 4, 25, 8, 11)])
    @pytest.mark.parametrize("eligibility_date", [None, datetime.datetime(2024, 4, 24, 8, 11)])
    def test_modify_nav_date(self, legit_user, authenticated_client, eligibility_date, new_nav_date):

        new_nav_date_paris = new_nav_date.strftime(date_utils.DATETIME_FIELD_FORMAT) if new_nav_date else None
        eligibility_date_paris = (
            eligibility_date.strftime(date_utils.DATETIME_FIELD_FORMAT) if eligibility_date else None
        )
        old_newNavDate = datetime.datetime(2024, 4, 25, 8, 13)
        old_eligibilityDate = datetime.datetime(2029, 4, 29, 8, 18)
        user_to_edit = offerers_factories.UserOffererFactory(user__postalCode="74000").user
        user_to_edit.pro_new_nav_state = users_models.UserProNewNavState(
            userId=user_to_edit.id, newNavDate=old_newNavDate, eligibilityDate=old_eligibilityDate
        )
        form_data = {
            "first_name": user_to_edit.firstName,
            "last_name": user_to_edit.lastName,
            "email": user_to_edit.email,
            "postal_code": user_to_edit.postalCode,
            "phone_number": user_to_edit.phoneNumber,
            "new_nav_date": new_nav_date_paris,
            "eligibility_date": eligibility_date_paris,
        }

        response = self.post_to_endpoint(authenticated_client, user_id=user_to_edit.id, form=form_data)
        assert response.status_code == 303

        user_edited = users_models.User.query.filter_by(id=user_to_edit.id).one()
        assert user_edited.pro_new_nav_state.eligibilityDate == (
            datetime.datetime(2024, 4, 24, 6, 11) if eligibility_date else None
        )
        assert user_edited.pro_new_nav_state.newNavDate == (
            datetime.datetime(2024, 4, 25, 6, 11) if new_nav_date else None
        )

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUser == legit_user
        assert action.user == user_to_edit
        assert action.extraData["modified_info"]["pro_new_nav_state.newNavDate"]["old_info"] == str(old_newNavDate)[:19]
        assert (
            action.extraData["modified_info"]["pro_new_nav_state.eligibilityDate"]["old_info"]
            == str(old_eligibilityDate)[:19]
        )

        assert action.extraData["modified_info"]["pro_new_nav_state.newNavDate"]["new_info"] == (
            "2024-04-25 06:11:00" if new_nav_date else None
        )

        assert action.extraData["modified_info"]["pro_new_nav_state.eligibilityDate"]["new_info"] == (
            "2024-04-24 06:11:00" if eligibility_date else None
        )

    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryGrant18Factory, users_factories.AdminFactory])
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
        assert history_models.ActionHistory.query.count() == 0


class GetProUserHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro_user.get_details"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_PRO_ENTITY

    # session + current user + user + actions + former user_offerer
    expected_num_queries = 5

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

        with assert_num_queries(self.expected_num_queries):
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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data, parent_class="history-tab-pane") == 0

    @override_features(ENABLE_PRO_NEW_NAV_MODIFICATION=True)
    def test_new_nav_dates_in_history(self, authenticated_client):
        user = offerers_factories.UserOffererFactory().user
        old_eligibility_date = datetime.datetime(2024, 4, 27, 8, 13, 3, 0)
        old_new_nav_date = datetime.datetime(2024, 4, 28, 8, 13, 3, 0)
        new_eligibility_date = datetime.datetime(2024, 4, 24, 8, 11, 0, 0)
        new_nav_date = datetime.datetime(2024, 4, 25, 8, 11, 0, 0)
        user.pro_new_nav_state = users_factories.UserProNewNavStateFactory(
            user=user, eligibilityDate=new_eligibility_date, newNavDate=new_nav_date
        )
        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.INFO_MODIFIED,
            user=user,
            extraData={
                "modified_info": {
                    "pro_new_nav_state.eligibilityDate": {
                        "old_info": old_eligibility_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "new_info": new_eligibility_date.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    "pro_new_nav_state.newNavDate": {
                        "old_info": old_new_nav_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "new_info": new_nav_date.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                }
            },
        )
        url = url_for("backoffice_web.pro_user.get_details", user_id=user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(rows) == 1

        assert rows[0]["Type"] == history_models.ActionType.INFO_MODIFIED.value
        assert (
            "Date d'éligibilité à la nouvelle interface Pro : 2024-04-27 08:13:03 => 2024-04-24 08:11:00"
            in rows[0]["Commentaire"]
        )
        assert (
            "Date de passage sur la nouvelle interface Pro : 2024-04-28 08:13:03 => 2024-04-25 08:11:00"
            in rows[0]["Commentaire"]
        )

    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryGrant18Factory, users_factories.AdminFactory])
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

        expected_url = url_for("backoffice_web.pro_user.get", user_id=pro_user.id, _external=True)
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

    # session + current user + user + actions + user_offerer objects
    expected_num_queries = 5

    def test_get_user_offerers(self, authenticated_client, pro_user):
        user_offerer_validated = offerers_factories.UserOffererFactory(user=pro_user)
        user_offerer_new = offerers_factories.NotValidatedUserOffererFactory(user=pro_user)
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
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

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_get_user_offerers_in_different_offerer_status(self, authenticated_client, pro_user):
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerers_factories.PendingOffererFactory())
        url = url_for(self.endpoint, user_id=pro_user.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="user_offerers-tab-pane")
        assert len(rows) == 2

        assert rows[0]["Statut structure"] == "Validée"
        assert rows[1]["Statut structure"] == "En attente"


class ValidateProEmailTest(PostEndpointHelper):
    endpoint = "backoffice_web.pro_user.validate_pro_user_email"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    def test_validate_pro_user_email_ff_on(self, authenticated_client):
        pro_user = offerers_factories.NotValidatedUserOffererFactory(user__isEmailValidated=False).user
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
        user = users_factories.UserFactory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
        history_factories.SuspendedUserActionHistoryFactory(user=user)
        user_id = user.id
        user_email = user.email
        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.pro.search_pro", _external=True)

        mails_api.delete_contact.assert_called_once_with(user_email)
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
        assert response.location == url_for("backoffice_web.pro.search_pro", _external=True)

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
    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryGrant18Factory, users_factories.AdminFactory])
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
        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 1
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.userId == user_id).count() == 1

    def test_delete_pro_user_with_related_objects(self, authenticated_client):
        user = users_factories.NonAttachedProFactory()
        users_factories.FavoriteFactory(user=user)
        offers_factories.MediationFactory(author=user)

        user_id = user.id

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form={"email": user.email})

        # ensure that it does not crash
        assert response.status_code == 303

        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 0
        assert users_models.Favorite.query.filter(users_models.Favorite.userId == user_id).count() == 0
        assert offers_models.Mediation.query.one().authorId is None

    @patch("pcapi.routes.backoffice.pro_users.blueprint.mails_api")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.DeleteBatchUserAttributesRequest", return_value="canary")
    @patch("pcapi.routes.backoffice.pro_users.blueprint.delete_user_attributes_task")
    def test_delete_pro_user_with_beneficiary_dependencies(
        self, delete_user_attributes_task, DeleteBatchUserAttributesRequest, mails_api, authenticated_client
    ):
        user = users_factories.BeneficiaryGrant18Factory(roles=[users_models.UserRole.NON_ATTACHED_PRO])
        history_factories.SuspendedUserActionHistoryFactory(user=user)
        user_id = user.id
        deposit_id = user.deposits[0].id
        beneficiary_fraud_check_id = user.beneficiaryFraudChecks[0].id
        user_email = user.email
        form = {"email": user.email}

        response = self.post_to_endpoint(authenticated_client, user_id=user_id, form=form, follow_redirects=True)

        assert response.status_code == 200

        mails_api.delete_contact.assert_called_once_with(user_email)
        DeleteBatchUserAttributesRequest.assert_called_once_with(user_id=user_id)
        delete_user_attributes_task.delay.assert_called_once_with("canary")
        assert users_models.User.query.filter(users_models.User.id == user_id).count() == 0
        assert finance_models.Deposit.query.filter(finance_models.Deposit.id == deposit_id).count() == 0
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter(
                fraud_models.BeneficiaryFraudCheck.id == beneficiary_fraud_check_id
            ).count()
            == 0
        )
        assert history_models.ActionHistory.query.filter(history_models.ActionHistory.userId == user_id).count() == 0


class GetConnectAsProUserTest(GetEndpointHelper):
    endpoint = "backoffice_web.pro_user.connect_as"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PRO_ENTITY

    # session + current user + pro user data + WIP_CONNECT_AS
    expected_num_queries = 4

    # when pro is not loaded, e.g. invalid token or FF disabled
    expected_num_queries_when_failed = expected_num_queries - 1

    def _get_csrf_token(self, auth_client):
        auth_client.get(url_for("backoffice_web.home"))
        return g.get("csrf_token", None)

    @override_features(WIP_CONNECT_AS=True)
    @pytest.mark.parametrize("roles", [[users_models.UserRole.PRO], [users_models.UserRole.NON_ATTACHED_PRO]])
    def test_connect_as(self, client, legit_user, roles):
        user = users_factories.ProFactory(roles=roles)
        authenticated_client = client.with_bo_session_auth(legit_user)

        expected_token_data = {
            "user_id": user.id,
            "internal_admin_id": legit_user.id,
            "internal_admin_email": legit_user.email,
            "redirect_link": settings.PRO_URL,
        }

        url = url_for(self.endpoint, user_id=user.id, csrf_token=self._get_csrf_token(authenticated_client))
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        # check url form
        base_url, key_token = response.location.rsplit("/", 1)
        assert base_url + "/" == urls.build_pc_pro_connect_as_link("")
        assert SecureToken(token=key_token).data == expected_token_data

    @override_features(WIP_CONNECT_AS=False)
    def test_connect_as_protected_by_feature_flag(self, authenticated_client):
        user = users_factories.ProFactory()

        url = url_for(self.endpoint, user_id=user.id, csrf_token=self._get_csrf_token(authenticated_client))
        with assert_num_queries(self.expected_num_queries_when_failed):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id, _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "L'utilisation du « connect as » requiert l'activation de la feature : WIP_CONNECT_AS"
        )

    @override_features(WIP_CONNECT_AS=True)
    def test_connect_as_protected_by_csrf(self, authenticated_client):
        user = users_factories.ProFactory()

        g.csrf_valid = False

        url = url_for(self.endpoint, user_id=user.id, csrf_token="invalid-token")
        with assert_num_queries(self.expected_num_queries_when_failed):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id, _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "Échec de la validation de sécurité, veuillez réessayer"
        )

    @override_features(WIP_CONNECT_AS=True)
    def test_connect_as_user_not_found(self, authenticated_client):
        url = url_for(self.endpoint, user_id=0, csrf_token=self._get_csrf_token(authenticated_client))
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 404

    @override_features(WIP_CONNECT_AS=True)
    def test_connect_as_inactive_user(self, authenticated_client):
        user = users_factories.ProFactory(isActive=False)

        url = url_for(self.endpoint, user_id=user.id, csrf_token=self._get_csrf_token(authenticated_client))
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id, _external=True)
        redirected_response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(redirected_response.data)
            == "L'utilisation du « connect as » n'est pas disponible pour les comptes inactifs"
        )

    @override_features(WIP_CONNECT_AS=True)
    @pytest.mark.parametrize(
        "roles,warning",
        [
            (
                [users_models.UserRole.PRO, users_models.UserRole.ADMIN],
                "L'utilisation du « connect as » n'est pas disponible pour les comptes ADMIN",
            ),
            (
                [users_models.UserRole.PRO, users_models.UserRole.ANONYMIZED],
                "L'utilisation du « connect as » n'est pas disponible pour les comptes anonymisés",
            ),
            ([], ""),
        ],
    )
    def test_connect_as_uneligible_user(self, authenticated_client, roles, warning):
        user = users_factories.UserFactory(roles=roles)

        url = url_for(self.endpoint, user_id=user.id, csrf_token=self._get_csrf_token(authenticated_client))
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 303

        assert response.location == url_for("backoffice_web.pro_user.get", user_id=user.id, _external=True)
        if warning:
            redirected_response = authenticated_client.get(response.location)
            assert html_parser.extract_alert(redirected_response.data) == warning
