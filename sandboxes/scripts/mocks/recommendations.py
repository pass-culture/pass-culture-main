""" recommendations """
from utils.human_ids import humanize

RECOMMENDATION_MOCKS = []

SCRATCH_RECOMMENDATION_MOCKS = [
    {
        "id": humanize(0),
        "mediationId": humanize(10),
        "offerId": humanize(0), # Rencontre avec Franck Lepage LE GRAND REX PARIS
        "userId": humanize(999) # pctest.jeune.93@btmx.fr
    },

    {
        "id": humanize(1),
        "mediationId": humanize(11),
        "offerId": humanize(3), # Ravage THEATRE DE L ODEON
        "userId": humanize(999) # pctest.jeune.93@btmx.fr
    }
]
RECOMMENDATION_MOCKS += SCRATCH_RECOMMENDATION_MOCKS
