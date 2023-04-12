"""Remove `booking_xor_collective_booking_check` check constraint on `pricing` table"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c00fce7569d7"
down_revision = "ccacb677c93a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE pricing DROP CONSTRAINT IF EXISTS booking_xor_collective_booking_check")


def downgrade() -> None:
    # Do not restore the constraint. It would take too long (or,
    # actually, we would need to make it NOT VALID first and then
    # VALIDATE it later) and we will want to remove it, eventually.
    pass
