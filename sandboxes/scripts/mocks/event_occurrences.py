""" event_occurrences """
from datetime import timedelta

from sandboxes.scripts.mocks.offers import ALL_TYPED_EVENT_OFFER_MOCKS
from sandboxes.scripts.mocks.utils.generators import get_all_typed_event_occurrence_mocks
from utils.date import today, strftime

EVENT_OCCURRENCE_MOCKS = []

ALL_TYPED_EVENT_OCCURRENCE_MOCKS = get_all_typed_event_occurrence_mocks(ALL_TYPED_EVENT_OFFER_MOCKS)
EVENT_OCCURRENCE_MOCKS += ALL_TYPED_EVENT_OCCURRENCE_MOCKS

SCRATCH_EVENT_OCCURRENCE_MOCKS = [
    {
        "beginningDatetime": strftime(today),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130000" # Rencontre avec Franck Lepage  LE GRAND REX PARIS
    },
    {
        "beginningDatetime": strftime(today + timedelta(days=1)),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130000" # Rencontre avec Franck Lepage  LE GRAND REX PARIS
    },


    {
        "beginningDatetime": strftime(today),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130002",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130001" # Concert de Gael Faye THEATRE DE L ODEON
    },

    {
        "beginningDatetime":  strftime(today),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130003",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130002" # PNL chante Marx THEATRE DE L ODEON
    }
]
EVENT_OCCURRENCE_MOCKS += SCRATCH_EVENT_OCCURRENCE_MOCKS
