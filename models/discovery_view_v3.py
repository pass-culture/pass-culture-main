from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy_utils import refresh_materialized_view

from models import DiscoveryView
from models.db import Model, db


class DiscoveryViewV3(Model):
    __tablename__ = 'discovery_view_v3'

    venueId = Column(BigInteger, ForeignKey('venue.id'))

    mediationId = Column(BigInteger, ForeignKey('mediation.id'))

    id = Column(BigInteger, primary_key=True)

    type = Column(String(50))

    url = Column(String(255))

    offerDiscoveryOrder = Column(Integer)

    name = Column(String(140))

    isNational = Column(Boolean)

    def __init__(self, session: scoped_session):
        self.session = session
        self.discovery_view = DiscoveryView(session)

    def create(self) -> None:
        get_recommendable_offers = self._create_function_get_recommendable_offers()

        self.session.execute(f"""
            CREATE MATERIALIZED VIEW IF NOT EXISTS {self.__tablename__} AS
                SELECT
                    ROW_NUMBER() OVER ()                AS "offerDiscoveryOrder",
                    recommendable_offers.id             AS id,
                    recommendable_offers."venueId"      AS "venueId",
                    recommendable_offers.type           AS type,
                    recommendable_offers.name           AS name,
                    recommendable_offers.url            AS url,
                    recommendable_offers."isNational"   AS "isNational",
                    offer_mediation.id                  AS "mediationId"
                FROM (SELECT * FROM {get_recommendable_offers}()) AS recommendable_offers
                LEFT OUTER JOIN mediation AS offer_mediation ON recommendable_offers.id = offer_mediation."offerId"
                    AND offer_mediation."isActive"
                ORDER BY recommendable_offers.partitioned_offers;
        """)
        self.session.execute(f"""
            CREATE UNIQUE INDEX ON {self.__tablename__} ("offerDiscoveryOrder");
        """)
        self.session.commit()

    def _create_function_get_recommendable_offers(self) -> str:
        function_name = 'get_recommendable_offers'

        get_offer_score = self._create_function_get_offer_score()
        offer_has_at_least_one_active_mediation = self._create_function_offer_has_at_least_one_active_mediation()
        offer_has_at_least_one_bookable_stock = self._create_function_offer_has_at_least_one_bookable_stock()

        self.session.execute(f"""
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
            ) AS $body$
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
                    {self._order_by_digital_offers()} AS partitioned_offers
                FROM offer
                WHERE offer.id IN (
                    SELECT DISTINCT ON (offer.id) offer.id
                    FROM offer
                    JOIN venue ON offer."venueId" = venue.id
                    JOIN offerer ON offerer.id = venue."managingOffererId"
                    WHERE offer."isActive" = TRUE
                        AND venue."validationToken" IS NULL
                        AND (EXISTS (SELECT * FROM {offer_has_at_least_one_active_mediation}(offer.id)))
                        AND (EXISTS (SELECT * FROM {offer_has_at_least_one_bookable_stock}(offer.id)))
                        AND offerer."isActive" = TRUE
                        AND offerer."validationToken" IS NULL
                        AND offer.type != 'ThingType.ACTIVATION'
                        AND offer.type != 'EventType.ACTIVATION'
                )
                ORDER BY {self._order_by_digital_offers()};
            END
            $body$
            LANGUAGE plpgsql;
        """)
        return function_name

    def _order_by_digital_offers(self) -> str:
        get_offer_score = self._create_function_get_offer_score()
        event_is_in_less_than_10_days = self._create_function_event_is_in_less_than_10_days()

        return f"""
            ROW_NUMBER() OVER (
                PARTITION BY offer.type, offer.url IS NULL
                ORDER BY
                    (EXISTS (SELECT * FROM {event_is_in_less_than_10_days}(offer.id))) DESC,
                    (SELECT * FROM {get_offer_score}(offer.id)) DESC,
                    RANDOM()
            )
        """

    def _create_function_offer_has_at_least_one_bookable_stock(self) -> str:
        return self.discovery_view._create_function_offer_has_at_least_one_bookable_stock()

    def _create_function_offer_has_at_least_one_active_mediation(self) -> str:
        return self.discovery_view._create_function_offer_has_at_least_one_active_mediation()

    def _create_function_event_is_in_less_than_10_days(self) -> str:
        return self.discovery_view._create_function_event_is_in_less_than_10_days()

    def _create_function_get_offer_score(self) -> str:
        return self.discovery_view._create_function_get_offer_score()

    @classmethod
    def refresh(cls, concurrently: bool = True) -> None:
        refresh_materialized_view(db.session, cls.__tablename__, concurrently)
        db.session.commit()
