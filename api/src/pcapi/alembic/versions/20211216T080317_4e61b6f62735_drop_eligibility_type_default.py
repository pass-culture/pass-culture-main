"""drop_eligibility_type_default
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4e61b6f62735"
down_revision = "608d334310cd"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "beneficiary_fraud_result", "eligibilityType", existing_type=sa.TEXT(), server_default=None, nullable=True
    )


def downgrade():
    op.alter_column(
        "beneficiary_fraud_result",
        "eligibilityType",
        existing_type=sa.TEXT(),
        server_default=sa.text("'AGE18'::text"),
        nullable=False,
    )
