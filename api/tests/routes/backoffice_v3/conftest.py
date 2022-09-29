import pytest

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


ROLE_PERMISSIONS: dict[str, list[perm_models.Permissions]] = {
    "admin": [
        perm_models.Permissions.MANAGE_PERMISSIONS,
    ],
    "support-N1": [
        perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
    ],
    "support-N2": [
        perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
    ],
    "support-pro": [
        perm_models.Permissions.SEARCH_PRO_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
    ],
    "fraude-conformite": [
        perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.SEARCH_PRO_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.VALIDATE_OFFERER,
    ],
    "daf": [],
    "bizdev": [],
    "programmation": [],
    "product-management": [],
}


@pytest.fixture(scope="function", name="roles_with_permissions")
def roles_with_permissions_fixture() -> None:
    perms_in_db = {perm.name: perm for perm in perm_models.Permission.query.all()}

    for name, perms in ROLE_PERMISSIONS.items():
        role = perm_models.Role(name=name, permissions=[perms_in_db[perm.name] for perm in perms])
        db.session.add(role)

    db.session.commit()


@pytest.fixture(scope="function", name="legit_user")
def legit_user_fixture(roles_with_permissions) -> users_models.User:
    user = users_factories.UserFactory(isActive=True)

    user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user)
    backoffice_api.upsert_roles(user, list(perm_models.Roles))

    db.session.commit()

    return user
