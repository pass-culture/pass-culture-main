"""Populate business_unit_venue_link table."""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b63eb1053857"
down_revision = "11f137937ae5"
branch_labels = None
depends_on = None


def upgrade():
    # Create a row in business_unit_venue_link for each venue that is
    # linked to a business unit. The lower bound of the timespan is
    # set to the Epoch to make it clearer that the information is
    # fabricated.
    op.execute(
        """
        INSERT INTO business_unit_venue_link ("venueId", "businessUnitId", timespan)
        SELECT
          venue.id,
          venue."businessUnitId",
          tsrange('1970-01-01', NULL, '[)')
        FROM venue
        LEFT OUTER JOIN
          business_unit_venue_link AS link
          ON link."businessUnitId" = venue."businessUnitId"
          AND link."venueId" = venue.id
        WHERE
          venue."businessUnitId" IS NOT NULL
          AND link.id IS NULL
        """
    )


def downgrade():
    pass
