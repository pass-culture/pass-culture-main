import datetime

import pytest
import sqlalchemy.orm as sa_orm
from flask import url_for

from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db
from pcapi.models import feature as feature_models
from pcapi.utils import date as date_utils

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.get import GetEndpointWithoutPermissionHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetRolesTest(GetEndpointHelper):
    endpoint = "backoffice_web.get_roles"
    needed_permission = perm_models.Permissions.READ_PERMISSIONS

    # session + roles + permissions
    expected_num_queries = 3

    def test_get_roles_matrix(self, authenticated_client):
        count_roles = db.session.query(perm_models.Role).count()
        count_permissions = db.session.query(perm_models.Permission).count()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        table_rows = html_parser.extract_table_rows(response.data)

        assert len(table_rows) == count_permissions
        assert len(table_rows[0]) == count_roles

        # First row is "support pro avancé"
        assert table_rows[0]["admin"] == ""
        assert table_rows[0]["global_access"] == "x"
        assert table_rows[0]["support_pro"] == ""
        assert table_rows[0]["support_pro_n2"] == "x"


class GetRolesManagementTest(GetEndpointHelper):
    endpoint = "backoffice_web.get_roles_management"
    needed_permission = perm_models.Permissions.MANAGE_PERMISSIONS

    # session + roles + permissions
    expected_num_queries = 3

    def test_can_list_roles_and_permissions(self, authenticated_client):
        perm_factories.RoleFactory(name="test_role_1")
        perm_factories.RoleFactory(name="test_role_2")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        roles = html_parser.extract(response.data, class_="card-header")
        assert "test_role_1" in roles
        assert "test_role_2" in roles

        switches = html_parser.extract(response.data, class_="form-switch")
        assert set(switches) == {p.value for p in perm_models.Permissions}

    def test_can_list_roles_ignoring_obsolete_permissions(self, authenticated_client):
        obsolete_perm = perm_factories.PermissionFactory(name="OBSOLETE")
        perm_factories.RoleFactory(name="test_role_1", permissions=[obsolete_perm])
        perm_factories.RoleFactory(name="test_role_2")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        roles = html_parser.extract(response.data, class_="card-header")
        assert "test_role_1" in roles
        assert "test_role_2" in roles


class UpdateRoleTest(PostEndpointHelper):
    endpoint = "backoffice_web.update_role"
    endpoint_kwargs = {"role_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PERMISSIONS

    def test_update_role(self, authenticated_client):
        perms = perm_factories.PermissionFactory.create_batch(4)
        old_perms = [perms[0], perms[1]]
        role_to_edit = perm_factories.RoleFactory(permissions=old_perms)
        role_not_to_edit = perm_factories.RoleFactory(permissions=old_perms)

        new_perms = [perms[1], perms[3]]
        base_form = {"comment": "Test"}
        for perm in perms:
            base_form[perm.name] = perm in new_perms

        response = self.post_to_endpoint(authenticated_client, role_id=role_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_web.get_roles", active_tab="management")
        assert response.location == expected_url

        role_to_edit = db.session.query(perm_models.Role).filter_by(id=role_to_edit.id).one()
        assert set(role_to_edit.permissions) == set(new_perms)

        role_not_to_edit = db.session.query(perm_models.Role).filter_by(id=role_not_to_edit.id).one()
        assert set(role_not_to_edit.permissions) == set(old_perms)

    def test_update_role_with_empty_permissions(self, authenticated_client):
        role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])

        response = self.post_to_endpoint(
            authenticated_client,
            role_id=role.id,
            form={perm.name: False for perm in db.session.query(perm_models.Permission).all()},
        )
        assert response.status_code == 303

        db.session.refresh(role)
        assert role.permissions == []

    def test_log_update_role(self, legit_user, authenticated_client):
        permissions = (
            db.session.query(perm_models.Permission)
            .filter(
                perm_models.Permission.name.in_(
                    (
                        perm_models.Permissions.FEATURE_FLIPPING.name,
                        perm_models.Permissions.MANAGE_PERMISSIONS.name,
                        perm_models.Permissions.READ_ADMIN_ACCOUNTS.name,
                    )
                )
            )
            .order_by(perm_models.Permission.name)
            .all()
        )
        role_to_edit = perm_factories.RoleFactory(permissions=permissions[:2])

        response = self.post_to_endpoint(
            authenticated_client,
            role_id=role_to_edit.id,
            form={
                perm_models.Permissions.MANAGE_PERMISSIONS.name: "on",
                perm_models.Permissions.READ_ADMIN_ACCOUNTS.name: "on",
                "comment": "Test",
            },
        )
        assert response.status_code == 303

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.ROLE_PERMISSIONS_CHANGED
        assert action.authorUserId == legit_user.id
        assert action.comment == "Test"
        assert action.extraData == {
            "role_name": role_to_edit.name,
            "modified_info": {
                perm_models.Permissions.FEATURE_FLIPPING.name: {"old_info": True, "new_info": False},
                perm_models.Permissions.READ_ADMIN_ACCOUNTS.name: {"old_info": False, "new_info": True},
            },
        }

    def test_log_update_role_no_modification(self, legit_user, authenticated_client):
        permissions = (
            db.session.query(perm_models.Permission)
            .filter(
                perm_models.Permission.name.in_(
                    (
                        perm_models.Permissions.MANAGE_PERMISSIONS.name,
                        perm_models.Permissions.READ_ADMIN_ACCOUNTS.name,
                    )
                )
            )
            .all()
        )

        role = perm_factories.RoleFactory(permissions=permissions)

        response = self.post_to_endpoint(
            authenticated_client,
            role_id=role.id,
            form={
                perm_models.Permissions.MANAGE_PERMISSIONS.name: "on",
                perm_models.Permissions.READ_ADMIN_ACCOUNTS.name: "on",
            },
        )
        assert response.status_code == 303

        assert db.session.query(history_models.ActionHistory).count() == 0

    @pytest.mark.settings(BACKOFFICE_ROLES_WITHOUT_GOOGLE_GROUPS=0)
    def test_comment_is_mandatory_in_production(self, authenticated_client):
        role_to_edit = perm_factories.RoleFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            role_id=role_to_edit.id,
            form={
                perm_models.Permissions.READ_OFFERS.name: "on",
                perm_models.Permissions.READ_BOOKINGS.name: "",
                "comment": "",
            },
        )
        assert response.status_code == 303

        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "Les données envoyées comportent des erreurs. "
            "Commentaire obligatoire : raison de la modification : Information obligatoire ;"
        )
        assert len(role_to_edit.permissions) == 0
        assert db.session.query(history_models.ActionHistory).count() == 0


class GetRolesHistoryTest(GetEndpointHelper):
    endpoint = "backoffice_web.get_roles_history"
    needed_permission = perm_models.Permissions.READ_PERMISSIONS

    # session + history
    expected_num_queries = 2

    def test_get_log_history_admin(self, legit_user, authenticated_client):
        permission1 = (
            db.session.query(perm_models.Permission)
            .filter_by(name=perm_models.Permissions.MANAGE_PERMISSIONS.name)
            .one()
        )
        permission2 = (
            db.session.query(perm_models.Permission)
            .filter_by(name=perm_models.Permissions.READ_ADMIN_ACCOUNTS.name)
            .one()
        )

        role = perm_factories.RoleFactory(permissions=[permission1, permission2])

        action = history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.ROLE_PERMISSIONS_CHANGED,
            authorUser=legit_user,
            comment=None,
            extraData={
                "role_name": role.name,
                "modified_info": {
                    permission1.name: {"new_info": False, "old_info": True},
                    permission2.name: {"new_info": True, "old_info": False},
                },
            },
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        history_rows = html_parser.extract_table_rows(response.data)
        assert len(history_rows) == 1
        assert history_rows[0]["Type"] == "Modification des permissions du rôle"
        assert (
            history_rows[0]["Commentaire"] == f"Rôle : {role.name} "
            f"Informations modifiées : {perm_models.Permissions.MANAGE_PERMISSIONS.value} : Oui → Non "
            f"{perm_models.Permissions.READ_ADMIN_ACCOUNTS.value} : Non → Oui"
        )
        assert history_rows[0]["Auteur"] == action.authorUser.full_name


class ListFeatureFlagsTest(GetEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.list_feature_flags"

    # session + list of feature flags
    expected_num_queries = 2

    def test_list_feature_flags(self, authenticated_client):
        first_feature_flag = db.session.query(feature_models.Feature).order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True
        db.session.flush()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert "Vous allez désactiver" in rows[0]["Activé"]  # "Vous allez désactiver" is inside the modal
        assert rows[0]["Nom"] == first_feature_flag.name
        assert rows[0]["Description"] == first_feature_flag.description

        first_feature_flag.isActive = False
        db.session.flush()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert "Vous allez activer" in rows[0]["Activé"]  # "Vous allez activer" is inside the modal
        assert rows[0]["Nom"] == first_feature_flag.name
        assert rows[0]["Description"] == first_feature_flag.description

    def test_read_only_list_feature_flags(self, client, read_only_bo_user):
        first_feature_flag = db.session.query(feature_models.Feature).order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True
        db.session.flush()

        response = client.with_bo_session_auth(read_only_bo_user).get(url_for(self.endpoint))
        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        for row in rows:
            assert row["Activé"] == ""


class EnableFeatureFlagTest(PostEndpointHelper):
    endpoint = "backoffice_web.enable_feature_flag"
    endpoint_kwargs = {"feature_flag_id": 1}
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_enable_feature_flag(self, authenticated_client):
        first_feature_flag = db.session.query(feature_models.Feature).order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = False

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303

        assert first_feature_flag.isActive is True
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} a été activé" in response.data.decode("utf-8")

    def test_enable_already_active_feature_flag(self, authenticated_client):
        first_feature_flag = db.session.query(feature_models.Feature).order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} est déjà activé" in response.data.decode("utf-8")


class DisableFeatureFlagTest(PostEndpointHelper):
    endpoint = "backoffice_web.disable_feature_flag"
    endpoint_kwargs = {"feature_flag_id": 1}
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_disable_feature_flag(self, authenticated_client):
        first_feature_flag = db.session.query(feature_models.Feature).order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303

        assert first_feature_flag.isActive is False
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} a été désactivé" in response.data.decode("utf-8")

    def test_disable_already_inactive_feature_flag(self, authenticated_client):
        first_feature_flag = db.session.query(feature_models.Feature).order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = False

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} est déjà désactivé" in response.data.decode("utf-8")


def assert_user_equals(result_card_text: str, expected_user: users_models.User):
    assert f"{expected_user.firstName} {expected_user.lastName} " in result_card_text
    assert f"User ID : {expected_user.id} " in result_card_text
    assert f"Email : {expected_user.email} " in result_card_text
    if users_models.UserRole.ADMIN in expected_user.roles:
        assert "Admin " in result_card_text
    if not expected_user.isActive:
        assert "Suspendu" in result_card_text


class SearchBoUsersTest(GetEndpointHelper):
    endpoint = "backoffice_web.bo_users.search_bo_users"
    needed_permission = perm_models.Permissions.READ_ADMIN_ACCOUNTS

    # - fetch session and user
    # - fetch results
    # - fetch count for pagination
    expected_num_queries = 3

    def test_search_without_filter(self, authenticated_client, legit_user):
        user1 = users_factories.AdminFactory()
        user2 = users_factories.AdminFactory(isActive=False)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 3
        cards_text = sorted(cards_text)
        assert_user_equals(cards_text[0], user1)  # starts with "Admin"
        assert_user_equals(cards_text[1], legit_user)  # starts with "Hercule"
        assert_user_equals(cards_text[2], user2)  # starts with "Suspendu"

    def test_search_paginated_without_filter(self, authenticated_client, legit_user):
        users_factories.AdminFactory.create_batch(2)  # + legit_user = 3 admin users

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, page=1, per_page=2))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, page=2, per_page=2))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1

    def test_search_by_name(self, authenticated_client, legit_user):
        user1 = users_factories.AdminFactory(firstName="Alice", lastName="Bob")
        users_factories.AdminFactory(firstName="Bob", lastName="Carole")
        user2 = users_factories.AdminFactory(firstName="Carole", lastName="Alice")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="alice"))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 2
        assert_user_equals(cards_text[0], user1)
        assert_user_equals(cards_text[1], user2)

    def test_search_by_id(self, authenticated_client, legit_user):
        users = users_factories.AdminFactory.create_batch(2)
        user_id = users[1].id

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=str(user_id)))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], users[1])

    def test_search_by_email(self, authenticated_client, legit_user):
        users = users_factories.AdminFactory.create_batch(2)
        email = users[0].email

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=email))
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert_user_equals(cards_text[0], users[0])

    def test_search_invalid(self, authenticated_client):
        with assert_num_queries(2):  # only session + rollback
            response = authenticated_client.get(url_for(self.endpoint, q="%"))
            assert response.status_code == 400

        assert "Le caractère % n'est pas autorisé" in html_parser.extract_warnings(response.data)


class GetBoUserTest(GetEndpointHelper):
    endpoint = "backoffice_web.bo_users.get_bo_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.READ_ADMIN_ACCOUNTS

    # - fetch session  and user (1 query)
    # - fetch displayed user with joinedloaded data (1 query)
    expected_num_queries = 2

    def test_get_bo_user(self, authenticated_client):
        user = users_factories.AdminFactory()

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Admin" in content
        assert "Suspendu" not in content
        assert f"User ID : {user.id} " in content
        assert f"Email : {user.email} " in content
        assert f"Date de création du compte : {user.dateCreated.strftime('%d/%m/%Y')}" in content
        assert (
            f"Date de dernière connexion : {user.lastConnectionDate.strftime('%d/%m/%Y') if user.lastConnectionDate else ''}"
            in content
        )
        assert "Date de naissance" not in content
        assert "Tél :" not in content
        assert "Adresse :" not in content

    def test_get_suspended_bo_user_with_history(self, authenticated_client, legit_user):
        user = users_factories.AdminFactory(
            isActive=False, roles=[], dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=180)
        )

        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=2),
            authorUser=legit_user,
            user=user,
            extraData={"reason": users_constants.SuspensionReason.END_OF_CONTRACT},
            comment="Test",
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        content = html_parser.content_as_text(response.data)
        assert "Suspendu" in content

        rows = html_parser.extract_table_rows(response.data, parent_class="history-tab-pane")
        assert len(rows) == 2
        assert rows[0]["Type"] == "Compte suspendu"
        assert rows[0]["Date/Heure"]
        assert rows[0]["Commentaire"] == "Fin de contrat Test"
        assert rows[0]["Auteur"] == legit_user.full_name
        assert rows[1]["Type"] == "Création du compte"
        assert rows[1]["Date/Heure"]
        assert rows[1]["Auteur"] == user.full_name

    def test_get_bo_user_roles(self, authenticated_client, roles_with_permissions):
        user = users_factories.AdminFactory(
            backoffice_profile__roles=[
                role
                for role in roles_with_permissions
                if role.name
                in (
                    perm_models.Roles.SUPPORT_N2.value,
                    perm_models.Roles.SUPPORT_PRO.value,
                    perm_models.Roles.FRAUDE_CONFORMITE.value,
                )
            ]
        )

        user_id = user.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="roles-tab-pane")
        assert [row["Rôle"] for row in rows] == [
            perm_models.Roles.FRAUDE_CONFORMITE.value,
            perm_models.Roles.SUPPORT_N2.value,
            perm_models.Roles.SUPPORT_PRO.value,
        ]
        assert "visualiser une entité juridique, un partenaire culturel ou un compte pro" in " ".join(
            [row["Permissions"] for row in rows]
        )

    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryFactory, users_factories.ProFactory])
    def test_get_non_bo_user(self, authenticated_client, user_factory):
        user = user_factory()

        user_id = user.id
        expected_num_queries = self.expected_num_queries
        expected_num_queries += 1  # rollback after error
        with assert_num_queries(expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, user_id=user_id))
            assert response.status_code == 404

    def test_get_my_backoffice_profile(self, pro_fraud_admin, client):
        my_id = pro_fraud_admin.id
        client = client.with_bo_session_auth(pro_fraud_admin)

        with assert_num_queries(self.expected_num_queries):
            response = client.get(url_for(self.endpoint, user_id=my_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="roles-tab-pane")
        assert len(rows) == 1
        assert rows[0]["Rôle"] == perm_models.Roles.FRAUDE_CONFORMITE.value
        assert "actions exclusives à l'équipe Fraude et Conformité (PRO)" in rows[0]["Permissions"]

    def test_get_other_backoffice_profile_without_permission(self, pro_fraud_admin, client):
        client = client.with_bo_session_auth(pro_fraud_admin)
        user_id = users_factories.AdminFactory().id

        response = client.get(url_for(self.endpoint, user_id=user_id))
        assert response.status_code == 403


class UpdateButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS
    button_label = "Modifier les informations"

    @property
    def path(self):
        user = users_factories.AdminFactory()
        return url_for("backoffice_web.bo_users.get_bo_user", user_id=user.id)


class SuspendButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS
    button_label = "Suspendre le compte"

    @property
    def path(self):
        user = users_factories.AdminFactory()
        return url_for("backoffice_web.bo_users.get_bo_user", user_id=user.id)


class UnsuspendButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS
    button_label = "Réactiver le compte"

    @property
    def path(self):
        user = users_factories.AdminFactory(isActive=False)
        return url_for("backoffice_web.bo_users.get_bo_user", user_id=user.id)


class UpdateBoUserTest(PostEndpointHelper):
    endpoint = "backoffice_web.bo_users.update_bo_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS

    def test_update_bo_user(self, authenticated_client, legit_user):
        user = users_factories.AdminFactory(firstName="Holmes", lastName="Sherlock", email="sholmes@example.com")

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user.id,
            form={
                "first_name": "Sherlock",
                "last_name": "Holmes",
                "email": user.email,
            },
        )

        assert response.status_code == 303

        db.session.refresh(user)
        assert user.full_name == "Sherlock Holmes"
        assert user.email == "sholmes@example.com"

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUserId == legit_user.id
        assert action.userId == user.id
        assert action.extraData["modified_info"] == {
            "firstName": {"new_info": "Sherlock", "old_info": "Holmes"},
            "lastName": {"new_info": "Holmes", "old_info": "Sherlock"},
        }

    def test_update_bo_user_with_existing_email(self, authenticated_client, legit_user):
        user1 = users_factories.AdminFactory()
        user2 = users_factories.AdminFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user1.id,
            form={
                "first_name": user1.firstName,
                "last_name": user1.lastName,
                "email": user2.email,
            },
        )

        assert response.status_code == 400
        assert html_parser.extract_alert(response.data) == "L'email est déjà associé à un autre utilisateur"

        assert db.session.query(history_models.ActionHistory).count() == 0

    @pytest.mark.parametrize("user_factory", [users_factories.BeneficiaryFactory, users_factories.ProFactory])
    def test_update_non_bo_user(self, authenticated_client, user_factory):
        user = user_factory()

        response = self.post_to_endpoint(
            authenticated_client,
            user_id=user.id,
            form={"first_name": "Hacked", "last_name": "Hacked", "email": user.email},
        )

        assert response.status_code == 404

        db.session.refresh(user)
        assert "Hacked" not in user.full_name
        assert db.session.query(history_models.ActionHistory).count() == 0


class GetSubcategoriesTest(GetEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.get_subcategories"

    def test_get_subcategories(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["pro_label"] == "Abonnement (bibliothèques, médiathèques...)"
        assert rows[0]["app_label"] == "Abonnement (bibliothèques, médiathèques...)"
        assert rows[0]["Nom tech de la sous-catégorie"] == "ABO_BIBLIOTHEQUE"
        assert rows[0]["Nom tech de la catégorie"] == "LIVRE"
        assert rows[0]["homepage_label_name"] == "LIVRES"
        assert rows[0]["is_event"] == "Non"
        assert rows[0]["conditional_fields"] == "{}"
        assert rows[0]["can_expire"] == "Oui"
        assert rows[0]["is_physical_deposit"] == "Oui"
        assert rows[0]["is_digital_deposit"] == "Non"
        assert rows[0]["online_offline_platform"] == "OFFLINE"
        assert rows[0]["reimbursement_rule"] == "STANDARD"
        assert rows[0]["can_be_duo"] == "Non"
        assert rows[0]["is_selectable"] == "Oui"
        assert rows[0]["Réservable par les 15-17 si gratuite"] == "Oui"
        assert rows[0]["Réservable par les 15-17 si payante"] == "Non"
        assert rows[0]["can_be_withdrawable"] == "Non"


class ListUserProfileRefreshCampaignTest(GetEndpointWithoutPermissionHelper):
    needed_permission = perm_models.Permissions.READ_USER_PROFILE_REFRESH_CAMPAIGN
    endpoint = "backoffice_web.user_profile_refresh_campaigns.list_campaigns"

    def test_get_campaigns(self, authenticated_client):
        campaign1 = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-01-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=True,
        )
        campaign2 = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2027-01-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=False,
        )

        response = authenticated_client.get(url_for(self.endpoint))
        assert response.status_code == 200
        response_data = response.data
        # remove history tables to be able to check columns data
        rows = html_parser.extract_table_rows(response_data, recursive=False)
        assert len(rows) == 2
        assert {r["Id"] for r in rows} == {str(campaign1.id), str(campaign2.id)}

        row1 = [r for r in rows if r["Id"] == str(campaign1.id)][0]
        assert row1["Date de référence"] == "01/01/2026 à 02h01"
        assert row1["Active"] == "Oui"

        row2 = [r for r in rows if r["Id"] == str(campaign2.id)][0]
        assert row2["Date de référence"] == "01/01/2027 à 02h01"
        assert row2["Active"] == "Non"


class CreateUserProfileRefreshCampaignButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN
    button_label = "Créer une nouvelle campagne"

    @property
    def path(self):
        return url_for("backoffice_web.user_profile_refresh_campaigns.list_campaigns")

    @property
    def unauthorized_user(self) -> users_models.User:
        user = users_factories.UserFactory()
        perm_api.create_backoffice_profile(user)

        query = db.session.query(perm_models.Role).options(sa_orm.joinedload(perm_models.Role.permissions))
        roles_without_needed_permission = [
            perm_models.Roles(role.name)
            for role in query
            if (
                not role.has_permission(self.needed_permission)
                and role.has_permission(perm_models.Permissions.READ_USER_PROFILE_REFRESH_CAMPAIGN)
            )
        ]

        backoffice_api.upsert_roles(user, roles_without_needed_permission)

        return user


class CreateUserProfileRefreshCampaignTest(PostEndpointHelper):
    endpoint = "backoffice_web.user_profile_refresh_campaigns.create_campaign"
    needed_permission = perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN

    @pytest.mark.time_machine("2025-02-02")  # Winter time
    def test_create_campaign_regular(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            form={"campaign_date": "2027-01-01T01:01", "is_active": "false"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        campaigns = db.session.query(users_models.UserProfileRefreshCampaign).all()
        assert len(campaigns) == 1
        campaign = campaigns[0]
        assert campaign.isActive is False
        assert campaign.campaignDate == datetime.datetime.strptime("2027-01-01 00:01", "%Y-%m-%d %H:%M")
        assert html_parser.extract_alert(response.data) == "Campagne de mise à jour de données créée avec succès."

    @pytest.mark.time_machine("2025-02-02")  # Winter time
    def test_create_campaign_missing_is_active_field(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            form={"campaign_date": "2027-01-01T01:01"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        campaigns = db.session.query(users_models.UserProfileRefreshCampaign).all()
        assert len(campaigns) == 1
        campaign = campaigns[0]
        assert campaign.isActive is False
        assert campaign.campaignDate == datetime.datetime.strptime("2027-01-01 00:01", "%Y-%m-%d %H:%M")
        assert html_parser.extract_alert(response.data) == "Campagne de mise à jour de données créée avec succès."

    def test_create_campaign_missing_campaign_date_field(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, form={"is_active": False}, follow_redirects=True)
        assert response.status_code == 200
        campaigns = db.session.query(users_models.UserProfileRefreshCampaign).all()
        assert len(campaigns) == 0
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Date de début de la campagne : Information obligatoire ;"
        )

    def test_create_campaign_missing_all_fields(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client, form={}, follow_redirects=True)
        assert response.status_code == 200
        campaigns = db.session.query(users_models.UserProfileRefreshCampaign).all()
        assert len(campaigns) == 0
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Date de début de la campagne : Information obligatoire ;"
        )

    def test_create_campaign_action_history(self, authenticated_client, legit_user):
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "campaign_date": "2027-01-01T01:01",
                "is_active": "false",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        campaigns = db.session.query(users_models.UserProfileRefreshCampaign).all()
        assert len(campaigns) == 1
        campaign = campaigns[0]
        actions = campaign.action_history
        assert len(actions) == 1
        action = actions[0]
        assert action.actionType == history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_CREATED
        assert action.authorUser == legit_user

    def test_create_active_campaign_deactivates_existing_one(self, authenticated_client):
        existing_campaign = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-01-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=True,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "campaign_date": "2027-01-01T01:01",
                "is_active": "true",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        campaigns = db.session.query(users_models.UserProfileRefreshCampaign).all()
        assert len(campaigns) == 2
        new_campaign = [e for e in campaigns if e.id != existing_campaign.id][0]
        existing_campaign = [e for e in campaigns if e.id == existing_campaign.id][0]
        assert new_campaign.isActive is True
        assert existing_campaign.isActive is False

    def test_create_active_campaign_deactivates_existing_one_render(self, authenticated_client):
        existing_campaign = users_factories.UserProfileRefreshCampaignFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "campaign_date": "2027-01-01T01:01",
                "is_active": "true",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        campaigns = db.session.query(users_models.UserProfileRefreshCampaign).all()
        assert len(campaigns) == 2
        rows = html_parser.extract_table_rows(response.data, recursive=False)
        assert len(rows) == 2
        assert existing_campaign.id in [e.id for e in campaigns]
        assert {str(e.id) for e in campaigns} == {e["Id"] for e in rows}

    def test_create_active_campaign_deactivates_existing_one_action(self, authenticated_client):
        existing_campaign = users_factories.UserProfileRefreshCampaignFactory()
        assert len(existing_campaign.action_history) == 0
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "campaign_date": "2027-01-01T01:01",
                "is_active": "true",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        actions = existing_campaign.action_history
        assert len(actions) == 1
        action = actions[0]
        assert action.extraData == {"modified_info": {"isActive": {"old_info": True, "new_info": False}}}


class EditUserProfileRefreshCampaignTest(PostEndpointHelper):
    needed_permission = perm_models.Permissions.MANAGE_USER_PROFILE_REFRESH_CAMPAIGN
    endpoint = "backoffice_web.user_profile_refresh_campaigns.edit_campaign"
    endpoint_kwargs = {"campaign_id": 1}

    @pytest.mark.time_machine("2025-02-02")  # Winter time
    def test_edit_campaign_date(self, authenticated_client):
        campaign = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-01-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=True,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign.id,
            form={
                "campaign_date": "2027-01-01T01:01",
                "is_active": "true",
            },
        )
        assert response.status_code == 200
        # ensure that the row is rendered
        cells = html_parser.extract_plain_row(response.data, id=f"campaign-row-{campaign.id}")
        assert len(cells) == 6
        assert cells[0].startswith("Modifier Voir l'historique")
        assert cells[1] == str(campaign.id)
        assert cells[2] == "Oui"
        assert cells[3] == "01/01/2027 à 01h01"

        assert campaign.campaignDate == datetime.datetime.strptime("2027-01-01 00:01", "%Y-%m-%d %H:%M")
        assert campaign.isActive is True

    @pytest.mark.time_machine("2025-02-02")  # Winter time
    def test_edit_campaign_is_active(self, authenticated_client):
        campaign = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-01-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=True,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign.id,
            form={
                "campaign_date": "2026-01-01T01:01",
                "is_active": "false",
            },
        )
        assert response.status_code == 200
        # ensure that the row is rendered
        cells = html_parser.extract_plain_row(response.data, id=f"campaign-row-{campaign.id}")
        assert len(cells) == 6
        assert cells[0].startswith("Modifier Voir l'historique")
        assert cells[1] == str(campaign.id)
        assert cells[2] == "Non"
        assert cells[3] == "01/01/2026 à 01h01"

        assert campaign.campaignDate == datetime.datetime.strptime("2026-01-01 00:01", "%Y-%m-%d %H:%M")
        assert campaign.isActive is False

    @pytest.mark.time_machine("2025-02-02")  # Winter time
    def test_edit_campaign_action_history(self, authenticated_client, legit_user):
        campaign = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-01-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=True,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign.id,
            form={
                "campaign_date": "2026-01-01T02:01",
                "is_active": "false",
            },
        )
        assert response.status_code == 200
        actions = campaign.action_history
        assert len(actions) == 1
        action = actions[0]
        assert action.actionType == history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_UPDATED
        assert action.authorUser == legit_user
        assert action.extraData == {"modified_info": {"isActive": {"new_info": False, "old_info": True}}}

    @pytest.mark.time_machine("2025-10-22 16:00:00", tick=False)
    def test_edit_campaign_action_history_render(self, authenticated_client, legit_user):
        campaign = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-02-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=True,
        )

        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign.id,
            form={
                "campaign_date": "2026-03-01T01:01",
                "is_active": "false",
            },
        )
        assert response.status_code == 200
        actions = campaign.action_history
        assert len(actions) == 1
        history_table_rows = html_parser.extract_table_rows(response.data)
        assert len(history_table_rows) == 1
        history_row = history_table_rows[0]
        assert history_row["Action"] == "Mise à jour"
        assert history_row["Utilisateur"] == f"{legit_user.firstName} {legit_user.lastName}"
        assert history_row["Date"] == "22/10/2025 à 18h00"
        assert history_row["Informations"] == "Actif : Oui → Non Date : 01/02/2026 à 02h01 → 01/03/2026 à 01h01"

    def test_activate_campaign_deactivates_existing_one(self, authenticated_client):
        campaign1 = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-01-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=True,
        )
        campaign2 = users_factories.UserProfileRefreshCampaignFactory(
            campaignDate=datetime.datetime.strptime("2026-05-01 01:01", "%Y-%m-%d %H:%M"),
            isActive=False,
        )
        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign2.id,
            form={
                "campaign_date": "2026-05-01T01:01",
                "is_active": "true",
            },
        )
        assert response.status_code == 200
        db.session.refresh(campaign1)
        db.session.refresh(campaign2)
        assert campaign1.isActive is False
        assert campaign2.isActive is True

    def test_activate_campaign_deactivates_existing_one_render(self, authenticated_client):
        campaign1 = users_factories.UserProfileRefreshCampaignFactory(isActive=False)
        campaign2 = users_factories.UserProfileRefreshCampaignFactory(isActive=True)
        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign1.id,
            form={
                "is_active": "true",
                "campaign_date": "2026-05-01T01:01",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        rows = html_parser.extract_plain_rows(response.data)
        assert len(rows) == 2
        assert {str(campaign1.id), str(campaign2.id)} == {e[1] for e in rows}

    def test_activate_campaign_deactivates_existing_one_action(self, authenticated_client):
        campaign1 = users_factories.UserProfileRefreshCampaignFactory(isActive=False)
        campaign2 = users_factories.UserProfileRefreshCampaignFactory(isActive=True)
        assert len(campaign2.action_history) == 0
        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign1.id,
            form={
                "is_active": "true",
                "campaign_date": "2026-05-01T01:01",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        actions = campaign2.action_history
        assert len(actions) == 1
        action = actions[0]
        assert action.extraData == {"modified_info": {"isActive": {"old_info": True, "new_info": False}}}

    def test_activate_campaign_rerender_only_affected_campaigns(self, authenticated_client):
        users_factories.UserProfileRefreshCampaignFactory(isActive=False)
        campaign2 = users_factories.UserProfileRefreshCampaignFactory(isActive=True)
        campaign3 = users_factories.UserProfileRefreshCampaignFactory(isActive=False)
        assert len(campaign2.action_history) == 0
        response = self.post_to_endpoint(
            authenticated_client,
            campaign_id=campaign3.id,
            form={
                "is_active": "true",
                "campaign_date": "2026-05-01T01:01",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        rows = html_parser.extract_plain_rows(response.data)
        assert len(rows) == 2
        assert {str(campaign2.id), str(campaign3.id)} == {e[1] for e in rows}
