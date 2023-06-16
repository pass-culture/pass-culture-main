"""Make venue_provider venueIdAtOfferProvider column nullable"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e84fda00f67c"
down_revision = "ad2884071862"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("venue_provider", "venueIdAtOfferProvider", existing_type=sa.VARCHAR(length=70), nullable=True)


def downgrade() -> None:
    # Do not restore NOT NULL constraint.
    pass
