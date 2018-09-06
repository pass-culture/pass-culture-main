""" event_occurrences """
from domain.stocks import soft_delete_stock

def soft_delete_event_occurrence(event_occurrence):
    soft_delete_stock(event_occurrence.stock)

    event_occurrence.isSoftDeleted = True
    PcObject.check_and_save(event_occurrence)
