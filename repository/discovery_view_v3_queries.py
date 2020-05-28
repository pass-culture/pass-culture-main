from sqlalchemy.orm import Session
from sqlalchemy_utils import refresh_materialized_view
from typing import Callable

from models import DiscoveryViewV3
from models.db import db


def _order_by_digital_offers() -> str:
    return f"""
        ROW_NUMBER() OVER (
            ORDER BY
                (
                    SELECT COALESCE(SUM(criterion."scoreDelta"), 0) AS coalesce_1
                    FROM criterion, offer_criterion
                    WHERE criterion.id = offer_criterion."criterionId"
                        AND offer_criterion."offerId" = offer.id
                ) DESC,
                offer.url IS NOT NULL DESC,
                RANDOM()
        )
    """


def create(session: Session, order: Callable = _order_by_digital_offers) -> None:
    _create_discovery_view(session, order, DiscoveryViewV3.__tablename__)
    session.commit()


def refresh(concurrently: bool = True) -> None:
    refresh_materialized_view(db.session, DiscoveryViewV3.__tablename__, concurrently)
    db.session.commit()


def _create_discovery_view(session: Session, order: Callable, name: str) -> None:
    get_recommendable_offers = _create_function_get_recommendable_offers_ordered_by_digital_offers(session, order)
    session.execute(f"""
        CREATE MATERIALIZED VIEW IF NOT EXISTS {name} AS
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
    session.execute(f"""
        CREATE UNIQUE INDEX ON {name} ("offerDiscoveryOrder");
    """)


def _create_function_get_recommendable_offers_ordered_by_digital_offers(session, order: Callable) -> str:
    get_offer_score = _create_function_get_offer_score(session)
    get_active_offers_ids = _create_function_get_active_offers_ids(session)

    session.execute(f"""
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
                (SELECT * FROM {get_offer_score}(offer.id)) AS criterion_score,
                offer.id AS id,
                offer."venueId" AS "venueId",
                offer.type AS type,
                offer.name AS name,
                offer.url AS url,
                offer."isNational" AS "isNational",
                {order()} AS partitioned_offers
            FROM offer
            WHERE offer.id IN (SELECT * FROM {get_active_offers_ids}(TRUE))
            ORDER BY {order()};
        END
        $body$
        LANGUAGE plpgsql;
    """)
    return 'get_recommendable_offers_ordered_by_digital_offers'


def _create_function_offer_has_at_least_one_bookable_stock(session) -> str:
    function_name = 'offer_has_at_least_one_bookable_stock'
    session.execute(f"""
        CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
        RETURNS SETOF INTEGER AS $body$
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
                    OR (
                        SELECT GREATEST(stock.quantity - COALESCE(SUM(booking.quantity), 0), 0)
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


def _create_function_offer_has_at_least_one_active_mediation(session) -> str:
    function_name = 'offer_has_at_least_one_active_mediation'
    session.execute(f"""
        CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
        RETURNS SETOF INTEGER AS $body$
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


def _create_function_event_is_in_less_than_10_days(session) -> str:
    function_name = 'event_is_in_less_than_10_days'
    session.execute(f"""
        CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
        RETURNS SETOF INTEGER AS $body$
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


def _create_function_get_active_offers_ids(session) -> str:
    function_name = 'get_active_offers_ids'
    offer_has_at_least_one_active_mediation = _create_function_offer_has_at_least_one_active_mediation(session)
    offer_has_at_least_one_bookable_stock = _create_function_offer_has_at_least_one_bookable_stock(session)

    session.execute(f"""
        CREATE OR REPLACE FUNCTION {function_name}(with_mediation bool)
        RETURNS SETOF BIGINT AS
        $body$
        BEGIN
            RETURN QUERY
            SELECT DISTINCT ON (offer.id) offer.id
            FROM offer
            JOIN venue ON offer."venueId" = venue.id
            JOIN offerer ON offerer.id = venue."managingOffererId"
            WHERE offer."isActive" = TRUE
                AND venue."validationToken" IS NULL
                AND (
                    NOT with_mediation
                    OR (with_mediation AND EXISTS (SELECT * FROM {offer_has_at_least_one_active_mediation}(offer.id)))
                )
                AND (EXISTS (SELECT * FROM {offer_has_at_least_one_bookable_stock}(offer.id)))
                AND offerer."isActive" = TRUE
                AND offerer."validationToken" IS NULL
                AND offer.type != 'ThingType.ACTIVATION'
                AND offer.type != 'EventType.ACTIVATION';
        END;
        $body$
        LANGUAGE plpgsql;
    """)
    return function_name


def _create_function_get_offer_score(session) -> str:
    function_name = 'get_offer_score'
    session.execute(f"""
        CREATE OR REPLACE FUNCTION {function_name}(offer_id BIGINT)
        RETURNS SETOF BIGINT AS $body$
        BEGIN
            RETURN QUERY
            SELECT COALESCE(SUM(criterion."scoreDelta"), 0)
            FROM criterion, offer_criterion
            WHERE criterion.id = offer_criterion."criterionId"
                AND offer_criterion."offerId" = offer_id;
        END
        $body$
        LANGUAGE plpgsql;
    """)
    return function_name
