"""Add CollectiveBookingStatus.PENDING_REIMBURSEMENT"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "41f046c7025f"
down_revision = "a94a6d202f5a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE bookingstatus ADD VALUE IF NOT EXISTS 'PENDING_REIMBURSEMENT';")


def downgrade() -> None:
    op.execute("ALTER TYPE bookingstatus RENAME TO bookingstatus_old")
    op.execute("""
        CREATE TYPE bookingstatus AS ENUM (
                'PENDING',
                'CONFIRMED',
                'USED',
                'CANCELLED',
                'REIMBURSED'
        );
    """)
    op.execute("ALTER TABLE collective_booking ADD COLUMN status_tmp text;")
    op.execute('UPDATE collective_booking SET status_tmp="status"::text;')
    op.execute('ALTER TABLE collective_booking DROP COLUMN "status";')
    op.execute("ALTER TABLE collective_booking ADD COLUMN status bookingstatus;")
    op.execute('UPDATE collective_booking SET "status"=status_tmp::bookingstatus;')
    op.execute('ALTER TABLE collective_booking ALTER COLUMN "status" SET NOT NULL;')
    op.execute('ALTER TABLE collective_booking DROP COLUMN "status_tmp";')
    op.execute("DROP TYPE IF EXISTS bookingstatus_old")
