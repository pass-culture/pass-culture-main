"""Add venue_registration table"""
from alembic import op
import sqlalchemy as sa

from pcapi.core.offerers.models import Target
import pcapi.utils.db as db_utils


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b1ee65265887"
down_revision = "0e0fe7986d01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "venue_registration",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("target", db_utils.MagicEnum(Target), nullable=False),
        sa.Column("webPresence", sa.Text(), nullable=True),
    )
    # new table is empty, unique constraint is created instantly
    op.create_index(op.f("ix_venue_registration_venueId"), "venue_registration", ["venueId"], unique=True)


def downgrade() -> None:
    op.drop_table("venue_registration")
