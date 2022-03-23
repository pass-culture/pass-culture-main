"""add_offer_withdrawal
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f5f77c745513"
down_revision = "f5a5da60e349"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("withdrawalDelay", sa.BigInteger(), nullable=True))
    op.add_column(
        "offer",
        sa.Column("withdrawalType", sa.String(), nullable=True),
    )


def downgrade():
    op.drop_column("offer", "withdrawalType")
    op.drop_column("offer", "withdrawalDelay")
