"""Add partial index on stock.beginningDatetime
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "56d7319f1713"
down_revision = "74409447111a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.create_index(
        "ix_stock_beginningDatetime_partial",
        "stock",
        ["beginningDatetime"],
        unique=False,
        postgresql_where=sa.text('"beginningDatetime" IS NOT NULL'),
        postgresql_concurrently=True,
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_index(
        "ix_stock_beginningDatetime_partial",
        table_name="stock",
        postgresql_where=sa.text('"beginningDatetime" IS NOT NULL'),
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
