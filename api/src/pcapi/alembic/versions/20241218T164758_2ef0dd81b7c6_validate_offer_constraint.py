"""Validate offer ean check constraint"""

from alembic import op
from sqlalchemy import text

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2ef0dd81b7c6"
down_revision = "17a79fcf1646"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    if not settings.IS_PROD:
        op.execute(text("""ALTER TABLE offer VALIDATE CONSTRAINT "check_ean_validity";"""))


def downgrade() -> None:
    pass
