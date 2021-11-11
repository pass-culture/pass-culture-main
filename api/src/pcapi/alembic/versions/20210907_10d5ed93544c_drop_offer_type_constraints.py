"""Drop Offer.type constraints"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "10d5ed93544c"
down_revision = "e788c9f3cd3b"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("offer", "type", existing_type=sa.VARCHAR(length=50), nullable=True)
    op.execute("ALTER TABLE offer DROP CONSTRAINT IF EXISTS offer_type_check")


def downgrade():
    pass
