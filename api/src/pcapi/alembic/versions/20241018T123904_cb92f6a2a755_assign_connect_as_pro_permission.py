"""Assign new CONNECT_AS_PRO permission to backoffice roles which can already "connect-as" """

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cb92f6a2a755"
down_revision = "5adc36a47352"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT DISTINCT "roleId", (SELECT id FROM permission p WHERE p.name = 'CONNECT_AS_PRO')
        FROM role_permission
        JOIN permission on role_permission."permissionId" = permission.id
        WHERE permission.name = 'MANAGE_PRO_ENTITY'
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )


def downgrade() -> None:
    pass
