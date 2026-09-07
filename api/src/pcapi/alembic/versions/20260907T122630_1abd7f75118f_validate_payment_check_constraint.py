"""Validate payment check constraint"""

from alembic import op
from sqlalchemy.sql import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1abd7f75118f"
down_revision = "0cb3c303d7dd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")

    op.execute("""ALTER TABLE payment VALIDATE CONSTRAINT "check_iban_and_bic_xor_not_iban_and_not_bic" """)

    op.execute(
        text("SET SESSION statement_timeout=:statement_timeout").bindparams(
            statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT,
        )
    )


def downgrade() -> None:
    pass
