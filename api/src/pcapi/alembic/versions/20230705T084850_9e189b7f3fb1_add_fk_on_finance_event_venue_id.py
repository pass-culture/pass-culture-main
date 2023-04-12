"""Add foreign key on `finance_event.venueId`
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9e189b7f3fb1"
down_revision = "1b0734e11842"
branch_labels = None
depends_on = None


fk_name = "finance_event_venueId_fkey"


def upgrade() -> None:
    op.create_foreign_key(fk_name, "finance_event", "venue", ["venueId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(fk_name, "finance_event", type_="foreignkey")
