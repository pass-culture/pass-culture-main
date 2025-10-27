"""Add NOT NULL constraint on "role_permission.roleId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7ee89e968019"
down_revision = "75513c2a253f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("role_permission_roleId_not_null_constraint", table_name="role_permission")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "role_permission" ADD CONSTRAINT "role_permission_roleId_not_null_constraint" CHECK ("roleId" IS NOT NULL) NOT VALID"""
    )
