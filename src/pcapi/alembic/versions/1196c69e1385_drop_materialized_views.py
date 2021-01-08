"""drop_materialized_views

Revision ID: 1196c69e1385
Revises: 692f4bd89a83
Create Date: 2021-01-08 11:04:14.731846

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "1196c69e1385"
down_revision = "692f4bd89a83"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP MATERIALIZED VIEW discovery_view")
    op.execute("DROP MATERIALIZED VIEW discovery_view_v3")

    op.execute("DROP FUNCTION IF EXISTS get_recommendable_offers;")
    op.execute("DROP FUNCTION IF EXISTS get_recommendable_offers_ordered;")
    op.execute("DROP FUNCTION IF EXISTS get_recommendable_offers_ordered_by_digital_offers;")


def downgrade():
    op.execute(
        """
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
        """
    )

    op.execute(
        """
                CREATE OR REPLACE FUNCTION get_recommendable_offers()
                RETURNS TABLE (
                    criterion_score BIGINT,
                    id BIGINT,
                    "venueId" BIGINT,
                    type VARCHAR,
                    name VARCHAR,
                    url VARCHAR,
                    "isNational" BOOLEAN,
                    partitioned_offers BIGINT
                    ) AS
                $body$
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
                         row_number() OVER (
                           PARTITION BY offer.type, offer.url IS NULL
                           ORDER BY (EXISTS(SELECT * FROM event_is_in_less_than_10_days(offer.id))) DESC,
                                    (SELECT * FROM get_offer_score(offer.id)) DESC,
                                    random()
                          ) AS partitioned_offers
                   FROM offer
                   WHERE offer.id IN (SELECT DISTINCT ON (offer.id) offer.id
                                        FROM offer
                                        JOIN venue ON offer."venueId" = venue.id
                                        JOIN offerer ON offerer.id = venue."managingOffererId"
                                       WHERE offer."isActive" = TRUE
                                         AND venue."validationToken" IS NULL
                                         AND (EXISTS (SELECT * FROM offer_has_at_least_one_active_mediation(offer.id)))
                                         AND (EXISTS(SELECT * FROM offer_has_at_least_one_bookable_stock(offer.id)))
                                         AND offerer."isActive" = TRUE
                                         AND offerer."validationToken" IS NULL
                                         AND offer.type != 'ThingType.ACTIVATION'
                                         AND offer.type != 'EventType.ACTIVATION'
                                        )
                   ORDER BY row_number() OVER ( PARTITION BY offer.type, offer.url IS NULL
                               ORDER BY (EXISTS (SELECT * FROM event_is_in_less_than_10_days(offer.id))) DESC,
                                        (SELECT * FROM get_offer_score(offer.id)) DESC,
                                        random()
                   );
                END
                $body$
                LANGUAGE plpgsql;
            """
    )

    op.execute(
        """
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
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ON discovery_view ("offerDiscoveryOrder");
        COMMIT;
        """
    )

    op.execute(
        """
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
        """
    )

    op.create_index(op.f("idx_discovery_view_offerId"), "discovery_view", ["id"], postgresql_concurrently=True)
    op.create_index(op.f("idx_discovery_view_v3_offerId"), "discovery_view_v3", ["id"], postgresql_concurrently=True)
