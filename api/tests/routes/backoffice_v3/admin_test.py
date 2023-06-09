import datetime

from flask import url_for
import pytest

from pcapi.core.history import models as history_models
import pcapi.core.history.factories as history_factories
from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import feature as feature_models

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class GetRolesTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.get_roles"
    needed_permission = perm_models.Permissions.MANAGE_PERMISSIONS

    def test_can_list_roles_and_permissions(self, authenticated_client):
        # given
        perm_factories.RoleFactory(name="test_role_1")
        perm_factories.RoleFactory(name="test_role_2")

        # when
        response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200

        roles = html_parser.extract(response.data, class_="card-header")
        assert "test_role_1" in roles
        assert "test_role_2" in roles

        switches = html_parser.extract(response.data, class_="form-switch")
        assert set(switches) == {p.value for p in perm_models.Permissions}

    def test_can_list_roles_ignoring_obsolete_permissions(self, authenticated_client):
        # given
        obsolete_perm = perm_factories.PermissionFactory(name="OBSOLETE")
        perm_factories.RoleFactory(name="test_role_1", permissions=[obsolete_perm])
        perm_factories.RoleFactory(name="test_role_2")

        # when
        response = authenticated_client.get(url_for(self.endpoint))

        # then
        assert response.status_code == 200

        roles = html_parser.extract(response.data, class_="card-header")
        assert "test_role_1" in roles
        assert "test_role_2" in roles


class UpdateRoleTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.update_role"
    endpoint_kwargs = {"role_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_PERMISSIONS

    def test_update_role(self, authenticated_client):
        perms = perm_factories.PermissionFactory.create_batch(4)
        old_perms = [perms[0], perms[1]]
        role_to_edit = perm_factories.RoleFactory(permissions=old_perms)
        role_not_to_edit = perm_factories.RoleFactory(permissions=old_perms)

        new_perms = [perms[1], perms[3]]
        base_form = {}
        for perm in perms:
            base_form[perm.name] = perm in new_perms

        response = self.post_to_endpoint(authenticated_client, role_id=role_to_edit.id, form=base_form)
        assert response.status_code == 303

        expected_url = url_for("backoffice_v3_web.get_roles", _external=True)
        assert response.location == expected_url

        role_to_edit = perm_models.Role.query.get(role_to_edit.id)
        assert role_to_edit.permissions == new_perms

        role_not_to_edit = perm_models.Role.query.get(role_not_to_edit.id)
        assert role_not_to_edit.permissions == old_perms

    def test_update_role_with_empty_permissions(self, authenticated_client):
        role = perm_factories.RoleFactory(name="dummy_role", permissions=[perm_factories.PermissionFactory()])

        response = self.post_to_endpoint(
            authenticated_client,
            role_id=role.id,
            form={perm.name: False for perm in perm_models.Permission.query.all()},
        )
        assert response.status_code == 303

        db.session.refresh(role)
        assert role.permissions == []


class ListFeatureFlagsTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.list_feature_flags"
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_list_feature_flags(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert "Vous allez désactiver" in rows[0]["Activé"]  # "Vous allez désactiver" is inside the modal
        assert rows[0]["Nom"] == first_feature_flag.name
        assert rows[0]["Description"] == first_feature_flag.description

        first_feature_flag.isActive = False

        response = authenticated_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        rows = html_parser.extract_table_rows(response.data)
        assert "Vous allez activer" in rows[0]["Activé"]  # "Vous allez activer" is inside the modal
        assert rows[0]["Nom"] == first_feature_flag.name
        assert rows[0]["Description"] == first_feature_flag.description


class EnableFeatureFlagTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.enable_feature_flag"
    endpoint_kwargs = {"feature_flag_id": 1}
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_enable_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = False

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303

        assert first_feature_flag.isActive is True
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} a été activé" in response.data.decode("utf-8")

    def test_enable_already_active_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} est déjà activé" in response.data.decode("utf-8")


class DisableFeatureFlagTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.disable_feature_flag"
    endpoint_kwargs = {"feature_flag_id": 1}
    needed_permission = perm_models.Permissions.FEATURE_FLIPPING

    def test_disable_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
        first_feature_flag.isActive = True

        response = self.post_to_endpoint(authenticated_client, feature_flag_id=first_feature_flag.id)
        assert response.status_code == 303

        assert first_feature_flag.isActive is False
        response = authenticated_client.get(response.location)
        assert f"Le feature flag {first_feature_flag.name} a été désactivé" in response.data.decode("utf-8")

    def test_disable_already_inactive_feature_flag(self, authenticated_client):
        first_feature_flag = feature_models.Feature.query.order_by(feature_models.Feature.name).first()
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
    endpoint = "backoffice_v3_web.bo_users.search_bo_users"
    needed_permission = perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS

    # - fetch session
    # - fetch authenticated user
    # - fetch results
    # - fetch count for pagination
    expected_num_queries = 4

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


class GetBoUserTest(GetEndpointHelper):
    endpoint = "backoffice_v3_web.bo_users.get_bo_user"
    endpoint_kwargs = {"user_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS

    # - fetch session (1 query)
    # - fetch authenticated user (1 query)
    # - fetch displayed user with joinedloaded data (1 query)
    expected_num_queries = 3

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
            isActive=False, roles=[], dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=180)
        )

        history_factories.ActionHistoryFactory(
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=datetime.datetime.utcnow() - datetime.timedelta(days=2),
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
        assert rows[0]["Type"] == history_models.ActionType.USER_SUSPENDED.value
        assert rows[0]["Date/Heure"]
        assert rows[0]["Commentaire"] == "Fin de contrat Test"
        assert rows[0]["Auteur"] == legit_user.full_name
        assert rows[1]["Type"] == history_models.ActionType.USER_CREATED.value
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


class UpdateBoUserTest(PostEndpointHelper):
    endpoint = "backoffice_v3_web.bo_users.update_bo_user"
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

        action = history_models.ActionHistory.query.one()
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

        assert history_models.ActionHistory.query.count() == 0
