""" event_occurrences """
from sandboxes.scripts.mocks import get_all_event_occurrence_mocks_by_type
from utils.date import get_now_datetime_plus_an_hour_string


event_occurrence_mocks = [
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130000"
    },
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130000"
    },

    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130001"
    },
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130001"
    },
    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130001"
    },

    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130002"
    },

    {
        "beginningDatetime": get_now_datetime_plus_an_hour_string(),
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130002"
    }
] +  get_all_event_occurrence_mocks_by_type()
