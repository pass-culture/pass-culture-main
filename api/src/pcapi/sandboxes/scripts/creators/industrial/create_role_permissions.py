from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models


ROLE_PERMISSIONS: dict[str, list[perm_models.Permissions]] = {
    "admin": [
        perm_models.Permissions.MANAGE_PERMISSIONS,
        perm_models.Permissions.READ_ADMIN_ACCOUNTS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
        perm_models.Permissions.MANAGE_TAGS_N2,
        perm_models.Permissions.MANAGE_OFFERER_TAG,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
    ],
    "support_n1": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
    ],
    "support_n2": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
    ],
    "support_pro": [
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.DELETE_PRO_ENTITY,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_INCIDENTS,
        perm_models.Permissions.MANAGE_INCIDENTS,
        perm_models.Permissions.MANAGE_TECH_PARTNERS,
    ],
    "support_pro_n2": [
        perm_models.Permissions.MOVE_SIRET,
        perm_models.Permissions.ADVANCED_PRO_SUPPORT,
    ],
    "fraude_conformite": [
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
    ],
    "fraude_jeunes": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.UNSUSPEND_USER,
        perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
    ],
    "daf": [
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_INCIDENTS,
    ],
    "responsable_daf": [
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.CREATE_REIMBURSEMENT_RULES,
    ],
    "partenaire_technique": [],
    "programmation_market": [
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
    ],
    "homologation": [],
    "product_management": [
        perm_models.Permissions.FEATURE_FLIPPING,
    ],
    "charge_developpement": [],
    "lecture_seule": [
        perm_models.Permissions.READ_ADMIN_ACCOUNTS,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
    ],
    "qa": [
        perm_models.Permissions.MANAGE_PERMISSIONS,
        perm_models.Permissions.READ_ADMIN_ACCOUNTS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
        perm_models.Permissions.FEATURE_FLIPPING,
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.UNSUSPEND_USER,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.DELETE_PRO_ENTITY,
        perm_models.Permissions.MOVE_SIRET,
        perm_models.Permissions.ADVANCED_PRO_SUPPORT,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_OFFERER_TAG,
        perm_models.Permissions.MANAGE_TAGS_N2,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.CREATE_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_INCIDENTS,
        perm_models.Permissions.MANAGE_INCIDENTS,
        perm_models.Permissions.MANAGE_TECH_PARTNERS,
    ],
    "global_access": [
        perm_models.Permissions.READ_ADMIN_ACCOUNTS,
        perm_models.Permissions.MANAGE_ADMIN_ACCOUNTS,
        perm_models.Permissions.FEATURE_FLIPPING,
        perm_models.Permissions.PRO_FRAUD_ACTIONS,
        perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS,
        perm_models.Permissions.READ_PUBLIC_ACCOUNT,
        perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT,
        perm_models.Permissions.SUSPEND_USER,
        perm_models.Permissions.UNSUSPEND_USER,
        perm_models.Permissions.READ_PRO_ENTITY,
        perm_models.Permissions.MANAGE_PRO_ENTITY,
        perm_models.Permissions.DELETE_PRO_ENTITY,
        perm_models.Permissions.MOVE_SIRET,
        perm_models.Permissions.ADVANCED_PRO_SUPPORT,
        perm_models.Permissions.MANAGE_BOOKINGS,
        perm_models.Permissions.READ_BOOKINGS,
        perm_models.Permissions.READ_OFFERS,
        perm_models.Permissions.MANAGE_OFFERS,
        perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
        perm_models.Permissions.VALIDATE_OFFERER,
        perm_models.Permissions.MANAGE_OFFERER_TAG,
        perm_models.Permissions.MANAGE_TAGS_N2,
        perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS,
        perm_models.Permissions.READ_REIMBURSEMENT_RULES,
        perm_models.Permissions.CREATE_REIMBURSEMENT_RULES,
        perm_models.Permissions.READ_INCIDENTS,
        perm_models.Permissions.MANAGE_INCIDENTS,
        perm_models.Permissions.MANAGE_TECH_PARTNERS,
    ],
}


def create_roles_with_permissions() -> None:
    # Roles have already been created from enum in sync_db_roles()
    roles_ids_in_db = {role.name: role.id for role in perm_models.Role.query.all()}
    perm_ids_in_db = {perm.name: perm.id for perm in perm_models.Permission.query.all()}

    for role_name, perms in ROLE_PERMISSIONS.items():
        for perm in perms:
            perm_factories.RolePermissionFactory(
                roleId=roles_ids_in_db[role_name], permissionId=perm_ids_in_db[perm.name]
            )
