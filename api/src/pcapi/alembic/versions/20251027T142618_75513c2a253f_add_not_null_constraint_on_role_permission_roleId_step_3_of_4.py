"""Add NOT NULL constraint on "role_permission.roleId" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "75513c2a253f"
down_revision = "d4e187fab734"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("role_permission", "roleId", nullable=False)


def downgrade() -> None:
    op.alter_column("role_permission", "roleId", nullable=True)
