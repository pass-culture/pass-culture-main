from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models


ROLE_PERMISSIONS: dict[str, list[perm_models.Permissions]] = {
    "admin": [
        perm_models.Permissions.MANAGE_PERMISSIONS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
        perm_models.Permissions.DELETE_OFFERER_TAG,
        perm_models.Permissions.MANAGE_OFFERER_TAG,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
    ],
    "support-N1": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
    ],
    "support-N2": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
    ],
    "support-PRO": [
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.DELETE_PRO_ENTITY,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
    ],
    "support-PRO-N2": [
        perm_models.Permissions.MOVE_SIRET,
        perm_models.Permissions.MANAGE_PROVIDERS,
    ],
    "fraude-conformite": [
        perm_models.Permissions.FRAUD_ACTIONS,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.UNSUSPEND_USER,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
    ],
    "daf": [
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
    ],
    "responsable-daf": [
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.CREATE_REIMBURSEMENT_RULES,
    ],
    "bizdev": [],
    "programmation": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
    ],
    "homologation": [],
    "product-management": [
        perm_models.Permissions.FEATURE_FLIPPING,
    ],
    "charge-developpement": [],
}


def create_roles_with_permissions() -> dict[str, perm_models.Role]:
    perms_in_db = {perm.name: perm for perm in perm_models.Permission.query.all()}

    roles = {
        name: perm_factories.RoleFactory(name=name, permissions=[perms_in_db[perm.name] for perm in perms])
        for name, perms in ROLE_PERMISSIONS.items()
    }
    return roles
