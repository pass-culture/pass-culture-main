"""
create table offer metadata"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "185416119576"
down_revision = "87e78f5b2185"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "offer_meta_data",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("videoUrl", sa.TEXT(), nullable=True),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_offer_meta_data_offerId"), "offer_meta_data", ["offerId"], unique=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_offer_meta_data_offerId"),
            table_name="offer_meta_data",
            postgresql_concurrently=True,
            if_exists=True,
        )
    op.drop_table("offer_meta_data")
