"""add_is_active_educational_institution
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "aca83eb30235"
down_revision = "2cd65d427b7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "educational_institution",
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("educational_institution", "isActive")
