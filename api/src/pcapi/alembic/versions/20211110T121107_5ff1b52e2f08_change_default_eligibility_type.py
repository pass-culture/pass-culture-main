"""change_default_eligibility_type
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "5ff1b52e2f08"
down_revision = "98a7c44f7ca1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE beneficiary_import ALTER COLUMN "eligibilityType" SET DEFAULT 'AGE18';
        """
    )


def downgrade():
    pass
