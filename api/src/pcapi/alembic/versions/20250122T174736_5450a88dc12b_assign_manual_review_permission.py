"""Assign new BENEFICIARY_MANUAL_REVIEW permission to backoffice roles"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5450a88dc12b"
down_revision = "f42c23a1a832"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Permission must be created here because it would be automatically created AFTER post migration!
    op.execute(
        """
        INSERT INTO permission ("name", "category")
        VALUES ('BENEFICIARY_MANUAL_REVIEW', NULL)
        ON CONFLICT ("name") DO NOTHING
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT DISTINCT "roleId", (SELECT id FROM permission p WHERE p.name = 'BENEFICIARY_MANUAL_REVIEW')
        FROM role_permission
        JOIN permission on role_permission."permissionId" = permission.id
        WHERE permission.name = 'BENEFICIARY_FRAUD_ACTIONS'
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        VALUES (
            (SELECT id FROM role r WHERE r.name = 'support_n2'),
            (SELECT id FROM permission p WHERE p.name = 'BENEFICIARY_MANUAL_REVIEW')
        )
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
    """
    )


def downgrade() -> None:
    pass
