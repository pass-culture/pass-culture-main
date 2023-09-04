"""Add FINANCE_INCIDENT to booking cancellation reasons
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e51bb5f173dd"
down_revision = "e8b807a89859"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # booking cancellation reasons update
    op.execute("ALTER TYPE cancellation_reason ADD VALUE 'FINANCE_INCIDENT'")
    # collective booking cancellation reasons update
    op.execute("ALTER TYPE bookingcancellationreasons ADD VALUE 'FINANCE_INCIDENT'")


def downgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason RENAME TO cancellation_reason_old")
    op.execute(
        "CREATE TYPE cancellation_reason AS ENUM('OFFERER','BENEFICIARY','EXPIRED', 'FRAUD', 'REFUSED_BY_INSTITUTE')"
    )
    op.execute(
        (
            'ALTER TABLE booking ALTER COLUMN "cancellationReason" TYPE cancellation_reason USING '
            '"cancellationReason"::text::cancellation_reason'
        )
    )
    op.execute("DROP TYPE cancellation_reason_old")

    op.execute("ALTER TYPE bookingcancellationreasons RENAME TO bookingcancellationreasons_old")
    op.execute(
        "CREATE TYPE bookingcancellationreasons AS ENUM('OFFERER','BENEFICIARY','EXPIRED', 'FRAUD', 'REFUSED_BY_INSTITUTE', 'REFUSED_BY_HEADMASTER', 'PUBLIC_API')"
    )
    op.execute(
        (
            'ALTER TABLE collective_booking ALTER COLUMN "cancellationReason" TYPE bookingcancellationreasons USING '
            '"cancellationReason"::text::bookingcancellationreasons'
        )
    )
    op.execute("DROP TYPE bookingcancellationreasons_old")
