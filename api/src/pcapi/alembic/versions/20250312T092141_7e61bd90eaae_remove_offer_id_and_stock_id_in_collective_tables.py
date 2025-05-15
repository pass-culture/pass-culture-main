"""
Remove offerId from collective_offer and collective_offer_template
and stockId from collective_stock
(used for an old migration from offer to collective_offer)
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7e61bd90eaae"
down_revision = "69add328b9fa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("collective_offer", "offerId")
    op.drop_column("collective_offer_template", "offerId")
    op.drop_column("collective_stock", "stockId")


def downgrade() -> None:
    op.add_column("collective_stock", sa.Column("stockId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column("collective_offer_template", sa.Column("offerId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column("collective_offer", sa.Column("offerId", sa.BIGINT(), autoincrement=False, nullable=True))
