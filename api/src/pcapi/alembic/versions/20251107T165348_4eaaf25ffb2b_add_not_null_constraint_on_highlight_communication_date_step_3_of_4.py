"""Add NOT NULL constraint on "highlight.communication_date" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4eaaf25ffb2b"
down_revision = "3407405ead9c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("highlight", "communication_date", nullable=False)


def downgrade() -> None:
    op.alter_column("highlight", "communication_date", nullable=True)
