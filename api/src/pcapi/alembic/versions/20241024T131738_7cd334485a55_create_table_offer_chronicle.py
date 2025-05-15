"""create table offer_chronicle"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7cd334485a55"
down_revision = "cbf6f244c14c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "offer_chronicle",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("chronicleId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["chronicleId"], ["chronicle.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("offerId", "chronicleId", name="unique_offer_chronicle_constraint"),
    )

    op.create_foreign_key(
        "offer_chronicle_offerId_fkey",
        "offer_chronicle",
        "offer",
        ["offerId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )

    op.execute("COMMIT")
    op.create_index(
        op.f("ix_offer_chronicle_chronicleId"),
        "offer_chronicle",
        ["chronicleId"],
        unique=False,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
    op.create_index(
        op.f("ix_offer_chronicle_offerId"),
        "offer_chronicle",
        ["offerId"],
        unique=False,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index(
        op.f("ix_offer_chronicle_offerId"),
        table_name="offer_chronicle",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.drop_index(
        op.f("ix_offer_chronicle_chronicleId"),
        table_name="offer_chronicle",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.execute("BEGIN")
    op.drop_table("offer_chronicle")
