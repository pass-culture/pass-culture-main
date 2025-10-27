"""Add NOT NULL constraint on "role_permission.permissionId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ef1c3fac38fd"
down_revision = "7ee89e968019"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "role_permission" DROP CONSTRAINT IF EXISTS "role_permission_permissionId_not_null_constraint";
        ALTER TABLE "role_permission" ADD CONSTRAINT "role_permission_permissionId_not_null_constraint" CHECK ("permissionId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("role_permission_permissionId_not_null_constraint", table_name="role_permission")
