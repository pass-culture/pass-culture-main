"""beneficiary_import_new_columns

Revision ID: 8df159da2826
Revises: 93925a2b551f
Create Date: 2020-06-12 15:00:34.491962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8df159da2826"
down_revision = "93925a2b551f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("beneficiary_import", sa.Column("applicationId", sa.BigInteger, nullable=True))
    op.add_column("beneficiary_import", sa.Column("sourceId", sa.Integer, nullable=True))
    op.add_column("beneficiary_import", sa.Column("source", sa.String(255), nullable=True))

    op.create_index(
        op.f("idx_beneficiary_import_application"), "beneficiary_import", ["applicationId", "sourceId", "source"]
    )


def downgrade():
    op.drop_index("idx_beneficiary_import_application", table_name="beneficiary_import")

    op.drop_column("beneficiary_import", "applicationId")
    op.drop_column("beneficiary_import", "sourceId")
    op.drop_column("beneficiary_import", "source")
