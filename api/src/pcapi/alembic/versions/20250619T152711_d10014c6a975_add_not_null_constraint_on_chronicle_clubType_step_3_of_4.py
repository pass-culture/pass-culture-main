"""Add NOT NULL constraint on "chronicle.clubType" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d10014c6a975"
down_revision = "a2b0b9fae9f5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("chronicle", "clubType", nullable=False)


def downgrade() -> None:
    op.alter_column("chronicle", "clubType", nullable=True)
