"""add_refused_by_headmaster_cancellation_reason
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d223c62b00b8"
down_revision = "c14229719483"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE bookingcancellationreasons ADD VALUE 'REFUSED_BY_HEADMASTER'")


def downgrade() -> None:
    op.execute("ALTER TYPE bookingcancellationreasons RENAME TO bookingcancellationreasons_old")
    op.execute(
        "CREATE TYPE bookingcancellationreasons AS ENUM('OFFERER','BENEFICIARY','EXPIRED', 'FRAUD', 'REFUSED_BY_INSTITUTE')"
    )
    op.execute(
        (
            'ALTER TABLE collective_booking ALTER COLUMN "cancellationReason" TYPE bookingcancellationreasons USING '
            '"cancellationReason"::text::bookingcancellationreasons'
        )
    )

    op.execute("DROP TYPE bookingcancellationreasons_old")
