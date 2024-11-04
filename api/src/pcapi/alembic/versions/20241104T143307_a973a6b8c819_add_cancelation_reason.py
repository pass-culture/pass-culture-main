"""ADD BACKOFFICE_OFFERER_BUSINESS_CLOSED as reason to cancel a booking"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a973a6b8c819"
down_revision = "a84a6a5c506c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason ADD VALUE  IF NOT EXISTS 'BACKOFFICE_OFFERER_BUSINESS_CLOSED'")
    op.execute("ALTER TYPE bookingcancellationreasons ADD VALUE IF NOT EXISTS 'BACKOFFICE_OFFERER_BUSINESS_CLOSED'")


def downgrade() -> None:
    pass
