"""
Change banId column from String to Text
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "faed981725fd"
down_revision = "562ae6d8be2f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("venue", "banId")
    op.add_column("venue", sa.Column("banId", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "banId")
    op.add_column("venue", sa.Column("banId", sa.String(20), nullable=True))
