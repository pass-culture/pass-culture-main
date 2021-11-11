"""add_third_party_id_column_to_beneficiary_import
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3be7014806b6"
down_revision = "ef03491f9e6f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("beneficiary_import", sa.Column("thirdPartyId", sa.TEXT(), nullable=True))
    op.alter_column("beneficiary_import", "applicationId", existing_type=sa.BIGINT(), nullable=True)
    op.drop_index("idx_beneficiary_import_application", table_name="beneficiary_import")


def downgrade():
    op.create_index(
        "idx_beneficiary_import_application", "beneficiary_import", ["applicationId", "sourceId", "source"], unique=True
    )
    op.alter_column("beneficiary_import", "applicationId", existing_type=sa.BIGINT(), nullable=False)
    op.drop_column("beneficiary_import", "thirdPartyId")
