"""
add new value to CollectiveBookingCancellationReasons enum
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1112f930c271"
down_revision = "72fa9c444b5a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE bookingcancellationreasons ADD VALUE IF NOT EXISTS 'PUBLIC_API'")


def downgrade() -> None:
    pass
