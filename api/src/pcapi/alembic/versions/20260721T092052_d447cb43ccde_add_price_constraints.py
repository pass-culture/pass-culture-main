"""Add constraints on collective_stock price and servicePrice"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d447cb43ccde"
down_revision = "8499f0606e34"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_price_is_not_negative",
        table_name="collective_stock",
        condition=sa.text("price >= 0"),
        postgresql_not_valid=True,
    )

    op.create_check_constraint(
        "check_service_price_is_not_negative",
        table_name="collective_stock",
        condition=sa.text('"servicePrice" >= 0'),
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_service_price_is_not_negative",
        table_name="collective_stock",
    )

    op.drop_constraint(
        "check_price_is_not_negative",
        table_name="collective_stock",
    )
