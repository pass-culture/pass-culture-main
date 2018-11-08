""" recommendations """
from sandboxes.scripts.mocks.mediations import LAST_STORED_MEDIATION_ID
from utils.human_ids import humanize

RECOMMENDATION_MOCKS = []

SCRATCH_RECOMMENDATION_MOCKS = [
    {
        # Be sure that any recommendation created will not conflict with that ones
        # "id": humanize(1000 + LAST_STORED_MEDIATION_ID + 1),
        "id": humanize(1),
        "mediationId": humanize(LAST_STORED_MEDIATION_ID + 1),
        "offerId": humanize(1), # Rencontre avec Franck Lepage LE GRAND REX PARIS
        "userId": humanize(1) # pctest.jeune.93@btmx.fr
    },

    {
        # "id": humanize(1000 + LAST_STORED_MEDIATION_ID + 2),
        "id": humanize(2),
        "mediationId": humanize(LAST_STORED_MEDIATION_ID + 2),
        "offerId": humanize(4), # Ravage THEATRE DE L ODEON
        "userId": humanize(1) # pctest.jeune.93@btmx.fr
    }
]
RECOMMENDATION_MOCKS += SCRATCH_RECOMMENDATION_MOCKS
