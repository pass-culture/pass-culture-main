"""
validate constraint collective booking_cancellation_user_fk
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "257bb3c980a7"
down_revision = "e068f2c51128"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
    op.execute("""ALTER TABLE collective_booking VALIDATE CONSTRAINT "collective_booking_cancellation_user_fk" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
