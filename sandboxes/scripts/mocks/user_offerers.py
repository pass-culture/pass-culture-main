""" user offerers """
from utils.human_ids import humanize

USER_OFFERER_MOCKS = []

SCRATCH_USER_OFFERER_MOCKS = [
    {
        "id": humanize(1),
        "offererId": humanize(1), # LE GRAND REX PARIS
        "rights": "admin",
        "userId": humanize(4) # pctest.pro.1@btmx.fr
    },
    {
        "id": humanize(2),
        "offererId": humanize(2), # THEATRE DE L ODEON
        "rights": "editor",
        "userId": humanize(4), # pctest.pro.1@btmx.fr
    },
    {
        "id": humanize(3),
        "offererId": humanize(3), # THEATRE DU SOLEIL
        "rights": "editor",
        "userId": humanize(4), # pctest.pro.1@btmx.fr
    }
]
USER_OFFERER_MOCKS += SCRATCH_USER_OFFERER_MOCKS
