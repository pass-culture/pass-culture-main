"""fix_permission_management_permission
"""
from alembic import op

from pcapi.core.permissions.models import Permissions


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d0ab8c9d794e"
down_revision = "80c915a0b453"
branch_labels = None
depends_on = None


def upgrade():
    """
    - delete the "gérer les droits" permission
    - change the admin "gérer les droits" permission for the "MANAGE_PERMISSIONS" one
    """
    op.execute(
        f"""
        WITH old_manage_perm(id) AS (
            DELETE FROM permission
            WHERE name = '{Permissions.MANAGE_PERMISSIONS.value}'
            RETURNING id
        ), new_manage_perm(id) AS (
            SELECT id FROM permission
            WHERE name = '{Permissions.MANAGE_PERMISSIONS.name}'
        )
        UPDATE role_permission
        SET "permissionId" = (SELECT id FROM new_manage_perm  LIMIT 1)
        WHERE "roleId" = (SELECT id FROM role WHERE name = 'admin')
          AND "permissionId" = (SELECT id FROM old_manage_perm  LIMIT 1);
    """
    )


def downgrade():
    """
    - recreate the "gérer les droits" permission
    - change the admin "MANAGE_PERMISSIONS" permission for the "gérer les droits" one
    """
    op.execute(
        f"""
        WITH old_manage_perm(id) AS (
            INSERT INTO permission (name)
            VALUES ('{Permissions.MANAGE_PERMISSIONS.value}')
            RETURNING id
        ), new_manage_perm(id) AS (
            SELECT id FROM permission
            WHERE name = '{Permissions.MANAGE_PERMISSIONS.name}'
        )
        UPDATE role_permission
        SET "permissionId" = (SELECT id FROM old_manage_perm LIMIT 1)
        WHERE "roleId" = (SELECT id FROM role WHERE name = 'admin')
          AND "permissionId" = (SELECT id FROM new_manage_perm  LIMIT 1);
    """
    )
