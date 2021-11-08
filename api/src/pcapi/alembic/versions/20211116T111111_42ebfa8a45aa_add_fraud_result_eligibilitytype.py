"""add_fraud_result_eligibilityType
"""
from alembic import op
import sqlalchemy as sa

from pcapi.core.users import models as users_models


# revision identifiers, used by Alembic.
revision = "42ebfa8a45aa"
down_revision = "e2ec54a156f2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "beneficiary_fraud_result",
        sa.Column("eligibilityType", sa.TEXT(), server_default=users_models.EligibilityType.AGE18.name, nullable=False),
    )


def downgrade():
    op.drop_column("beneficiary_fraud_result", "eligibilityType")
