"""Add foreign key on `pricing.eventId`
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9801fe92e7af"
down_revision = "95c24b48212e"
branch_labels = None
depends_on = None


fk_name = "pricing_eventId_fkey"


def upgrade() -> None:
    op.create_foreign_key(fk_name, "pricing", "finance_event", ["eventId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(fk_name, "pricing", type_="foreignkey")
