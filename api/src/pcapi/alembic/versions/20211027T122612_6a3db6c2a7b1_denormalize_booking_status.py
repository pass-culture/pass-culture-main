"""denormalize_booking_status
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6a3db6c2a7b1"
down_revision = "3908af1a50e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE booking_status ADD VALUE 'REIMBURSED'")
    op.add_column("booking", sa.Column("reimbursementDate", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.execute("ALTER TYPE booking_status RENAME TO booking_status_old;")
    op.execute("UPDATE booking SET status='USED'::booking_status_old WHERE status='REIMBURSED'::booking_status_old;")
    op.execute("ALTER TABLE booking ALTER COLUMN status TYPE TEXT;")
    op.execute("CREATE TYPE booking_status AS ENUM ('PENDING', 'CONFIRMED', 'USED', 'CANCELLED');")
    op.execute("ALTER TABLE booking ALTER COLUMN status TYPE booking_status USING status::booking_status;")
    op.execute("DROP TYPE booking_status_old;")
    op.drop_column("booking", "reimbursementDate")
