"""Add booking_status.PENDING_REIMBURSEMENT"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "776f436c2de7"
down_revision = "67dd77c68f20"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE booking_status ADD VALUE IF NOT EXISTS 'PENDING_REIMBURSEMENT';")


def downgrade() -> None:
    pass
