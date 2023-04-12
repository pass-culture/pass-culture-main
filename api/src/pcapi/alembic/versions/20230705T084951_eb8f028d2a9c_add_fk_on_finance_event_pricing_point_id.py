"""Add foreign key on `finance_event.pricingPointId`
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "eb8f028d2a9c"
down_revision = "9e189b7f3fb1"
branch_labels = None
depends_on = None


fk_name = "finance_event_pricingPointId_fkey"


def upgrade() -> None:
    op.create_foreign_key(fk_name, "finance_event", "venue", ["pricingPointId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(fk_name, "finance_event", type_="foreignkey")
