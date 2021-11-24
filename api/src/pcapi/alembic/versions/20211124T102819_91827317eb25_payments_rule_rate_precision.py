"""Change precision of `CustomReimbursementRule.rate`."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "91827317eb25"
down_revision = "22d472b6e867"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "custom_reimbursement_rule",
        "rate",
        type_=sa.Numeric(5, 4),
    )


def downgrade():
    op.alter_column(
        "custom_reimbursement_rule",
        "rate",
        type_=sa.Numeric(3, 2),
    )
