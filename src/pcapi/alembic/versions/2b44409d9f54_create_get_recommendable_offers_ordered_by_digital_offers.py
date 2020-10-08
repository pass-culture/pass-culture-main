"""create_get_recommendable_offers_ordered_by_digital_offers

Revision ID: 2b44409d9f54
Revises: da973e646e06
Create Date: 2020-04-02 11:47:27.703029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b44409d9f54'
down_revision = 'da973e646e06'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE OR REPLACE FUNCTION get_recommendable_offers_ordered_by_digital_offers()
        RETURNS TABLE (
            criterion_score BIGINT,
            id BIGINT,
            "venueId" BIGINT,
            type VARCHAR,
            name VARCHAR,
            url VARCHAR,
            "isNational" BOOLEAN,
            partitioned_offers BIGINT
        ) AS $body$
        BEGIN
            RETURN QUERY
            SELECT
                (SELECT * FROM get_offer_score(offer.id)) AS criterion_score,
                offer.id AS id,
                offer."venueId" AS "venueId",
                offer.type AS type,
                offer.name AS name,
                offer.url AS url,
                offer."isNational" AS "isNational",
                ROW_NUMBER() OVER (
                    ORDER BY
                        offer.url IS NOT NULL DESC,
                        (EXISTS (SELECT 1 FROM stock WHERE stock."offerId" = offer.id AND stock."beginningDatetime" > '2020-04-25T00:00:00'::TIMESTAMP)) DESC,
                        (
                            SELECT COALESCE(SUM(criterion."scoreDelta"), 0) AS coalesce_1
                            FROM criterion, offer_criterion
                            WHERE criterion.id = offer_criterion."criterionId"
                                AND offer_criterion."offerId" = offer.id
                        ) DESC,
                        RANDOM()
                ) AS partitioned_offers
            FROM offer
            WHERE offer.id IN (
                SELECT DISTINCT ON (offer.id) offer.id
                FROM offer
                JOIN venue ON offer."venueId" = venue.id
                JOIN offerer ON offerer.id = venue."managingOffererId"
                WHERE offer."isActive" = TRUE
                    AND venue."validationToken" IS NULL
                    AND (EXISTS (SELECT * FROM offer_has_at_least_one_active_mediation(offer.id)))
                    AND (EXISTS (SELECT * FROM offer_has_at_least_one_bookable_stock(offer.id)))
                    AND offerer."isActive" = TRUE
                    AND offerer."validationToken" IS NULL
                    AND offer.type != 'ThingType.ACTIVATION'
                    AND offer.type != 'EventType.ACTIVATION'
            )
            ORDER BY ROW_NUMBER() OVER (
                ORDER BY
                    offer.url IS NOT NULL DESC,
                    (EXISTS (SELECT 1 FROM stock WHERE stock."offerId" = offer.id AND stock."beginningDatetime" > '2020-04-25T00:00:00'::TIMESTAMP)) DESC,
                    (
                        SELECT COALESCE(SUM(criterion."scoreDelta"), 0) AS coalesce_1
                        FROM criterion, offer_criterion
                        WHERE criterion.id = offer_criterion."criterionId"
                            AND offer_criterion."offerId" = offer.id
                    ) DESC,
                    RANDOM()
            );
        END
        $body$
        LANGUAGE plpgsql;
    """)
    op.execute("""
        DROP MATERIALIZED VIEW discovery_view;
    """)
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS discovery_view AS
            SELECT
                ROW_NUMBER() OVER ()                AS "offerDiscoveryOrder",
                recommendable_offers.id             AS id,
                recommendable_offers."venueId"      AS "venueId",
                recommendable_offers.type           AS type,
                recommendable_offers.name           AS name,
                recommendable_offers.url            AS url,
                recommendable_offers."isNational"   AS "isNational",
                offer_mediation.id                  AS "mediationId"
            FROM (SELECT * FROM get_recommendable_offers_ordered_by_digital_offers()) AS recommendable_offers
            LEFT OUTER JOIN mediation AS offer_mediation ON recommendable_offers.id = offer_mediation."offerId"
                AND offer_mediation."isActive"
            ORDER BY recommendable_offers.partitioned_offers;
    """)
    op.execute("""
        CREATE UNIQUE INDEX ON discovery_view ("offerDiscoveryOrder");
        COMMIT;
    """)


def downgrade():
    op.execute("""
        DROP MATERIALIZED VIEW discovery_view;
    """)
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS discovery_view AS
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
    """)
    op.execute("""
        CREATE UNIQUE INDEX ON discovery_view ("offerDiscoveryOrder");
        COMMIT;
    """)
    op.execute("""
        DROP FUNCTION get_recommendable_offers_ordered_by_digital_offers;
    """)
