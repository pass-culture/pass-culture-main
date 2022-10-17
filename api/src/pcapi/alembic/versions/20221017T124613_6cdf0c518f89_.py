"""add index on beneficiary_fraud_check.thirdPartyId
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6cdf0c518f89"
down_revision = "8ab2b534c85b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_beneficiary_fraud_check_thirdPartyId" ON "beneficiary_fraud_check" ("thirdPartyId")
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index("ix_beneficiary_fraud_check_thirdPartyId", table_name="beneficiary_fraud_check")
