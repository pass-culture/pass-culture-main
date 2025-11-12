"""Add NOT NULL constraint on "highlight.availability_datespan" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e25d813658b8"
down_revision = "1930d1565439"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("highlight", "availability_datespan", nullable=False)


def downgrade() -> None:
    op.alter_column("highlight", "availability_datespan", nullable=True)
