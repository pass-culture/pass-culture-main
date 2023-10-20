"""Add preferences to backoffice_user_profile table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "45372e34d18c"
down_revision = "9470268ecb94"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "backoffice_user_profile",
        sa.Column("preferences", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("backoffice_user_profile", "preferences")
