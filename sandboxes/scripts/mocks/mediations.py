from models.mediation import Mediation

from sandboxes.scripts.mocks.offers import ALL_TYPED_EVENT_OFFER_MOCKS,\
                                           ALL_TYPED_THING_OFFER_MOCKS
from sandboxes.scripts.mocks import get_all_typed_event_mediation_mocks,\
                                    get_all_typed_thing_mediation_mocks
from sandboxes.utils import get_last_stored_id_of_model
from utils.human_ids import dehumanize, humanize

MEDIATION_MOCKS = []

# NEED TO BE AT LEAST GREATER THEN 1 (because of tuto mediations)
LAST_STORED_MEDIATION_ID = get_last_stored_id_of_model(Mediation)

SCRATCH_MEDIATION_MOCKS = [
    {

        "id": humanize(LAST_STORED_MEDIATION_ID + 1),
        "offerId": humanize(1), # Rencontre avec Franck Lepage LE GRAND REX PARIS
        "thumbName": "FranckLepage"
    },

    {
        "id": humanize(LAST_STORED_MEDIATION_ID + 2),
        "offerId": humanize(4), # Ravage THEATRE DE L ODEON
        "thumbName": "Ravage"
    }
]
MEDIATION_MOCKS += SCRATCH_MEDIATION_MOCKS

ALL_TYPED_EVENT_MEDIATION_MOCKS = get_all_typed_event_mediation_mocks(
    ALL_TYPED_EVENT_OFFER_MOCKS,
    starting_id=dehumanize(MEDIATION_MOCKS[-1]['id']) + 1
)
ALL_TYPED_THING_MEDIATION_MOCKS = get_all_typed_thing_mediation_mocks(
    ALL_TYPED_THING_OFFER_MOCKS,
    starting_id=dehumanize(ALL_TYPED_EVENT_MEDIATION_MOCKS[-1]['id']) + 1
)
ALL_TYPED_MEDIATION_MOCKS = ALL_TYPED_EVENT_MEDIATION_MOCKS + ALL_TYPED_THING_MEDIATION_MOCKS
MEDIATION_MOCKS += ALL_TYPED_MEDIATION_MOCKS
