"""Create CollectiveOfferInstructor"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4102bbc59a50"
down_revision = "31459e23f19a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "collective_offer_instructor",
        sa.Column("instructorId", sa.BigInteger(), nullable=False),
        sa.Column("collectiveOfferId", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instructorId", "collectiveOfferId", name="unique_collective_offer_instructor"),
    )
    op.create_foreign_key(
        "collective_offer_instructor_instructorId_fkey",
        "collective_offer_instructor",
        "user",
        ["instructorId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.create_foreign_key(
        "collective_offer_instructor_collectiveOfferId_fkey",
        "collective_offer_instructor",
        "collective_offer",
        ["collectiveOfferId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.create_index(
        op.f("ix_collective_offer_instructor_collectiveOfferId"),
        "collective_offer_instructor",
        ["collectiveOfferId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_collective_offer_instructor_instructorId"),
        "collective_offer_instructor",
        ["instructorId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("collective_offer_instructor")
