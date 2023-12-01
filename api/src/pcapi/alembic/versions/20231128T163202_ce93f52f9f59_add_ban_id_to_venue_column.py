"""
Adds banId column in Venue table (unique address id in national address DB)
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ce93f52f9f59"
down_revision = "d42246a7f9ba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("banId", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "banId")
