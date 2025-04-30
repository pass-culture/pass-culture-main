from flask import url_for
from flask_login import login_user
import pytest

from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.backoffice import menu


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.fixture(name="disable_menu_settings")
def disable_menu_settings_fixture(settings):
    settings.ENABLE_TEST_USER_GENERATION = False
    settings.ENABLE_BO_COMPONENT_PAGE = False


@pytest.fixture(name="permissions")
def permissions_fixture():
    # Roles have already been created from enum in sync_db_permissions()
    return {perm.name: perm for perm in db.session.query(perm_models.Permission).all()}


@pytest.fixture(name="generate_user_with_bo_permissions")
def generate_user_with_bo_permissions_fixture(permissions):
    def generate_user(permission_names: list[str]):
        user = users_factories.UserFactory(roles=["ADMIN"])
        role = perm_factories.RoleFactory(permissions=[permissions[name] for name in permission_names])
        perm_factories.BackOfficeUserProfileFactory(user=user, roles=[role])

        return user

    return generate_user


class MenuTest:
    def test_menu_regular(self, generate_user_with_bo_permissions, disable_menu_settings):
        user = generate_user_with_bo_permissions(["MANAGE_PUBLIC_ACCOUNT"])
        login_user(user)

        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 2
        assert {e.label for e in menu_sections} == {"Jeunes et grand public", "Admin"}
        menu_section = [e for e in menu_sections if e.label == "Jeunes et grand public"][0]
        assert len(menu_section.items) == 1
        menu_item = menu_section.items[0]
        assert menu_item.label == "Extraction des données jeunes"

    def test_menu_anonymous_user(self):
        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 0

    def test_menu_dev(self, generate_user_with_bo_permissions, settings):
        settings.ENABLE_TEST_USER_GENERATION = True
        settings.ENABLE_BO_COMPONENT_PAGE = True

        user = generate_user_with_bo_permissions([])
        login_user(user)

        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 2
        assert {e.label for e in menu_sections} == {"Dev", "Admin"}
        menu_section = [e for e in menu_sections if e.label == "Dev"][0]
        menu_items = menu_section.items
        assert len(menu_items) == 3
        assert {"Générateur d'utilisateurs de test", "Suppression d'utilisateur", "Liste des composants"} == {
            e.label for e in menu_items
        }

    def test_partial_menu_dev(self, generate_user_with_bo_permissions, settings):
        settings.ENABLE_TEST_USER_GENERATION = True
        settings.ENABLE_BO_COMPONENT_PAGE = False

        user = generate_user_with_bo_permissions([])
        login_user(user)

        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 2
        assert {e.label for e in menu_sections} == {"Dev", "Admin"}
        menu_section = [e for e in menu_sections if e.label == "Dev"][0]
        menu_items = menu_section.items
        assert len(menu_items) == 2
        assert {"Générateur d'utilisateurs de test", "Suppression d'utilisateur"} == {e.label for e in menu_items}

    def test_multiple_permissions_menu_item_visible(self, generate_user_with_bo_permissions, disable_menu_settings):
        user = generate_user_with_bo_permissions(["READ_PRO_ENTITY", "MANAGE_PRO_ENTITY"])
        login_user(user)

        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 2
        assert {e.label for e in menu_sections} == {"Acteurs culturels", "Admin"}
        menu_section = [e for e in menu_sections if e.label == "Acteurs culturels"][0]
        assert len(menu_section.items) == 5
        assert "Actions sur les partenaires culturels" in {e.label for e in menu_section.items}

    def test_multiple_permissions_menu_item_not_visible(self, generate_user_with_bo_permissions, disable_menu_settings):
        user = generate_user_with_bo_permissions(["MANAGE_PRO_ENTITY"])
        login_user(user)

        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 1
        assert {e.label for e in menu_sections} == {"Admin"}

    def test_partial_permissions_menu_items(self, generate_user_with_bo_permissions, disable_menu_settings):
        user = generate_user_with_bo_permissions(["READ_PRO_ENTITY"])
        login_user(user)

        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 2
        assert {e.label for e in menu_sections} == {"Acteurs culturels", "Admin"}
        menu_section = [e for e in menu_sections if e.label == "Acteurs culturels"][0]
        assert len(menu_section.items) == 4
        assert {
            "Liste des acteurs culturels",
            "Entités juridiques à valider",
            "Rattachements à valider",
            "Préférences",
        } == {e.label for e in menu_section.items}

    def test_menu_item_url_with_kwargs(self, generate_user_with_bo_permissions, disable_menu_settings):
        user = generate_user_with_bo_permissions([])
        login_user(user)

        menu_sections = menu.get_menu_sections()
        assert len(menu_sections) == 1
        menu_section = menu_sections[0]
        assert menu_section.label == "Admin"
        assert len(menu_section.items) == 3
        assert "Mon compte backoffice" in {e.label for e in menu_section.items}
        menu_item = [e for e in menu_section.items if e.label == "Mon compte backoffice"][0]
        assert menu_item.url == url_for("backoffice_web.bo_users.get_bo_user", user_id=user.id, active_tab="roles")
