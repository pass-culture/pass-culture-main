"""validate fkey constraint around chronicle table"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "aac1de8cfaf8"
down_revision = "6519c3689ae8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE chronicle VALIDATE CONSTRAINT "chronicle_userId_fkey" """)
    op.execute("""ALTER TABLE product_chronicle VALIDATE CONSTRAINT "product_chronicle_productId_fkey" """)
    op.execute("""ALTER TABLE offer_chronicle VALIDATE CONSTRAINT "offer_chronicle_offerId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
