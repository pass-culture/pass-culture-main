"""Add CustomReimbursementRule.subcategories column."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "a5f8cf0d75da"
down_revision = "bf9641a0f5a8"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "custom_reimbursement_rule",
        sa.Column("subcategories", postgresql.ARRAY(sa.Text()), server_default="{}", nullable=True),
    )


def downgrade():
    op.drop_column("custom_reimbursement_rule", "subcategories")
