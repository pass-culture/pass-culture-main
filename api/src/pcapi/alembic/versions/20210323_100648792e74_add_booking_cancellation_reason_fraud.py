"""add_booking_cancellation_reason_fraud

Revision ID: 100648792e74
Revises: 508c975a420b
Create Date: 2021-03-23 14:43:11.529718

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "100648792e74"
down_revision = "508c975a420b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason ADD VALUE 'FRAUD'")


def downgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason RENAME TO cancellation_reason_old")
    op.execute("CREATE TYPE cancellation_reason AS ENUM('OFFERER','BENEFICIARY','EXPIRED')")
    op.execute(
        (
            'ALTER TABLE booking ALTER COLUMN "cancellationReason" TYPE cancellation_reason USING '
            '"cancellationReason"::text::cancellation_reason'
        )
    )

    op.execute("DROP TYPE cancellation_reason_old")
