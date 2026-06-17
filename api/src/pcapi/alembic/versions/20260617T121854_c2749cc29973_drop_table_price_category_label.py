"""Drop table: price_category_label"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c2749cc29973"
down_revision = "a6e040de3f81"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("price_category_label")


def downgrade() -> None:
    op.create_table(
        "price_category_label",
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("label", "venueId", name="unique_label_venue"),
    )
    op.create_index(op.f("ix_price_category_label_venueId"), "price_category_label", ["venueId"], unique=False)
