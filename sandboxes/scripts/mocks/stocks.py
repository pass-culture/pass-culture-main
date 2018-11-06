""" stocks """
from sandboxes.scripts.mocks.event_occurrences import ALL_TYPED_EVENT_OCCURRENCE_MOCKS
from sandboxes.scripts.mocks.offers import ALL_TYPED_THING_OFFER_MOCKS
from sandboxes.scripts.mocks.utils.generators import get_all_typed_event_stock_mocks, \
                                                     get_all_typed_thing_stock_mocks
from utils.human_ids import humanize

STOCK_MOCKS = []

ALL_TYPED_EVENT_STOCK_MOCKS = get_all_typed_event_stock_mocks(ALL_TYPED_EVENT_OCCURRENCE_MOCKS)
ALL_TYPED_THING_STOCK_MOCKS = get_all_typed_thing_stock_mocks(ALL_TYPED_THING_OFFER_MOCKS)
ALL_TYPED_STOCK_MOCKS = ALL_TYPED_EVENT_STOCK_MOCKS + ALL_TYPED_THING_STOCK_MOCKS
STOCK_MOCKS += ALL_TYPED_STOCK_MOCKS

SCRATCH_STOCK_MOCKS = [
    {
        "available": 10,
        "eventOccurrenceId": humanize(0), # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h
        "id": humanize(0),
        "price": 10
    },
    {
        "available": 15,
        "eventOccurrenceId": humanize(0), # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h
        "id": humanize(1),
        "price": 15
    },

    {
        "available": 100,
        "eventOccurrenceId": humanize(1), # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h + 1D
        "id": humanize(3),
        "price": 10
    },
    {
        "available": 90,
        "eventOccurrenceId": humanize(1), # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h + 1D
        "id": humanize(4),
        "price": 15
    },

    {
        "available": 50,
        "eventOccurrenceId": humanize(2), # Concert de Gael Faye THEATRE DE L ODEON 20h
        "id": humanize(5),
        "price": 50
    },

    {
        "available": 50,
        "eventOccurrenceId": humanize(3), # PNL chante Marx THEATRE DE L ODEON 20h
        "id": humanize(6),
        "price": 50
    },

    {
        "available": 50,
        "offerId": humanize(3), # Ravage THEATRE DE L ODEON
        "id": humanize(7),
        "price": 50
    }
]
STOCK_MOCKS += SCRATCH_STOCK_MOCKS
