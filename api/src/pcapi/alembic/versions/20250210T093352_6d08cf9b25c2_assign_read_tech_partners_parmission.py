"""Assign new READ_TECH_PARTNERS permission to backoffice roles"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6d08cf9b25c2"
down_revision = "00722e04ea13"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Permission must be created here because it would be automatically created AFTER post migration!
    op.execute(
        """
        INSERT INTO permission ("name", "category")
        VALUES ('READ_TECH_PARTNERS', NULL)
        ON CONFLICT ("name") DO NOTHING
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT DISTINCT "roleId", (SELECT id FROM permission p WHERE p.name = 'READ_TECH_PARTNERS')
        FROM role_permission
        JOIN permission on role_permission."permissionId" = permission.id
        WHERE permission.name = 'MANAGE_TECH_PARTNERS'
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        VALUES (
            (SELECT id FROM role r WHERE r.name = 'charge_developpement'),
            (SELECT id FROM permission p WHERE p.name = 'READ_TECH_PARTNERS')
        )
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        VALUES (
            (SELECT id FROM role r WHERE r.name = 'lecture_seule'),
            (SELECT id FROM permission p WHERE p.name = 'READ_TECH_PARTNERS')
        )
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )


def downgrade() -> None:
    pass
