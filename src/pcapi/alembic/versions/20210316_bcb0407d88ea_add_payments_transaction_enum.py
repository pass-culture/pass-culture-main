"""add_payments_transaction_enum

Revision ID: bcb0407d88ea
Revises: fccbd701588b
Create Date: 2021-03-16 15:02:16.688269

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "bcb0407d88ea"
down_revision = "fccbd701588b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE transactionstatus ADD VALUE 'UNDER_REVIEW'")


def downgrade() -> None:
    op.execute("ALTER TYPE transactionstatus RENAME TO transactionstatus_old")
    op.execute("CREATE TYPE transactionstatus AS ENUM('PENDING','NOT_PROCESSABLE','SENT','ERROR','RETRY','BANNED')")
    op.execute(
        (
            "ALTER TABLE payment_status ALTER COLUMN status TYPE transactionstatus USING "
            "status::text::transactionstatus"
        )
    )
    op.execute("DROP TYPE transactionstatus_old")
