"""Validate check_ean_validity constraint on product table"""

from alembic import op
from sqlalchemy import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "94d104d65c23"
down_revision = "6d08cf9b25c2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    if not settings.IS_PROD:
        op.execute(text("SET SESSION statement_timeout = '300s'"))

        op.execute(text('ALTER TABLE product VALIDATE CONSTRAINT "check_ean_validity";'))

        op.execute(text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))


def downgrade() -> None:
    pass
