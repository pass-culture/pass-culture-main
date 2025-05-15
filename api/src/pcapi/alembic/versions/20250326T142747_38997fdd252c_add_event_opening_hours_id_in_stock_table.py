"""Add "eventOpeningHoursId" in stock table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "38997fdd252c"
down_revision = "508b85341c00"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("stock", sa.Column("eventOpeningHoursId", sa.BigInteger(), nullable=True))
    op.create_check_constraint(
        "check_stock_with_opening_hours_does_not_have_beginningDatetime",
        "stock",
        '"eventOpeningHoursId" IS NULL OR "beginningDatetime" IS NULL',
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("check_stock_with_opening_hours_does_not_have_beginningDatetime", "stock", type_="check")
    op.drop_column("stock", "eventOpeningHoursId")
