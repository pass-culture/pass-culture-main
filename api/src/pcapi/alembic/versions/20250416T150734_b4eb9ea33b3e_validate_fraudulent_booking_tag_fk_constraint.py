"""Validate FraudulentBookingTag user foreign key constraint
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b4eb9ea33b3e"
down_revision = "b0b1ec888d1b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE fraudulent_booking_tag VALIDATE CONSTRAINT "fraudulent_booking_tag_author_fk" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
