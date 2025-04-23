"""Assign new READ_SPECIAL_EVENTS permission to backoffice roles"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "69add328b9fa"
down_revision = "8caa36f11c23"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Permission must be created here because it would be automatically created AFTER post migration!
    op.execute(
        """
        INSERT INTO permission ("name", "category")
        VALUES ('READ_SPECIAL_EVENTS', NULL)
        ON CONFLICT ("name") DO NOTHING
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT DISTINCT "roleId", (SELECT id FROM permission p WHERE p.name = 'READ_SPECIAL_EVENTS')
        FROM role_permission
        JOIN permission on role_permission."permissionId" = permission.id
        WHERE permission.name = 'MANAGE_SPECIAL_EVENTS'
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        VALUES (
            (SELECT id FROM role r WHERE r.name = 'lecture_seule'),
            (SELECT id FROM permission p WHERE p.name = 'READ_SPECIAL_EVENTS')
        )
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )


def downgrade() -> None:
    pass
