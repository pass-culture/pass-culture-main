import pytest

from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
import pcapi.core.users.backoffice.api as backoffice_api
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(scope="function", name="permissions")
def permissions_fixture() -> list[perm_models.Permissions]:
    return perm_models.Permission.query.order_by(perm_models.Permission.name).limit(5).all()


@pytest.fixture(scope="function", name="roles")
def roles_fixture(permissions) -> list[perm_models.Roles]:
    roles = (
        perm_models.Role.query.filter(
            perm_models.Role.name.in_(
                [
                    perm_models.Roles.SUPPORT_N1.value,
                    perm_models.Roles.SUPPORT_N2.value,
                    perm_models.Roles.SUPPORT_PRO.value,
                ]
            )
        )
        .order_by(perm_models.Role.name)
        .all()
    )

    roles[0].permissions = [permissions[1], permissions[3]]
    roles[1].permissions = [permissions[2], permissions[3]]
    roles[2].permissions = [permissions[0], permissions[1]]

    db.session.bulk_save_objects(roles)
    db.session.commit()

    return roles


def test_update_roles_from_no_profile(permissions, roles) -> None:
    user: users_models.User = users_factories.UserFactory()

    backoffice_api.upsert_roles(user, [perm_models.Roles.SUPPORT_N1, perm_models.Roles.SUPPORT_PRO])

    assert set(user.backoffice_profile.roles) == {roles[0], roles[2]}


def test_update_roles_add_one_role(permissions, roles) -> None:
    user: users_models.User = users_factories.AdminFactory(backoffice_profile__roles=[roles[1]])

    backoffice_api.upsert_roles(user, [perm_models.Roles.SUPPORT_N2, perm_models.Roles.SUPPORT_PRO])

    assert set(user.backoffice_profile.roles) == {roles[1], roles[2]}


def test_update_roles_remove_one_role(permissions, roles) -> None:
    user: users_models.User = users_factories.AdminFactory(backoffice_profile__roles=[roles[0], roles[1]])

    backoffice_api.upsert_roles(user, [perm_models.Roles.SUPPORT_N2])

    assert user.backoffice_profile.roles == [roles[1]]


def test_update_roles_add_remove_role(permissions, roles) -> None:
    user: users_models.User = users_factories.AdminFactory(backoffice_profile__roles=[roles[0], roles[1]])

    backoffice_api.upsert_roles(user, [perm_models.Roles.SUPPORT_N2, perm_models.Roles.SUPPORT_PRO])

    assert set(user.backoffice_profile.roles) == {roles[1], roles[2]}


def test_update_roles_clear_roles(permissions, roles) -> None:
    user: users_models.User = users_factories.AdminFactory(backoffice_profile__roles=[roles[0], roles[1]])

    backoffice_api.upsert_roles(user, [])

    assert user.backoffice_profile.roles == []


def test_update_roles_keep_roles(permissions, roles) -> None:
    user: users_models.User = users_factories.AdminFactory(backoffice_profile__roles=[roles[1], roles[2]])

    backoffice_api.upsert_roles(user, [perm_models.Roles.SUPPORT_N2, perm_models.Roles.SUPPORT_PRO])

    assert set(user.backoffice_profile.roles) == {roles[1], roles[2]}


def test_fetch_user_with_profile(permissions, roles) -> None:
    user: users_models.User = users_factories.AdminFactory(backoffice_profile__roles=[roles[0], roles[1]])

    user_id = user.id
    with assert_num_queries(1):
        user_with_profile = backoffice_api.fetch_user_with_profile(user_id)

        # user_with_profile.backoffice_profile.permission contains Permissions enum items
        # permissions contains Permission objects from database
        assert set(perm.name for perm in user_with_profile.backoffice_profile.permissions) == set(
            perm.name for perm in permissions[1:4]
        )
