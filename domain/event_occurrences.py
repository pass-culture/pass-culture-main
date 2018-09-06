""" event_occurrences """
from domain.stocks import soft_delete_stock

def soft_delete_event_occurrence(event_occurrence):
    stocks_and_bookings_to_save = []
    for stock in event_occurrence.stocks:
        stocks_and_bookings_to_save += soft_delete_stock(stock)

    event_occurrence.isSoftDeleted = True

    return [event_occurrence] + stocks_and_bookings_to_save
