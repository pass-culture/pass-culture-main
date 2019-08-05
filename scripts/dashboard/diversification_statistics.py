import pandas

from models import Offerer, UserOfferer, Venue, Offer, Stock, Booking, EventType, ThingType
from models.db import db
from repository.booking_queries import query_final_bookings
from repository.offer_queries import active_offer_ids_query


def get_offerer_count() -> int:
    return _query_offerers_with_user_offerer().count()


def _query_offerers_with_user_offerer():
    return Offerer.query \
        .join(UserOfferer) \
        .distinct(Offerer.id)


def get_offerer_with_stock_count() -> int:
    return _query_offerers_with_user_offerer() \
        .join(Venue, Venue.managingOffererId == Offerer.id) \
        .join(Offer) \
        .join(Stock) \
        .count()


def get_offerers_with_offer_available_on_discovery_count() -> int:
    offer_ids_subquery = active_offer_ids_query()
    return Offerer.query \
        .join(Venue) \
        .join(Offer) \
        .filter(Offer.id.in_(offer_ids_subquery)) \
        .distinct(Offerer.id) \
        .count()


def get_offerers_with_non_cancelled_bookings_count() -> int:
    return Offerer.query \
        .join(Venue) \
        .join(Offer) \
        .join(Stock) \
        .join(Booking) \
        .filter_by(isCancelled=False) \
        .distinct(Offerer.id) \
        .count()


def get_offers_with_user_offerer_and_stock_count() -> int:
    return Offer.query \
        .join(Venue) \
        .join(Offerer) \
        .join(UserOfferer) \
        .join(Stock, Stock.offerId == Offer.id) \
        .distinct(Offer.id) \
        .count()


def get_offers_available_on_discovery_count() -> int:
    offer_ids_subquery = active_offer_ids_query()
    return Offer.query.filter(Offer.id.in_(offer_ids_subquery)).count()


def get_offers_with_non_cancelled_bookings_count() -> int:
    return Offer.query \
        .join(Stock) \
        .join(Booking) \
        .filter_by(isCancelled=False) \
        .distinct(Offer.id) \
        .count()


def get_all_bookings_count() -> int:
    return Booking.query.count()


def get_all_used_bookings_count() -> int:
    return query_final_bookings().count()


def get_all_cancelled_bookings_count():
    return Booking.query.filter_by(isCancelled=True).count()


def _get_counts_grouped_by_type_and_medium(query_get_counts_per_type_and_digital, counts_column_name):
    offers_by_type_and_digital_table = _get_offers_grouped_by_type_and_medium()
    offer_counts_per_type_and_digital = query_get_counts_per_type_and_digital()

    offers_by_type_and_digital_table[counts_column_name] = 0
    for offer_counts in offer_counts_per_type_and_digital:
        offer_type = offer_counts[0]
        is_digital = offer_counts[1]
        counts = offer_counts[2]
        support = 'Numérique' if is_digital else 'Physique'
        offers_by_type_and_digital_table.loc[
            (offers_by_type_and_digital_table['type'] == offer_type) & (offers_by_type_and_digital_table['Support'] == support),
            counts_column_name] = counts

    offers_by_type_and_digital_table.drop('type', axis=1, inplace=True)
    offers_by_type_and_digital_table.sort_values(by=[counts_column_name, 'Catégorie', 'Support'], ascending=[False, True, True], inplace=True)

    return offers_by_type_and_digital_table.reset_index(drop=True)


def _get_offers_grouped_by_type_and_medium():
    human_types = []
    types = []
    digital_or_physical = []

    for product_type in EventType:
        human_product_type = product_type.value['proLabel']
        human_types.append(human_product_type)
        types.append(str(product_type))
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

    type_and_digital_dataframe = pandas.DataFrame(data={'Catégorie': human_types, 'Support': digital_or_physical, 'type': types})
    type_and_digital_dataframe.sort_values(by=['Catégorie', 'Support'], inplace=True, ascending=True)
    type_and_digital_dataframe.reset_index(drop=True, inplace=True)

    return type_and_digital_dataframe


def _query_get_offer_counts_grouped_by_type_and_medium():
    return db.engine.execute(
        """
        SELECT type, url IS NOT NULL AS is_digital, count(offer.id) 
        FROM offer 
        JOIN stock ON stock."offerId" = offer.id
        JOIN venue ON venue.id = offer."venueId"
        JOIN offerer ON offerer.id = venue."managingOffererId"
        JOIN user_offerer ON user_offerer."offererId" = offerer.id
        GROUP BY type, is_digital;
        """)


def _query_get_booking_counts_grouped_by_type_and_medium():
    return db.engine.execute(
        """
        SELECT type, url IS NOT NULL AS is_digital, SUM(booking.quantity)
        FROM booking 
        JOIN stock ON stock.id = booking."stockId"
        JOIN offer ON offer.id = stock."offerId"
        JOIN venue ON venue.id = offer."venueId"
        JOIN offerer ON offerer.id = venue."managingOffererId"
        JOIN user_offerer ON user_offerer."offererId" = offerer.id
        WHERE booking."isCancelled" IS FALSE
        GROUP BY type, is_digital;
        """)
