"""Add OfferPriceLimitationRule table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b1c9eff03366"
down_revision = "1ac22a2f313e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offer_price_limitation_rule",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("subcategoryId", sa.Text(), nullable=False),
        sa.Column("rate", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subcategoryId"),
    )


def downgrade() -> None:
    op.drop_table("offer_price_limitation_rule")
