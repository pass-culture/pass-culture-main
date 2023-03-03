"""Delete `cashflow.transactionId`"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "27ca16bd3d32"
down_revision = "3634768b063b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("cashflow", "transactionId")


def downgrade():
    op.add_column(
        "cashflow",
        sa.Column(
            "transactionId",
            postgresql.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.create_unique_constraint("cashflow_transactionId_key", "cashflow", ["transactionId"])
