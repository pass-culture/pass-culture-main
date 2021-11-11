"""Add Deposit.dateUpdated column."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "98a7c44f7ca1"
down_revision = "49f58959dbd4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("deposit", sa.Column("dateUpdated", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("deposit", "dateUpdated")
