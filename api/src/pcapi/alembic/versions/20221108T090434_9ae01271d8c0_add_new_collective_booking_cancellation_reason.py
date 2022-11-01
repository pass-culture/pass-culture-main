"""add_new_collective_booking_cancellation_reason
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9ae01271d8c0"
down_revision = "92484e2002ee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE bookingcancellationreasons ADD VALUE 'DEACTIVATION'")


def downgrade() -> None:
    op.execute("ALTER TYPE bookingcancellationreasons RENAME TO bookingcancellationreasons_old")
    op.execute(
        "CREATE TYPE bookingcancellationreasons AS ENUM('OFFERER','BENEFICIARY','EXPIRED','FRAUD','REFUSED_BY_INSTITUTE')"
    )
    op.execute(
        (
            'ALTER TABLE collective_booking ALTER COLUMN "cancellationReason" TYPE bookingcancellationreasons USING '
            '"cancellationReason"::text::bookingcancellationreasons'
        )
    )

    op.execute("DROP TYPE bookingcancellationreasons_old")
