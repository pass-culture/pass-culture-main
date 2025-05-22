"""Assign new READ_PERMISSIONS permission to backoffice roles which already manage permissions"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "22e94edcc427"
down_revision = "0a17873525e7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT DISTINCT "roleId", (SELECT id FROM permission p WHERE p.name = 'READ_PERMISSIONS')
        FROM role_permission
        JOIN permission on role_permission."permissionId" = permission.id
        WHERE permission.name = 'MANAGE_PERMISSIONS'
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        VALUES (
            (SELECT id FROM role r WHERE r.name = 'admin'),
            (SELECT id FROM permission p WHERE p.name = 'READ_PERMISSIONS')
        )
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )


def downgrade() -> None:
    pass
