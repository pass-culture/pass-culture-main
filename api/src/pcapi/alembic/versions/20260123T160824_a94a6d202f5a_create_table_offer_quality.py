"""create table offer quality"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a94a6d202f5a"
down_revision = "7c1693892cbc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "offer_quality",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("completion_score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("offerId", name="ix_offer_quality_offerId"),
    )


def downgrade() -> None:
    op.drop_table("offer_quality", if_exists=True)
