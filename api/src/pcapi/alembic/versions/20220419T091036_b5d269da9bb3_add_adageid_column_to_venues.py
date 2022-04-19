"""add_adageId_column_to_venues
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b5d269da9bb3"
down_revision = "bc19bb0b294f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("adageId", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "adageId")
