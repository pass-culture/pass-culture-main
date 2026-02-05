"""Add CollectiveBookingStatus.PENDING_REIMBURSEMENT"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "055f840f1976"
down_revision = "776f436c2de7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE bookingstatus ADD VALUE IF NOT EXISTS 'PENDING_REIMBURSEMENT';")


def downgrade() -> None:
    pass
