""" stocks """
from repository import booking_queries, offerer_queries
from validation.stocks import check_offer_offerer_exists, \
                              check_event_occurrence_offerer_exists


def find_offerer_for_new_stock(offer_id, event_occurrence_id):
    if offer_id:
        offerer = offerer_queries.get_by_offer_id(offer_id)
        check_offer_offerer_exists(offerer)
    if event_occurrence_id:
        offerer = offerer_queries.get_by_event_occurrence_id(event_occurrence_id)
        check_event_occurrence_offerer_exists(offerer)
    return offerer

def _cancel_bookings(all_bookings_with_soft_deleted_stocks):
    soft_deleted_bookings = []
    for booking in all_bookings_with_soft_deleted_stocks:
        booking.isCancelled = True
        soft_deleted_bookings.append(booking)
    return soft_deleted_bookings

def soft_delete_stock(stock):
    stock.isSoftDeleted = True

    all_bookings_with_soft_deleted_stocks = booking_queries.find_all_with_soft_deleted_stocks()
    return [stock] + _cancel_bookings(all_bookings_with_soft_deleted_stocks)
