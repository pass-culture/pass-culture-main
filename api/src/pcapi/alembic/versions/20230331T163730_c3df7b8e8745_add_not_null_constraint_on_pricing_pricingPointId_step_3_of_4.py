"""Add NOT NULL constraint on "pricing.pricingPointId" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c3df7b8e8745"
down_revision = "ed7b962072df"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("pricing", "pricingPointId", nullable=False)


def downgrade() -> None:
    op.alter_column("pricing", "pricingPointId", nullable=True)
