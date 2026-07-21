"""Validate collective_stock check_price_is_not_negative and check_service_price_is_not_negative constraints"""

from alembic import op
from sqlalchemy.sql import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "237683b365aa"
down_revision = "d447cb43ccde"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")

    op.execute("""ALTER TABLE collective_stock VALIDATE CONSTRAINT "check_price_is_not_negative" """)
    op.execute("""ALTER TABLE collective_stock VALIDATE CONSTRAINT "check_service_price_is_not_negative" """)

    op.execute(
        text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
