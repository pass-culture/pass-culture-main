"""Validate FutureOffers constraints"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ea04f7c88f15"
down_revision = "b587bd63c5b6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE future_offer_reminder VALIDATE CONSTRAINT "future_offer_reminder_userId_fkey" """)
    op.execute("""ALTER TABLE future_offer_reminder VALIDATE CONSTRAINT "future_offer_reminder_futureOfferId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
