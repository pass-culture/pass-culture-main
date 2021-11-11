"""add_institution_head_to_cancellation_reasons

Revision ID: 7fcfdc9beb40
Revises: 854d09f3b5b7
Create Date: 2021-08-16 17:16:02.736384

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7fcfdc9beb40"
down_revision = "854d09f3b5b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason ADD VALUE 'REFUSED_BY_INSTITUTE'")


def downgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason RENAME TO cancellation_reason_old")
    op.execute("CREATE TYPE cancellation_reason AS ENUM('OFFERER','BENEFICIARY','EXPIRED', 'FRAUD')")
    op.execute(
        (
            'ALTER TABLE booking ALTER COLUMN "cancellationReason" TYPE cancellation_reason USING '
            '"cancellationReason"::text::cancellation_reason'
        )
    )

    op.execute("DROP TYPE cancellation_reason_old")
