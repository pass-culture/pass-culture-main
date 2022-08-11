from pcapi import settings
import pcapi.core.users.models as users_models


def _get_permission_mapping() -> dict:
    mapping = {}
    for line in settings.PERMISSIONS.split("\n"):
        if not line:
            continue
        permission, emails = line.split(":")
        mapping[permission] = {email.strip() for email in emails.split(",")}
    return mapping


def has_permission(user: users_models.User, permission: str) -> bool:
    if not user.has_admin_role:  # safety belt, do not remove
        return False
    # Yes, we calculate the mapping on every call. It's fine:
    # - it's fast;
    # - testing is easier;
    # - it's temporary, anyway.
    mapping = _get_permission_mapping()
    emails = mapping.get(permission, set())
    return bool({user.email, "*"} & emails)
