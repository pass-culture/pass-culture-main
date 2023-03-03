"""Make `cashflow.transactionId` nullable (before its deletion)"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "af95cd1b1a41"
down_revision = "1552f6d411e4"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "cashflow",
        "transactionId",
        existing_type=postgresql.UUID(),
        nullable=True,
        existing_server_default=sa.text("gen_random_uuid()"),
    )


def downgrade():
    pass
