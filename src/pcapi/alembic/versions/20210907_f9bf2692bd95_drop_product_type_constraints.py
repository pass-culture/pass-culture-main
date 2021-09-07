"""Drop Product.type constraints"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f9bf2692bd95"
down_revision = "10d5ed93544c"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("product", "type", existing_type=sa.VARCHAR(length=50), nullable=True)
    op.execute("ALTER TABLE product DROP CONSTRAINT IF EXISTS product_type_check")


def downgrade():
    pass
