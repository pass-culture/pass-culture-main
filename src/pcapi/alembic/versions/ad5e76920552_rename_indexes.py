"""Rename indexes

Revision ID: ad5e76920552
Revises: df15599370fd
Create Date: 2020-12-04 09:30:19.933353

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ad5e76920552"
down_revision = "df15599370fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
ALTER INDEX "idx_api_key_offererId" RENAME TO "ix_api_key_offererId";
ALTER INDEX "idx_api_key_value" RENAME TO "ix_api_key_value";
ALTER INDEX "idx_bank_information_applicationId" RENAME TO "ix_bank_information_applicationId";
ALTER INDEX "ix_status" RENAME TO "ix_email_status";
    """
    )


def downgrade() -> None:
    op.execute(
        """
ALTER INDEX "ix_email_status" RENAME TO "ix_status";
ALTER INDEX "ix_bank_information_applicationId" RENAME TO "idx_bank_information_applicationId";
ALTER INDEX "ix_api_key_value" RENAME TO "idx_api_key_value";
ALTER INDEX "ix_api_key_offererId" RENAME TO "idx_api_key_offererId";
    """
    )
