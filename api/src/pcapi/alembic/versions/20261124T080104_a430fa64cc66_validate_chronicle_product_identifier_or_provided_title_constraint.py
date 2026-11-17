"""Validate "check_has_product_identifier_or_provided_title" constraint on "chronicle" table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a430fa64cc66"
down_revision = "a4854666bc4e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE chronicle VALIDATE CONSTRAINT "check_has_product_identifier_or_provided_title" """)
    op.execute(
        sa.text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
