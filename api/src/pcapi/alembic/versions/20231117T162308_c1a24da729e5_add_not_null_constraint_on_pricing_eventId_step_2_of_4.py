"""Add NOT NULL constraint on "pricing.eventId" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c1a24da729e5"
down_revision = "ec9e39ae7940"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    # The timeout here has the same value (5 minutes) as `helm upgrade`.
    # If this migration fails, you'll have to execute it manually.
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute('ALTER TABLE "pricing" VALIDATE CONSTRAINT "pricing_eventId_not_null_constraint"')
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
