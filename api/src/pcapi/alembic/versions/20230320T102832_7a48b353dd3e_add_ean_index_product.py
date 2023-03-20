"""add_ean_index_product
"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7a48b353dd3e"
down_revision = "26ae10b002ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '900s'""")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS product_ean_idx
        ON product
        USING btree ((("jsonData" ->> 'ean'::text)));
        """
    )
    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "product_ean_idx"
        """
    )
