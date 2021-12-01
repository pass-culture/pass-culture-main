"""add_user_school_type
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1ab309876ab0"
down_revision = "3cb2b2fb88d3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column("schoolType", sa.TEXT(), nullable=True),
    )


def downgrade():
    op.drop_column("user", "schoolType")
