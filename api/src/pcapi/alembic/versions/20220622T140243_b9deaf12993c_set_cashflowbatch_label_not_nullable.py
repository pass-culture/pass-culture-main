"""Make cashflow_batch_label not nullable."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b9deaf12993c"
down_revision = "01e4e1b7f714"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("cashflow_batch", "label", existing_type=sa.TEXT(), nullable=False)


def downgrade():
    op.alter_column("cashflow_batch", "label", existing_type=sa.TEXT(), nullable=True)
