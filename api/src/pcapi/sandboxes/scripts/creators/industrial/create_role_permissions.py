from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models


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
    "support-PRO": [
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


def create_roles_with_permissions() -> dict[str, perm_models.Role]:
    perms_in_db = {perm.name: perm for perm in perm_models.Permission.query.all()}

    roles = {
        name: perm_factories.RoleFactory(name=name, permissions=[perms_in_db[perm.name] for perm in perms])
        for name, perms in ROLE_PERMISSIONS.items()
    }
    return roles
