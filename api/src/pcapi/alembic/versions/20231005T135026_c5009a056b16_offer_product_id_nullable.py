"""Make offer productId nullable"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c5009a056b16"
down_revision = "4205ae20bb32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    op.alter_column("offer", "productId", existing_type=sa.BIGINT(), nullable=False)
