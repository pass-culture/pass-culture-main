from typing import Callable, List, Tuple

import pandas
from sqlalchemy import text
from sqlalchemy.sql import selectable

import pcapi.core.bookings.repository as booking_repository
from pcapi.models import Offerer, UserOfferer, VenueSQLEntity, Offer, StockSQLEntity, Booking, EventType, ThingType, UserSQLEntity, DiscoveryView
from pcapi.models.db import db
from pcapi.core.bookings.repository import count_cancelled as query_count_all_cancelled_bookings
from pcapi.core.bookings.repository import _query_keep_only_used_and_non_cancelled_bookings_on_non_activation_offers
from pcapi.repository.offer_queries import get_active_offers_ids_query, _filter_recommendable_offers_for_search, \
    keep_only_offers_in_venues_or_national
from pcapi.repository.offerer_queries import count_offerer, count_offerer_with_stock, count_offerer_by_departement, \
    count_offerer_with_stock_by_departement


def get_offerer_count(departement_code: str = None) -> int:
    return count_offerer_by_departement(departement_code) if departement_code else count_offerer()


def get_offerer_with_stock_count(departement_code: str = None) -> int:
    return count_offerer_with_stock_by_departement(departement_code) if departement_code else count_offerer_with_stock()


def get_offerers_with_offer_available_on_discovery_count(departement_code: str = None) -> int:
    active_offers_ids = get_active_offers_ids_query(user=None)
    query = Offerer.query\
        .join(VenueSQLEntity)\
        .join(Offer)\
        .filter(Offer.id.in_(active_offers_ids))

    if departement_code:
        query = query \
            .filter(VenueSQLEntity.departementCode == departement_code)

    return query \
        .distinct(Offerer.id) \
        .count()


def get_offerers_with_offer_available_on_discovery_count_v2(departement_code: str = None) -> int:
    discovery_view_query = DiscoveryView.query

    if departement_code:
        venues_ids = _get_physical_venue_ids_for_departement(departement_code)
    else:
        venues_ids = _get_all_physical_venue_ids()

    discovery_view_query = keep_only_offers_in_venues_or_national(discovery_view_query, venues_ids) \
        .with_entities(DiscoveryView.venueId)\
        .subquery()


    return VenueSQLEntity.query\
        .filter(VenueSQLEntity.id.in_(discovery_view_query))\
        .distinct(VenueSQLEntity.managingOffererId)\
        .count()


def _get_all_physical_venue_ids() -> selectable.Alias:
    return VenueSQLEntity.query \
        .filter(VenueSQLEntity.departementCode.isnot(None)) \
        .with_entities(VenueSQLEntity.id) \
        .subquery()


def _get_physical_venue_ids_for_departement(departement_code: str) -> selectable.Alias:
    return VenueSQLEntity.query \
        .filter_by(departementCode=departement_code) \
        .with_entities(VenueSQLEntity.id) \
        .subquery()


def get_offerers_with_offers_available_on_search_count(departement_code: str = None) -> int:
    base_query = Offerer.query.join(VenueSQLEntity).join(Offer)
    query = _filter_recommendable_offers_for_search(base_query)
    query = query.distinct(Offerer.id)

    if departement_code:
        query = query.filter(VenueSQLEntity.departementCode == departement_code)

    return query.count()


def get_offerers_with_non_cancelled_bookings_count(departement_code: str = None) -> int:
    query = Offerer.query.join(VenueSQLEntity)

    if departement_code:
        query = query.filter(VenueSQLEntity.departementCode == departement_code)

    return query \
        .join(Offer) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .filter(Offer.type != str(EventType.ACTIVATION)) \
        .join(StockSQLEntity) \
        .join(Booking) \
        .filter_by(isCancelled=False) \
        .distinct(Offerer.id) \
        .count()


def get_offers_with_user_offerer_and_stock_count(departement_code: str = None) -> int:
    query = Offer.query.join(VenueSQLEntity)

    if departement_code:
        query = query.filter(VenueSQLEntity.departementCode == departement_code)

    return query \
        .join(Offerer) \
        .join(UserOfferer) \
        .join(StockSQLEntity, StockSQLEntity.offerId == Offer.id) \
        .filter(Offer.type != str(EventType.ACTIVATION)) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .distinct(Offer.id) \
        .count()


def get_offers_available_on_discovery_count(departement_code: str = None) -> int:
    offer_ids_subquery = get_active_offers_ids_query(user=None)
    query = Offer.query.filter(Offer.id.in_(offer_ids_subquery))

    if departement_code:
        query = query.join(VenueSQLEntity).filter(
            VenueSQLEntity.departementCode == departement_code)

    return query.count()


def get_offers_available_on_discovery_count_v2(departement_code: str = None) -> int:
    query = DiscoveryView.query

    if departement_code:
        visible_venues_ids = _get_physical_venue_ids_for_departement(departement_code)
    else:
        visible_venues_ids = _get_all_physical_venue_ids()

    query = keep_only_offers_in_venues_or_national(query, visible_venues_ids)

    return query.count()


def get_offers_available_on_search_count(departement_code: str = None) -> int:
    base_query = Offer.query.join(VenueSQLEntity).join(Offerer)
    query = _filter_recommendable_offers_for_search(base_query)

    if departement_code:
        query = query.filter(VenueSQLEntity.departementCode == departement_code)

    return query.count()


def get_offers_with_non_cancelled_bookings_count(departement_code: str = None) -> int:
    query = Offer.query \
        .join(StockSQLEntity) \
        .join(Booking)

    if departement_code:
        query = query.join(VenueSQLEntity).filter(
            VenueSQLEntity.departementCode == departement_code)
    return query \
        .filter(Booking.isCancelled.is_(False)) \
        .filter(Offer.type != str(ThingType.ACTIVATION)) \
        .filter(Offer.type != str(EventType.ACTIVATION)) \
        .distinct(Offer.id) \
        .count()


def get_all_bookings_count(departement_code: str = None) -> int:
    return booking_repository.count_by_departement(departement_code) if departement_code else booking_repository.count()


def get_all_used_or_finished_bookings(departement_code: str) -> int:
    query = booking_repository._query_keep_only_used_and_non_cancelled_bookings_on_non_activation_offers() \
        .join(UserSQLEntity)
    if departement_code:
        query = query.filter(UserSQLEntity.departementCode == departement_code)

    return query \
        .count()


def count_all_cancelled_bookings(departement_code: str = None) -> int:
    return booking_repository.count_cancelled_by_departement(
        departement_code) if departement_code else query_count_all_cancelled_bookings()


def get_offer_counts_grouped_by_type_and_medium(query_get_counts_per_type_and_digital: Callable,
                                                counts_column_name: str) -> pandas.DataFrame:
    offers_by_type_and_digital_table = _get_offers_grouped_by_type_and_medium()
    offer_counts_per_type_and_digital = query_get_counts_per_type_and_digital()

    offers_by_type_and_digital_table[counts_column_name] = 0
    counts_for_other_offers = pandas.DataFrame({
        'Catégorie': ['Autres', 'Autres'],
        'Support': ['Numérique', 'Physique'],
        counts_column_name: [0, 0]
    })

    for offer_counts in offer_counts_per_type_and_digital:
        offer_type = offer_counts[0]
        is_digital = offer_counts[1]
        counts = offer_counts[2]
        support = 'Numérique' if is_digital else 'Physique'

        row_matching_type_and_medium = (offers_by_type_and_digital_table['type'] == offer_type) & (
                    offers_by_type_and_digital_table['Support'] == support)
        has_matching_row = row_matching_type_and_medium.any()

        if has_matching_row:
            offers_by_type_and_digital_table.loc[
                row_matching_type_and_medium,
                counts_column_name] = counts

        else:
            counts_for_other_offers.loc[counts_for_other_offers['Support'] == support, counts_column_name] += counts

    offers_by_type_and_digital_table.drop('type', axis=1, inplace=True)
    offers_by_type_and_digital_table = offers_by_type_and_digital_table.append(counts_for_other_offers, ignore_index=True)
    offers_by_type_and_digital_table.sort_values(by=[counts_column_name, 'Catégorie', 'Support'],
                                                 ascending=[False, True, True], inplace=True)

    return offers_by_type_and_digital_table.reset_index(drop=True)


def _get_offers_grouped_by_type_and_medium() -> pandas.DataFrame:
    human_types = []
    types = []
    digital_or_physical = []

    for event_product_type in EventType:
        human_product_type = event_product_type.value['proLabel']
        human_types.append(human_product_type)
        types.append(str(event_product_type))
        digital_or_physical.append('Physique')

    for product_type in ThingType:
        human_product_type = product_type.value['proLabel']
        can_be_online = not product_type.value['offlineOnly']
        can_be_offline = not product_type.value['onlineOnly']

        if can_be_online:
            human_types.append(human_product_type)
            types.append(str(product_type))
            digital_or_physical.append('Numérique')

        if can_be_offline:
            human_types.append(human_product_type)
            types.append(str(product_type))
            digital_or_physical.append('Physique')

    type_and_digital_dataframe = pandas.DataFrame(
        data={'Catégorie': human_types, 'Support': digital_or_physical, 'type': types})
    type_and_digital_dataframe.sort_values(
        by=['Catégorie', 'Support'], inplace=True, ascending=True)
    type_and_digital_dataframe.reset_index(drop=True, inplace=True)

    return type_and_digital_dataframe


def query_get_offer_counts_grouped_by_type_and_medium() -> List[Tuple[str, bool, int]]:
    return db.engine.execute(
        """
        SELECT type, url IS NOT NULL AS is_digital, count(DISTINCT offer.id)
        FROM offer
        JOIN stock ON stock."offerId" = offer.id
        JOIN venue ON venue.id = offer."venueId"
        JOIN offerer ON offerer.id = venue."managingOffererId"
        JOIN user_offerer ON user_offerer."offererId" = offerer.id
        GROUP BY type, is_digital;
        """)


def query_get_offer_counts_grouped_by_type_and_medium_for_departement(departement_code: str) -> List[
    Tuple[str, bool, int]]:
    return db.engine.execute(
        text("""
        SELECT offer.type, offer.url IS NOT NULL AS is_digital, count(DISTINCT offer.id)
        FROM offer
        JOIN stock ON stock."offerId" = offer.id
        JOIN venue ON venue.id = offer."venueId"
        JOIN offerer ON offerer.id = venue."managingOffererId"
        JOIN user_offerer ON user_offerer."offererId" = offerer.id
        WHERE venue."departementCode"= :departementCode
         OR venue."isVirtual"
        GROUP BY type, is_digital;
        """).bindparams(departementCode=departement_code))


def query_get_booking_counts_grouped_by_type_and_medium() -> List[Tuple[str, bool, int]]:
    return db.engine.execute(
        """
        SELECT offer.type, offer.url IS NOT NULL AS is_digital, SUM(booking.quantity)
        FROM booking
        JOIN stock ON stock.id = booking."stockId"
        JOIN offer ON offer.id = stock."offerId"
        WHERE booking."isCancelled" IS FALSE
        GROUP BY type, is_digital;
        """)


def query_get_booking_counts_grouped_by_type_and_medium_for_departement(departement_code: str) -> List[
    Tuple[str, bool, int]]:
    return db.engine.execute(
        text("""
        SELECT offer.type, offer.url IS NOT NULL AS is_digital, SUM(booking.quantity)
        FROM booking
        JOIN stock ON stock.id = booking."stockId"
        JOIN offer ON offer.id = stock."offerId"
        JOIN "user" ON "user".id = booking."userId"
        WHERE booking."isCancelled" IS FALSE
         AND (
          "user"."departementCode"= :departementCode
          )
        GROUP BY type, is_digital;
        """).bindparams(departementCode=departement_code))
