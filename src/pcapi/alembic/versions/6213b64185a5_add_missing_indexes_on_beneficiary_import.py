"""Add missing indexes on beneficiary_import

Revision ID: 6213b64185a5
Revises: 8ab840b8db67
Create Date: 2019-10-25 10:20:38.228124

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "6213b64185a5"
down_revision = "8ab840b8db67"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS "idx_beneficiary_import_status_beneficiaryImportId" ON beneficiary_import_status ("beneficiaryImportId");
        CREATE INDEX IF NOT EXISTS "idx_beneficiary_import_status_authorId" ON beneficiary_import_status ("authorId");
        CREATE INDEX IF NOT EXISTS "idx_beneficiary_import_beneficiaryId" ON beneficiary_import ("beneficiaryId");
        """
    )


def downgrade():
    op.execute(
        """
        DROP INDEX IF EXISTS "idx_beneficiary_import_status_beneficiaryImportId";
        DROP INDEX IF EXISTS "idx_beneficiary_import_status_authorId";
        DROP INDEX IF EXISTS "idx_beneficiary_import_beneficiaryId";
        """
    )
