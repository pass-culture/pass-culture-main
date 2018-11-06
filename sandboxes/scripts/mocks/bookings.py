""" bookings """
from utils.human_ids import humanize

BOOKING_MOCKS = []

SCRATCH_BOOKING_MOCKS = [
    {
        "id": humanize(1),
        "recommendationId": humanize(1), # Rencontre avec Franck Lepage LE GRAND REX PARIS
        "stockId": humanize(1), # 20h
        "token": "2ALYY5",
        "userId": humanize(2) # pctest.jeune.93@btmx.fr
    },
    {
        "id": humanize(2),
        "recommendationId": humanize(2), # Ravage THEATRE DE L ODEON
        "stockId": humanize(7),
        "token": "2AEVY3",
        "userId": humanize(2) # pctest.jeune.93@btmx.fr
    }
]
BOOKING_MOCKS += SCRATCH_BOOKING_MOCKS
