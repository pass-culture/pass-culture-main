"""add_discovery_view

Revision ID: 2ab67d07fe52
Revises: 6b76c225cc26
Create Date: 2020-01-17 14:29:25.391443

"""
from alembic import op


# revision identifiers, used by Alembic.

revision = "2ab67d07fe52"
down_revision = "6b76c225cc26"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        f"""
                CREATE OR REPLACE FUNCTION get_offer_score(offer_id BIGINT)
                RETURNS SETOF BIGINT AS
                $body$
                BEGIN
                   RETURN QUERY
                   SELECT coalesce(sum(criterion."scoreDelta"), 0)
                    FROM criterion, offer_criterion
                   WHERE criterion.id = offer_criterion."criterionId"
                     AND offer_criterion."offerId" = offer_id;
                END
                $body$
                LANGUAGE plpgsql;
            """
    )

    op.execute(
        f"""
                CREATE OR REPLACE FUNCTION event_is_in_less_than_10_days(offer_id BIGINT)
                RETURNS SETOF INTEGER AS
                $body$
                BEGIN
                   RETURN QUERY
                   SELECT 1
                    FROM stock
                    WHERE stock."offerId" = offer_id
                      AND (stock."beginningDatetime" IS NULL
                            OR stock."beginningDatetime" > NOW()
                           AND stock."beginningDatetime" < NOW() + INTERVAL '10 DAY');
                END
                $body$
                LANGUAGE plpgsql;
            """
    )

    op.execute(
        """
                CREATE OR REPLACE FUNCTION offer_has_at_least_one_active_mediation(offer_id BIGINT)
                RETURNS SETOF INTEGER AS
                $body$
                BEGIN
                   RETURN QUERY
                   SELECT 1
                       FROM mediation
                      WHERE mediation."offerId" = offer_id
                        AND mediation."isActive";
                END
                $body$
                LANGUAGE plpgsql;
            """
    )
    op.execute(
        """
                CREATE OR REPLACE FUNCTION offer_has_at_least_one_bookable_stock(offer_id BIGINT)
                RETURNS SETOF INTEGER AS
                $body$
                BEGIN
                   RETURN QUERY
                   SELECT 1
                      FROM stock
                     WHERE stock."offerId" = offer_id
                       AND stock."isSoftDeleted" = FALSE
                       AND (stock."beginningDatetime" > NOW()
                            OR stock."beginningDatetime" IS NULL)
                       AND (stock."bookingLimitDatetime" > NOW() 
                            OR stock."bookingLimitDatetime" IS NULL)
                       AND (stock.available IS NULL
                            OR (SELECT greatest(stock.available - COALESCE(sum(booking.quantity), 0),0)
                                  FROM booking
                                 WHERE booking."stockId" = stock.id
                                   AND (booking."isUsed" = FALSE
                                         AND booking."isCancelled" = FALSE
                                          OR booking."isUsed" = TRUE
                                         AND booking."dateUsed" > stock."dateModified")
                                ) > 0
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
        f"""
            CREATE MATERIALIZED VIEW IF NOT EXISTS discovery_view
                AS SELECT
                   row_number() OVER () AS "offerDiscoveryOrder",
                   recommendable_offers.id                           AS id,
                   recommendable_offers."venueId"                    AS "venueId",
                   recommendable_offers.type                         AS type,
                   recommendable_offers.name                         AS name,
                   recommendable_offers.url                          AS url,
                   recommendable_offers."isNational"                 AS "isNational",
                   offer_mediation.id                                AS "mediationId"
                FROM (SELECT * FROM get_recommendable_offers()) AS recommendable_offers
                LEFT OUTER JOIN mediation AS offer_mediation ON recommendable_offers.id = offer_mediation."offerId"
                            AND offer_mediation."isActive"
                ORDER BY recommendable_offers.partitioned_offers;
        """
    )

    op.execute(
        f""" CREATE UNIQUE INDEX IF NOT EXISTS "discovery_view_offerDiscoveryOrder_idx" ON discovery_view ("offerDiscoveryOrder"); """
    )


def downgrade():
    op.execute(
        f"""
        DROP MATERIALIZED VIEW discovery_view;
        DROP FUNCTION get_offer_score;
        DROP FUNCTION event_is_in_less_than_10_days;
        DROP FUNCTION offer_has_at_least_one_bookable_stock;
        DROP FUNCTION offer_has_at_least_one_active_mediation;
        DROP FUNCTION get_recommendable_offers;
    """
    )
