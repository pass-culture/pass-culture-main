"""Add unique index on product.ean"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f84fb33f512c"
down_revision = "94d104d65c23"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    if not settings.IS_PROD:
        with op.get_context().autocommit_block():
            op.execute(sa.text("SET statement_timeout = 0;"))

            op.execute(
                sa.text(
                    """ CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "unique_ix_product_ean" ON product ("ean"); """
                )
            )

            op.execute(sa.text(f"SET statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}"))


def downgrade() -> None:
    pass
