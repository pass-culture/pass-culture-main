"""add hirPartyId_index on beneficiary_import table
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "4584c4d37792"
down_revision = "3be7014806b6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_beneficiary_import_thirdPartyId"
            ON beneficiary_import ("thirdPartyId")
        """
    )


def downgrade():
    op.drop_index(op.f("ix_beneficiary_import_thirdPartyId"), table_name="beneficiary_import")
