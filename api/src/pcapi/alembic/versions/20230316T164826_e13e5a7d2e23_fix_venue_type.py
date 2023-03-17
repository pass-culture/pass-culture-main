"""fix-venue-type
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e13e5a7d2e23"
down_revision = "ed5d909b3525"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """update venue set "venueTypeCode" = 'DIGITAL' where "isVirtual"=True and "venueTypeCode" <> 'DIGITAL'"""
    )


def downgrade() -> None:
    pass
