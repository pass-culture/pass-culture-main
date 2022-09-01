"""Create table latest_dms_import
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bfa3eb158af2"
down_revision = "0502f0f2f72c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "latest_dms_import",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("procedureId", sa.Integer(), nullable=False),
        sa.Column("latestImportDatetime", sa.DateTime(), nullable=False),
        sa.Column("isProcessing", sa.Boolean(), nullable=False),
        sa.Column("processedApplications", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("latest_dms_import")
