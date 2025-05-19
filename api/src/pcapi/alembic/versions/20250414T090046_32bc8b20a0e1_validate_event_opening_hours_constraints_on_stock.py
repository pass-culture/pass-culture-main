"""Validate 'stock_eventOpeningHoursId_fkey' and 'check_stock_with_opening_hours_does_not_have_beginningDatetime' constraints"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "32bc8b20a0e1"
down_revision = "cf1495e11a53"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("SET SESSION statement_timeout = '300s'"))

    op.execute(sa.text('ALTER TABLE stock VALIDATE CONSTRAINT "stock_eventOpeningHoursId_fkey";'))
    op.execute(
        sa.text(
            'ALTER TABLE stock VALIDATE CONSTRAINT "check_stock_with_opening_hours_does_not_have_beginningDatetime";'
        )
    )

    op.execute(sa.text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))


def downgrade() -> None:
    pass
