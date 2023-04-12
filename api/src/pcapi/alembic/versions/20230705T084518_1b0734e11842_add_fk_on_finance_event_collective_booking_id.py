"""Add foreign key on `finance_event.collectiveBookingId`
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1b0734e11842"
down_revision = "c1bd21cac4e9"
branch_labels = None
depends_on = None


fk_name = "finance_event_collectiveBookingId_fkey"


def upgrade() -> None:
    op.create_foreign_key(fk_name, "finance_event", "collective_booking", ["collectiveBookingId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(fk_name, "finance_event", type_="foreignkey")
