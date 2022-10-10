"""add_flag_for_collective_offers_from_api
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ac10b3d69c25"
down_revision = "b0f79857ab7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "collective_offer", sa.Column("isPublicApi", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("collective_offer", "isPublicApi")
