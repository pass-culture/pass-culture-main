"""Create OfferInstructor"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5206cabe15a3"
down_revision = "4102bbc59a50"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "offer_instructor",
        sa.Column("instructorId", sa.BigInteger(), nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instructorId", "offerId", name="unique_offer_instructor"),
    )
    op.create_foreign_key(
        "offer_instructor_instructorId_fkey",
        "offer_instructor",
        "user",
        ["instructorId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.create_foreign_key(
        "offer_instructor_offerId_fkey",
        "offer_instructor",
        "offer",
        ["offerId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.create_index(
        op.f("ix_offer_instructor_offerId"),
        "offer_instructor",
        ["offerId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_offer_instructor_instructorId"),
        "offer_instructor",
        ["instructorId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("offer_instructor")
