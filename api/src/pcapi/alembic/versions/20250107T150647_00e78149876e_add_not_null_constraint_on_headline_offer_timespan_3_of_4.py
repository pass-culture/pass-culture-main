"""
Add NOT NULL constraint on "headline_offer.timespan" (step 3 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "00e78149876e"
down_revision = "c125573195bc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("headline_offer", "timespan", nullable=False)


def downgrade() -> None:
    op.alter_column("headline_offer", "timespan", nullable=True)
