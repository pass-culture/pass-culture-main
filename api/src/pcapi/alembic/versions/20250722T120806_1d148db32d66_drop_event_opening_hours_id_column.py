"""Drop eventOpeningHoursId column in stock table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1d148db32d66"
down_revision = "280eae6d44f0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(op.f("stock_eventOpeningHoursId_fkey"), "stock", type_="foreignkey")
    op.drop_column("stock", "eventOpeningHoursId")


def downgrade() -> None:
    op.add_column("stock", sa.Column("eventOpeningHoursId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.execute(
        """
        ALTER TABLE "stock" ADD CONSTRAINT "stock_eventOpeningHoursId_fkey" FOREIGN KEY("eventOpeningHoursId") REFERENCES event_opening_hours (id) NOT VALID;
        """
    )
    op.create_check_constraint(
        "check_stock_with_opening_hours_does_not_have_beginningDatetime",
        "stock",
        '"eventOpeningHoursId" IS NULL OR "beginningDatetime" IS NULL',
        postgresql_not_valid=True,
    )
