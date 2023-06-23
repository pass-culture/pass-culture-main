"""Add bookingContact to offer table
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3eb1ca346ea8"
down_revision = "904635ecbc38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.add_column("offer", sa.Column("bookingContact", sa.String(length=120), nullable=True))
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_column("offer", "bookingContact")
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
