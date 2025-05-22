"""add offer_compliance table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a84a6a5c506c"
down_revision = "5b903a069f48"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Squawk advice us to use BigInt instead of smallInt, in this case compliance_score is betwwen 0 and 100.
    # Do not waste space with a bigInt
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_table(
        "offer_compliance",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("compliance_score", sa.SmallInteger(), nullable=False),
        sa.Column("compliance_reasons", postgresql.ARRAY(sa.String()), nullable=False),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_offer_compliance_offerId"),
            "offer_compliance",
            ["offerId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    op.drop_table("offer_compliance")
