"""drop_is_cancelled_column_from_booking_table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a9cb91d93ea0"
down_revision = "b7a2d1d87495"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("booking", "isCancelled")


def downgrade() -> None:
    op.add_column("booking", sa.Column("isCancelled", sa.BOOLEAN()))
