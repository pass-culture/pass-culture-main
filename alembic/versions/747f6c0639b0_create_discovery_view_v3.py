"""create_discovery_view_v3
Revision ID: 747f6c0639b0
Revises: 2b44409d9f54
Create Date: 2020-04-02 11:57:27.703029
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '747f6c0639b0'
down_revision = '2b44409d9f54'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS discovery_view_v3 AS
            SELECT
                ROW_NUMBER() OVER ()                AS "offerDiscoveryOrder",
                recommendable_offers.id             AS id,
                recommendable_offers."venueId"      AS "venueId",
                recommendable_offers.type           AS type,
                recommendable_offers.name           AS name,
                recommendable_offers.url            AS url,
                recommendable_offers."isNational"   AS "isNational",
                offer_mediation.id                  AS "mediationId"
            FROM (SELECT * FROM get_recommendable_offers()) AS recommendable_offers
            LEFT OUTER JOIN mediation AS offer_mediation ON recommendable_offers.id = offer_mediation."offerId"
                AND offer_mediation."isActive"
            ORDER BY recommendable_offers.partitioned_offers;

            CREATE UNIQUE INDEX ON discovery_view_v3 ("offerDiscoveryOrder");
    """)


def downgrade():
    op.execute("""
        DROP MATERIALIZED VIEW discovery_view_v3;
    """)
