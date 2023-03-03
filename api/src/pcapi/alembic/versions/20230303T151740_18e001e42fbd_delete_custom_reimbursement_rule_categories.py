"""Delete `custom_reimbursement_rule.categories`"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "18e001e42fbd"
down_revision = "27ca16bd3d32"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("custom_reimbursement_rule", "categories")


def downgrade():
    op.add_column(
        "custom_reimbursement_rule",
        sa.Column(
            "categories",
            postgresql.ARRAY(sa.TEXT()),
            server_default=sa.text("'{}'::text[]"),
            autoincrement=False,
            nullable=True,
        ),
    )
