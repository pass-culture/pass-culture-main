"""Add index on Cashflow.batchId"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "5223415d2eb7"
down_revision = "fa5a3135848e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f("ix_cashflow_batchId"), "cashflow", ["batchId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_cashflow_batchId"), table_name="cashflow")
