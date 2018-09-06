""" event_occurrences """
from domain.stocks import soft_delete_stock

def soft_delete_event_occurrence(event_occurrence):
    stock_and_bookings_to_save = soft_delete_stock(event_occurrence.stock)

    event_occurrence.isSoftDeleted = True

    return [event_occurrence] + stock_and_bookings_to_save
