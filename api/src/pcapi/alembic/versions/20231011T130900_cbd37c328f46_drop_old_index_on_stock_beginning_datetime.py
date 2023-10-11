"""Drop old index (including null values) on stock.beginningDatetime
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cbd37c328f46"
down_revision = "56d7319f1713"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_index("ix_stock_beginningDatetime", table_name="stock")
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.create_index(
        "ix_stock_beginningDatetime", "stock", ["beginningDatetime"], unique=False, postgresql_concurrently=True
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
