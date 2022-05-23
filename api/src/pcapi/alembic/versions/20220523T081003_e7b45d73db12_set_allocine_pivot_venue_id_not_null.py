"""set allocine_pivot venue_id not null
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7b45d73db12"
down_revision = "bdfc48c090db"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("allocine_pivot", "venueId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("allocine_pivot", "venueId", existing_type=sa.BIGINT(), nullable=True)
