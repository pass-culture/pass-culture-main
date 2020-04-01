from sqlalchemy import Column, BigInteger, ForeignKey, String, Integer, Boolean
from sqlalchemy_utils import refresh_materialized_view

from models.db import Model, db


class DiscoveryView(Model):
    __tablename__ = "discovery_view"

    venueId = Column(BigInteger, ForeignKey('venue.id'))

    mediationId = Column(BigInteger, ForeignKey('mediation.id'))

    id = Column(BigInteger, primary_key=True)

    type = Column(String(50))

    url = Column(String(255))

    offerDiscoveryOrder = Column(Integer)

    name = Column(String(140))

    isNational = Column(Boolean)

    @classmethod
    def create(cls, session):
        get_recommendable_offers = cls._create_function_get_recommendable_offers(session)

        session.execute(f"""
            CREATE MATERIALIZED VIEW IF NOT EXISTS {cls.__tablename__}
                AS SELECT
                   row_number() OVER () AS "offerDiscoveryOrder",
                   recommendable_offers.id                           AS id,
                   recommendable_offers."venueId"                    AS "venueId",
                   recommendable_offers.type                         AS type,
                   recommendable_offers.name                         AS name,
                   recommendable_offers.url                          AS url,
                   recommendable_offers."isNational"                 AS "isNational",
                   offer_mediation.id                                AS "mediationId"
                FROM (SELECT * FROM {get_recommendable_offers}()) AS recommendable_offers
                LEFT OUTER JOIN mediation AS offer_mediation ON recommendable_offers.id = offer_mediation."offerId"
                            AND offer_mediation."isActive"
                ORDER BY recommendable_offers.partitioned_offers;
        """)
        session.execute(f"""
            CREATE UNIQUE INDEX ON {cls.__tablename__} ("offerDiscoveryOrder");
        """)
        session.commit()

    @classmethod
    def _create_function_get_recommendable_offers(cls, session):
        function_name = 'get_recommendable_offers'

        get_offer_score = cls._create_function_get_offer_score(session)
        event_is_in_less_than_10_days = cls._create_function_event_is_in_less_than_10_days(session)
        offer_has_at_least_one_active_mediation = cls._create_function_offer_has_at_least_one_active_mediation(session)
        offer_has_at_least_one_bookable_stock = cls._create_function_offer_has_at_least_one_bookable_stock(session)

        session.execute(f"""
            CREATE OR REPLACE FUNCTION {function_name}()
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
                     (SELECT * from {get_offer_score}(offer.id)) AS criterion_score,
                     offer.id AS id,
                     offer."venueId" AS "venueId",
                     offer.type AS type,
                     offer.name AS name,
                     offer.url AS url,
                     offer."isNational" AS "isNational",
                     row_number() OVER (
                       PARTITION BY offer.type, offer.url IS NULL
                       ORDER BY (EXISTS(SELECT * FROM {event_is_in_less_than_10_days}(offer.id))) DESC,
                                (SELECT * FROM {get_offer_score}(offer.id)) DESC,
                                random()
                      ) AS partitioned_offers
               FROM offer
               WHERE offer.id IN (SELECT DISTINCT ON (offer.id) offer.id
                                    FROM offer
                                    JOIN venue ON offer."venueId" = venue.id
                                    JOIN offerer ON offerer.id = venue."managingOffererId"
                                   WHERE offer."isActive" = TRUE
                                     AND venue."validationToken" IS NULL
                                     AND (EXISTS (SELECT * FROM {offer_has_at_least_one_active_mediation}(offer.id)))
                                     AND (EXISTS(SELECT * FROM {offer_has_at_least_one_bookable_stock}(offer.id)))
                                     AND offerer."isActive" = TRUE
                                     AND offerer."validationToken" IS NULL
                                     AND offer.type != 'ThingType.ACTIVATION'
                                     AND offer.type != 'EventType.ACTIVATION'
                                    )
               ORDER BY row_number() OVER ( PARTITION BY offer.type, offer.url IS NULL
                           ORDER BY (EXISTS (SELECT * FROM {event_is_in_less_than_10_days}(offer.id))) DESC,
                                    (SELECT * FROM {get_offer_score}(offer.id)) DESC,
                                    random()
               );
            END
            $body$
            LANGUAGE plpgsql;
        """)
        return function_name

    @staticmethod
    def _create_function_offer_has_at_least_one_bookable_stock(session):
        function_name = 'offer_has_at_least_one_bookable_stock'
        session.execute(f"""
            CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
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
                   AND (stock.quantity IS NULL
                        OR (SELECT greatest(stock.quantity - COALESCE(sum(booking.quantity), 0),0)
                              FROM booking
                             WHERE booking."stockId" = stock.id
                               AND booking."isCancelled" = FALSE
                            ) > 0
                        );
            END
            $body$
            LANGUAGE plpgsql;
        """)
        return function_name

    @staticmethod
    def _create_function_offer_has_at_least_one_active_mediation(session) -> str:
        function_name = 'offer_has_at_least_one_active_mediation'
        session.execute(f"""
            CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
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
        """)
        return function_name

    @staticmethod
    def _create_function_event_is_in_less_than_10_days(session) -> str:
        function_name = 'event_is_in_less_than_10_days'
        session.execute(f"""
            CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
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
        """)
        return function_name

    @staticmethod
    def _create_function_get_offer_score(session) -> str:
        function_name = 'get_offer_score'
        session.execute(f"""
            CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
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
        """)
        return function_name

    @classmethod
    def refresh(cls, concurrently=True):
        refresh_materialized_view(db.session, cls.__tablename__, concurrently)
        db.session.commit()
