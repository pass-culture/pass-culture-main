"""Venue to BusinessUnit relation
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "194844a36610"
down_revision = "72743d0e21c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("businessUnitId", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "venue", "business_unit", ["businessUnitId"], ["id"])


def downgrade() -> None:
    op.drop_column("venue", "businessUnitId")
