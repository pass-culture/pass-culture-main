""" stocks """
from repository import offerer_queries
from validation.stocks import check_offer_offerer_exists, \
                              check_event_occurrence_offerer_exists


def find_offerer_for_new_stock(offer_id, event_occurrence_id):
    offerer = None
    if offer_id:
        offerer = offerer_queries.get_by_offer_id(offer_id)
        check_offer_offerer_exists(offerer)
    if event_occurrence_id:
        offerer = offerer_queries.get_by_event_occurrence_id(event_occurrence_id)
        check_event_occurrence_offerer_exists(offerer)
    return offerer
