"""Add NOT NULL constraint on "role_permission.permissionId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8416f459f37b"
down_revision = "3effa422d54e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("role_permission_permissionId_not_null_constraint", table_name="role_permission")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "role_permission" ADD CONSTRAINT "role_permission_permissionId_not_null_constraint" CHECK ("permissionId" IS NOT NULL) NOT VALID"""
    )
