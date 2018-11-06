from sandboxes.scripts.mocks.offers import ALL_TYPED_EVENT_OFFER_MOCKS,\
                                           ALL_TYPED_THING_OFFER_MOCKS
from sandboxes.scripts.mocks import get_all_typed_event_mediation_mocks,\
                                    get_all_typed_thing_mediation_mocks
from utils.human_ids import humanize

MEDIATION_MOCKS = [
    {
        "id": humanize(10),
        "offerId": humanize(0), # Rencontre avec Franck Lepage LE GRAND REX PARIS
        "thumbName": "FranckLepage"
    },

    {
        "id": humanize(11),
        "offerId": humanize(3), # Ravage THEATRE DE L ODEON
        "thumbName": "Ravage"
    }
]

ALL_TYPED_EVENT_MEDIATION_MOCKS = get_all_typed_event_mediation_mocks(ALL_TYPED_EVENT_OFFER_MOCKS)
ALL_TYPED_THING_MEDIATION_MOCKS = get_all_typed_thing_mediation_mocks(ALL_TYPED_THING_OFFER_MOCKS)
ALL_TYPED_MEDIATION_MOCKS = ALL_TYPED_EVENT_MEDIATION_MOCKS + ALL_TYPED_THING_MEDIATION_MOCKS
MEDIATION_MOCKS += ALL_TYPED_MEDIATION_MOCKS
