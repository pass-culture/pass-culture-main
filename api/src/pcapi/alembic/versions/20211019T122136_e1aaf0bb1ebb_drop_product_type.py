"""drop_product_type
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e1aaf0bb1ebb"
down_revision = "7a18546db0d5"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("product", "type")


def downgrade():
    op.add_column("product", sa.Column("type", sa.VARCHAR(length=50), autoincrement=False, nullable=True))
