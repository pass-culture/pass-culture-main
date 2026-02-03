"""Add booking_status.PENDING_REIMBURSEMENT"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "158f5287c6f0"
down_revision = "41f046c7025f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE booking_status ADD VALUE IF NOT EXISTS 'PENDING_REIMBURSEMENT';")


def downgrade() -> None:
    op.execute("ALTER TYPE booking_status RENAME TO booking_status_old")
    op.execute("""
        CREATE TYPE booking_status AS ENUM (
                'PENDING',
                'CONFIRMED',
                'USED',
                'CANCELLED',
                'REIMBURSED'
        );
    """)
    op.execute("ALTER TABLE booking ADD COLUMN status_tmp text;")
    op.execute('UPDATE booking SET status_tmp="status"::text;')
    op.execute('ALTER TABLE booking DROP COLUMN "status";')
    op.execute("ALTER TABLE booking ADD COLUMN status booking_status;")
    op.execute('UPDATE booking SET "status"=status_tmp::booking_status;')
    op.execute('ALTER TABLE booking ALTER COLUMN "status" SET NOT NULL;')
    op.execute('ALTER TABLE booking DROP COLUMN "status_tmp";')
    op.execute("DROP TYPE IF EXISTS booking_status_old")
