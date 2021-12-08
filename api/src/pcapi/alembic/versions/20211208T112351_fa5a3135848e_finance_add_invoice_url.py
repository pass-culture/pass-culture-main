"""Add Invoice.url column"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fa5a3135848e"
down_revision = "3b2ea23b8cf0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("invoice", sa.Column("url", sa.Text(), nullable=False))
    op.create_unique_constraint(None, "invoice", ["url"])


def downgrade():
    op.drop_column("invoice", "url")
