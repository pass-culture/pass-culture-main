"""
add timespan on headline_offer table
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f0b5bf6e0d3f"
down_revision = "b9b007fd9c03"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('ALTER TABLE headline_offer ADD COLUMN IF NOT EXISTS "timespan" TSRANGE')
    op.execute('UPDATE headline_offer SET "timespan" = tsrange(now()::timestamp, NULL) WHERE "timespan" IS NULL')

    # 'ADD CONSTRAINT IF EXIST' is not possible in postgresql, thus the two following commands
    op.execute(
        """
        ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_offer_timespan;
        ALTER TABLE headline_offer ADD CONSTRAINT exclude_offer_timespan EXCLUDE USING gist ("offerId" WITH =, timespan WITH &&);
        """
    )

    op.execute(
        """
        ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_venue_timespan;
        ALTER TABLE headline_offer ADD CONSTRAINT exclude_venue_timespan EXCLUDE USING gist ("venueId" WITH =, timespan WITH &&);
        """
    )


def downgrade() -> None:
    op.execute('ALTER TABLE headline_offer DROP COLUMN IF EXISTS "timespan"')
    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_offer_timespan")
    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_venue_timespan")
