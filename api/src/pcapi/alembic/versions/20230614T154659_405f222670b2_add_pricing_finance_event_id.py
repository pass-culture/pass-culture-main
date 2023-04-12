"""Add `pricing.eventId` column"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "405f222670b2"
down_revision = "c00fce7569d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pricing", sa.Column("eventId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("pricing", "eventId")
