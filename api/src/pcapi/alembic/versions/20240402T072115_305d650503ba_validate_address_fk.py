"""Validate address related foreign keys"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "305d650503ba"
down_revision = "4959dc20bd41"
branch_labels: tuple | None = None
depends_on: tuple | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE stock VALIDATE CONSTRAINT "stock_offererAddressId_fkey" """)
    op.execute("""ALTER TABLE offer VALIDATE CONSTRAINT "offer_offererAddressId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
