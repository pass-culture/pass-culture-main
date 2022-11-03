"""add_is_allowed_for_eac_on_offerer
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3be85d7c89d3"
down_revision = "9ae01271d8c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offerer", sa.Column("isAllowedForEAC", sa.Boolean(), server_default=sa.text("true"), nullable=False))


def downgrade() -> None:
    op.drop_column("offerer", "isAllowedForEAC")
