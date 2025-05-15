"""Add index on cancellationReason column of Booking table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fc7dd42a29ac"
down_revision = "232786daf672"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout='400s'")
    op.create_index(
        index_name="ix_booking_cancellation_reason",
        table_name="booking",
        if_not_exists=True,
        columns=["cancellationReason"],
        unique=False,
        postgresql_where=sa.text('"cancellationReason" IS NOT NULL'),
        postgresql_concurrently=True,
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.drop_index(
        index_name="ix_booking_cancellation_reason",
        table_name="booking",
    )
