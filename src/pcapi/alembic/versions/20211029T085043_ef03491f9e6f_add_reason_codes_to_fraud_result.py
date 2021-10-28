"""add_reason_codes_to_fraud_result
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ef03491f9e6f"
down_revision = "9e5ae228e4ab"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "beneficiary_fraud_result",
        sa.Column(
            "reason_codes",
            sa.ARRAY(sa.TEXT()),
            server_default="{}",
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("beneficiary_fraud_result", "reason_codes")
