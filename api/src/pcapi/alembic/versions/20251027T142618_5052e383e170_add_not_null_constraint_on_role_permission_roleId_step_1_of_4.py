"""Add NOT NULL constraint on "role_permission.roleId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5052e383e170"
down_revision = "122e253ad2d6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "role_permission" DROP CONSTRAINT IF EXISTS "role_permission_roleId_not_null_constraint";
        ALTER TABLE "role_permission" ADD CONSTRAINT "role_permission_roleId_not_null_constraint" CHECK ("roleId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("role_permission_roleId_not_null_constraint", table_name="role_permission")
