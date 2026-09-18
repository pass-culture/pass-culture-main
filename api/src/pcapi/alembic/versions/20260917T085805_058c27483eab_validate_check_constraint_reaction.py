"""Validate check constraint on reaction"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "058c27483eab"
down_revision = "fec32ca73a57"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")

    op.execute("""ALTER TABLE reaction VALIDATE CONSTRAINT "reaction_offer_product_check" """)

    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
