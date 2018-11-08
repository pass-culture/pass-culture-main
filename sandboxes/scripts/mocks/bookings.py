""" bookings """
from sandboxes.scripts.mocks.mediations import LAST_STORED_MEDIATION_ID
from utils.human_ids import humanize

BOOKING_MOCKS = []

SCRATCH_BOOKING_MOCKS = [
    {
        "amount": 1,
        "id": humanize(1),
        #"recommendationId": humanize(1000 + LAST_STORED_MEDIATION_ID + 1), # Rencontre avec Franck Lepage LE GRAND REX PARIS
        "recommendationId": humanize(1),
        "stockId": humanize(1), # 20h
        "token": "2ALYY5",
        "userId": humanize(2) # pctest.jeune.93@btmx.fr
    },
    {
        "amount": 1,
        "id": humanize(2),
        #"recommendationId": humanize(1000 + LAST_STORED_MEDIATION_ID + 2), # Ravage THEATRE DE L ODEON
        "recommendationId": humanize(2),
        "stockId": humanize(7),
        "token": "2AEVY3",
        "userId": humanize(2) # pctest.jeune.93@btmx.fr
    }
]
BOOKING_MOCKS += SCRATCH_BOOKING_MOCKS
