"""Add index for stock bookability"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b91453933c08"
down_revision = "afe8049e9364"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.create_index(
        op.f("ix_stock_bookability"),
        "stock",
        ["offerId", "beginningDatetime", "isSoftDeleted", "bookingLimitDatetime", "quantity", "dnBookedQuantity"],
        unique=False,
        if_not_exists=True,
        postgresql_concurrently=True,
    )
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index(
        op.f("ix_stock_bookability"),
        table_name="stock",
        if_exists=True,
        postgresql_concurrently=True,
    )
    op.execute("BEGIN")
