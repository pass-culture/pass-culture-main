"""Add CashflowBatch.label column."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0c2ef3abdbf8"
down_revision = "ce0fcf03be9a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("cashflow_batch", sa.Column("label", sa.Text(), nullable=True))
    op.create_unique_constraint(None, "cashflow_batch", ["label"])


def downgrade():
    op.drop_column("cashflow_batch", "label")
