""" event_occurrences """
from sandboxes.scripts.mocks.offers import ALL_TYPED_OFFER_MOCKS
from sandboxes.scripts.mocks.utils.generators import get_all_typed_event_occurrence_mocks
from utils.date import get_now_datetime_plus_an_hour_string

EVENT_OCCURRENCE_MOCKS = []

ALL_TYPED_EVENT_OCCURRENCE_MOCKS = get_all_typed_event_occurrence_mocks(ALL_TYPED_OFFER_MOCKS)
EVENT_OCCURRENCE_MOCKS += ALL_TYPED_EVENT_OCCURRENCE_MOCKS

SCRATCH_EVENT_OCCURRENCE_MOCKS = [
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130000"
    },
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130000"
    },

    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130001"
    },
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130001"
    },
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130001"
    },

    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130002",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130002"
    },

    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "key": "d33ee240-dc59-11e8-a29f-0242ac130002",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130002"
    }
]
EVENT_OCCURRENCE_MOCKS += SCRATCH_EVENT_OCCURRENCE_MOCKS
