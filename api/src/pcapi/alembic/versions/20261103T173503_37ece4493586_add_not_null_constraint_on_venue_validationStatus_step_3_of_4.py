"""Add NOT NULL constraint on "venue.validationStatus" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "37ece4493586"
down_revision = "41383677de6f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("venue", "validationStatus", nullable=False)


def downgrade() -> None:
    op.alter_column("venue", "validationStatus", nullable=True)
