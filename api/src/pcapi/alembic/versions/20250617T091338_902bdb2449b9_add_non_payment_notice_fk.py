"""Validate NonPaymentNotice fkeys"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "902bdb2449b9"
down_revision = "c9e52780e038"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE non_payment_notice VALIDATE CONSTRAINT "non_payment_notice_batchId_fkey" """)
    op.execute("""ALTER TABLE non_payment_notice VALIDATE CONSTRAINT "non_payment_notice_offererId_fkey" """)
    op.execute("""ALTER TABLE non_payment_notice VALIDATE CONSTRAINT "non_payment_notice_venueId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
