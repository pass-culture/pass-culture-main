"""Add backoffice cancellation reason for individual and collective bookings
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4205ae20bb32"
down_revision = "d41989bc9019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason ADD VALUE IF NOT EXISTS 'BACKOFFICE'")
    op.execute("ALTER TYPE bookingcancellationreasons ADD VALUE IF NOT EXISTS 'BACKOFFICE'")


def downgrade() -> None:
    op.execute("ALTER TYPE bookingcancellationreasons RENAME TO bookingcancellationreasons_old")
    op.execute(
        "CREATE TYPE bookingcancellationreasons AS ENUM('OFFERER','BENEFICIARY','EXPIRED', 'FRAUD', 'REFUSED_BY_INSTITUTE', 'REFUSED_BY_HEADMASTER', 'PUBLIC_API', 'FINANCE_INCIDENT')"
    )
    op.execute(
        (
            'ALTER TABLE collective_booking ALTER COLUMN "cancellationReason" TYPE bookingcancellationreasons USING '
            '"cancellationReason"::text::bookingcancellationreasons'
        )
    )
    op.execute("DROP TYPE bookingcancellationreasons_old")

    op.execute("ALTER TYPE cancellation_reason RENAME TO cancellation_reason_old")
    op.execute(
        "CREATE TYPE cancellation_reason AS ENUM('OFFERER','BENEFICIARY','EXPIRED', 'FRAUD', 'REFUSED_BY_INSTITUTE', 'FINANCE_INCIDENT', 'BACKOFFICE')"
    )
    op.execute(
        (
            'ALTER TABLE booking ALTER COLUMN "cancellationReason" TYPE cancellation_reason USING '
            '"cancellationReason"::text::cancellation_reason'
        )
    )
    op.execute("DROP TYPE cancellation_reason_old")
