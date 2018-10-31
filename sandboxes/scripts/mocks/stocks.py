""" stocks """
from sandboxes.scripts.mocks.event_occurrences import ALL_TYPED_EVENT_OCCURRENCE_MOCKS
from sandboxes.scripts.mocks.offers import ALL_TYPED_THING_OFFER_MOCKS
from sandboxes.scripts.mocks.utils.generators import get_all_typed_event_stock_mocks, \
                                                     get_all_typed_thing_stock_mocks

STOCK_MOCKS = []

ALL_TYPED_EVENT_STOCK_MOCKS = get_all_typed_event_stock_mocks(ALL_TYPED_EVENT_OCCURRENCE_MOCKS)
ALL_TYPED_THING_STOCK_MOCKS = get_all_typed_thing_stock_mocks(ALL_TYPED_THING_OFFER_MOCKS)
ALL_TYPED_STOCK_MOCKS = ALL_TYPED_EVENT_STOCK_MOCKS + ALL_TYPED_THING_STOCK_MOCKS
STOCK_MOCKS += ALL_TYPED_STOCK_MOCKS

SCRATCH_STOCK_MOCKS = [
    {
        "available": 10,
        "eventOccurrenceKey": "d33ee240-dc59-11e8-a29f-0242ac130000", # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "price": 10
    },
    {
        "available": 15,
        "eventOccurrenceKey": "d33ee240-dc59-11e8-a29f-0242ac130000", # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "price": 15
    },

    {
        "available": 100,
        "eventOccurrenceKey": "d33ee240-dc59-11e8-a29f-0242ac130001", # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h + 1D
        "key": "d33ee240-dc59-11e8-a29f-0242ac130002",
        "price": 10
    },
    {
        "available": 90,
        "eventOccurrenceKey": "d33ee240-dc59-11e8-a29f-0242ac130001", # Rencontre avec Franck Lepage  LE GRAND REX PARIS 20h + 1D
        "key": "d33ee240-dc59-11e8-a29f-0242ac130004",
        "price": 15
    },

    {
        "available": 50,
        "eventOccurrenceKey": "d33ee240-dc59-11e8-a29f-0242ac130002", # Concert de Gael Faye THEATRE DE L ODEON 20h
        "key": "d33ee240-dc59-11e8-a29f-0242ac130005",
        "price": 50
    },

    {
        "available": 50,
        "eventOccurrenceKey": 'd33ee240-dc59-11e8-a29f-0242ac130003', # PNL chante Marx THEATRE DE L ODEON 20h
        "key": "d33ee240-dc59-11e8-a29f-0242ac130006",
        "price": 50
    },

    {
        "available": 50,
        "offerKey": 'd33ee240-dc59-11e8-a29f-0242ac130003', # Ravage THEATRE DE L ODEON
        "key": "d33ee240-dc59-11e8-a29f-0242ac130007",
        "price": 50
    }
]
STOCK_MOCKS += SCRATCH_STOCK_MOCKS
