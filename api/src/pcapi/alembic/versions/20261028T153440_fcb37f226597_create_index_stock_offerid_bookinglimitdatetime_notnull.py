"""Create partial index "ix_stock_offerId_bookingLimitDatetime_notnull" on "stock" table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fcb37f226597"
down_revision = "83175286f95b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.create_index(
            "ix_stock_offerId_bookingLimitDatetime_notnull",
            "stock",
            ["offerId", "bookingLimitDatetime"],
            unique=False,
            postgresql_where=sa.text('"isSoftDeleted" IS NOT TRUE AND "bookingLimitDatetime" IS NOT NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(
            sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
            )
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.drop_index(
            "ix_stock_offerId_bookingLimitDatetime_notnull",
            table_name="stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(
            sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
            )
        )
