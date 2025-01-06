"""
add timespan on headline_offer table
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4c3be4ff5274"
down_revision = "4c53718279e7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('ALTER TABLE headline_offer DROP COLUMN IF EXISTS "dateUpdated"')
    op.execute('ALTER TABLE headline_offer DROP COLUMN IF EXISTS "dateCreated"')

    op.execute('ALTER TABLE headline_offer ADD COLUMN IF NOT EXISTS "timespan" TSRANGE')
    op.execute('UPDATE headline_offer SET "timespan" = tsrange(NULL, NULL) WHERE "timespan" IS NULL')
    op.execute('ALTER TABLE headline_offer ALTER COLUMN "timespan" SET NOT NULL')

    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_offer_timespan")
    op.execute(
        'ALTER TABLE headline_offer ADD CONSTRAINT exclude_offer_timespan EXCLUDE USING gist ("offerId" WITH =, timespan WITH &&)'
    )

    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_venue_timespan")
    op.execute(
        'ALTER TABLE headline_offer ADD CONSTRAINT exclude_venue_timespan EXCLUDE USING gist ("venueId" WITH =, timespan WITH &&)'
    )


def downgrade() -> None:
    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_offer_timespan")
    op.execute("ALTER TABLE headline_offer DROP CONSTRAINT IF EXISTS exclude_venue_timespan")
    op.execute('ALTER TABLE headline_offer DROP COLUMN IF EXISTS "timespan"')
    op.execute(
        'ALTER TABLE headline_offer ADD COLUMN IF NOT EXISTS "dateCreated" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()'
    )
    op.execute(
        'ALTER TABLE headline_offer ADD COLUMN IF NOT EXISTS "dateUpdated" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()'
    )
