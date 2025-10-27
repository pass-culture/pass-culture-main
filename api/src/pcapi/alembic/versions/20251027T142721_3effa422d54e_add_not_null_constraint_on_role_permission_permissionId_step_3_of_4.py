"""Add NOT NULL constraint on "role_permission.permissionId" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3effa422d54e"
down_revision = "77934693d4d3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("role_permission", "permissionId", nullable=False)


def downgrade() -> None:
    op.alter_column("role_permission", "permissionId", nullable=True)
