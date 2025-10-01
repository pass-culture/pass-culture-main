"""Add NOT NULL constraint on "collective_offer.locationType" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1d9891c08fbd"
down_revision = "02edfe9114d2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_offer", "locationType", nullable=False)


def downgrade() -> None:
    op.alter_column("collective_offer", "locationType", nullable=True)
