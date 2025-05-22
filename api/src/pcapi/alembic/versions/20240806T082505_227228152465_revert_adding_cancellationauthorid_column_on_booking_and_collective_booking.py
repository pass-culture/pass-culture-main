"""
revert adding cancellationAuthorId column on booking and collective_booking
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "227228152465"
down_revision = "4bd28b6d5d6c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE booking DROP CONSTRAINT IF EXISTS booking_cancellation_author_fk")
    op.execute("ALTER TABLE collective_booking DROP CONSTRAINT IF EXISTS collective_booking_cancellation_author_fk")
    op.execute('ALTER TABLE booking DROP COLUMN IF EXISTS "cancellationAuthorId" ')
    op.execute('ALTER TABLE collective_booking DROP COLUMN IF EXISTS "cancellationAuthorId" ')


def downgrade() -> None:
    pass
