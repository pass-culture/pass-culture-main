"""Add partial index on stock.bookingLimitDatetime
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "74409447111a"
down_revision = "a09a9a890bcb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.create_index(
        "ix_stock_bookingLimitDatetime_partial",
        "stock",
        ["bookingLimitDatetime"],
        unique=False,
        postgresql_where=sa.text('"bookingLimitDatetime" IS NOT NULL'),
        postgresql_concurrently=True,
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_index(
        "ix_stock_bookingLimitDatetime_partial",
        table_name="stock",
        postgresql_where=sa.text('"bookingLimitDatetime" IS NOT NULL'),
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
