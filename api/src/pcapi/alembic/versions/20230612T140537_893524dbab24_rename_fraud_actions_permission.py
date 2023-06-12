"""Rename 'FRAUD_ACTIONS' to 'PRO_FRAUD_ACTIONS'
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "893524dbab24"
down_revision = "17adb47d509c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE permission SET name = 'PRO_FRAUD_ACTIONS' WHERE name = 'FRAUD_ACTIONS'")


def downgrade() -> None:
    op.execute("UPDATE permission SET name = 'FRAUD_ACTIONS' WHERE name = 'PRO_FRAUD_ACTIONS'")
