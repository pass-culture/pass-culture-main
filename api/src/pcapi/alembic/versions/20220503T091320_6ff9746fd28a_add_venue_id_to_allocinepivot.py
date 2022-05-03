"""add venue_id to allocine_pivot
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6ff9746fd28a"
down_revision = "0c2ef3abdbf8"
branch_labels = None
depends_on = None

FORIGN_KEY_CONSTRAINT_NAME = "allocine_pivot_venueId_fkey"


def upgrade() -> None:
    op.add_column("allocine_pivot", sa.Column("venueId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(FORIGN_KEY_CONSTRAINT_NAME, "allocine_pivot", "venue", ["venueId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(FORIGN_KEY_CONSTRAINT_NAME, "allocine_pivot", type_="foreignkey")
    op.drop_column("allocine_pivot", "venueId")
