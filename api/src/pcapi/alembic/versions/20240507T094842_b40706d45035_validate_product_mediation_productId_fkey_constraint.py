"""
Validate product_mediation_productId_fkey constraint
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b40706d45035"
down_revision = "400f736caab1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute("""ALTER TABLE product_mediation VALIDATE CONSTRAINT "product_mediation_productId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute("""ALTER TABLE product_mediation VALIDATE CONSTRAINT "product_mediation_productId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
