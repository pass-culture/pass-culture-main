"""Add NOT NULL constraint on "venue.activity" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1b33a3a686da"
down_revision = "3aafea6467ce"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("venue", "activity", nullable=False)


def downgrade() -> None:
    op.alter_column("venue", "activity", nullable=True)
