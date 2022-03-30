"""Alter hasSeenProRgs Column of User table to not null defaulting to False.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "61006d347cb2"
down_revision = "6ee927d299b1"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "user", "hasSeenProRgs", existing_type=sa.BOOLEAN(), server_default=sa.text("false"), nullable=False
    )


def downgrade():
    op.alter_column("user", "hasSeenProRgs", existing_type=sa.BOOLEAN(), server_default=None, nullable=True)
