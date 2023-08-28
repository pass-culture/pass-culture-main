"""
change venueIdAtOfferProvider column for venue_provider table from dummyIdAtProvider to null
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ac3a0966b6c7"
down_revision = "0801acf4c79d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE venue_provider
        SET "venueIdAtOfferProvider" = NULL
        WHERE "venueIdAtOfferProvider" = 'dummyIdAtProvider';
    """
    )


def downgrade() -> None:
    pass
