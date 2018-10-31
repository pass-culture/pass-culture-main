from sandboxes.scripts.mocks.offers import ALL_TYPED_EVENT_OFFER_MOCKS,\
                                           ALL_TYPED_THING_OFFER_MOCKS
from sandboxes.scripts.mocks import get_all_typed_event_mediation_mocks,\
                                    get_all_typed_thing_mediation_mocks

MEDIATION_MOCKS = [
    {
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130000", # Rencontre avec Franck Lepage LE GRAND REX PARIS
        "thumbName": "FranckLepage"
    },

    {
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "offerKey": "d33ee240-dc59-11e8-a29f-0242ac130003", # Ravage THEATRE DE L ODEON
        "thumbName": "Ravage"
    }
]

ALL_TYPED_EVENT_MEDIATION_MOCKS = get_all_typed_event_mediation_mocks(ALL_TYPED_EVENT_OFFER_MOCKS)
ALL_TYPED_THING_MEDIATION_MOCKS = get_all_typed_thing_mediation_mocks(ALL_TYPED_THING_OFFER_MOCKS)
ALL_TYPED_MEDIATION_MOCKS = ALL_TYPED_EVENT_MEDIATION_MOCKS + ALL_TYPED_THING_MEDIATION_MOCKS
MEDIATION_MOCKS += ALL_TYPED_MEDIATION_MOCKS
