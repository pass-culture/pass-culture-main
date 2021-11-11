"""add_beneficiary_import_eligibility_type
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3908af1a50e5"
down_revision = "5efbe08eff49"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "beneficiary_import", sa.Column("eligibilityType", sa.TEXT(), server_default="age-18", nullable=False)
    )


def downgrade():
    op.drop_column("beneficiary_import", "eligibilityType")
