"""Add index on booking.cancellationUserId"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1007ef88d004"
down_revision = "03fe9009ff8e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        # Tested on staging: executed in: 157.314s (2.0 minutes 37 seconds)
        op.execute("SET SESSION statement_timeout='900s'")
        op.create_index(
            "ix_booking_cancellationUserId",
            "booking",
            ["cancellationUserId"],
            unique=False,
            postgresql_where=sa.text('"cancellationUserId" IS NOT NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_booking_cancellationUserId",
            table_name="booking",
            postgresql_where=sa.text('"cancellationUserId" IS NOT NULL'),
            postgresql_concurrently=True,
            if_exists=True,
        )
