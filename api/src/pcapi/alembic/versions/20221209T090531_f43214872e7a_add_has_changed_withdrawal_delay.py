"""add_has_changed_withdrawal_delay
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f43214872e7a"
down_revision = "2cd65d427b7d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("hasChangedWithdrawalDelay", sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column("offer", "hasChangedWithdrawalDelay")
