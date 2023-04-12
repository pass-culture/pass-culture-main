"""Add foreign key on `finance_event.bookingId`
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c1bd21cac4e9"
down_revision = "9801fe92e7af"
branch_labels = None
depends_on = None


fk_name = "finance_event_bookingId_fkey"


def upgrade() -> None:
    op.create_foreign_key(fk_name, "finance_event", "booking", ["bookingId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(fk_name, "finance_event", type_="foreignkey")
