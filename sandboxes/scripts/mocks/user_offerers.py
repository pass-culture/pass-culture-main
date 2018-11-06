""" user offerers """
from utils.human_ids import humanize

USER_OFFERER_MOCKS = []

SCRATCH_USER_OFFERER_MOCKS = [
    {
        "id": humanize(1000),
        # "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "offererId": humanize(1000), # LE GRAND REX PARIS
        # "offererKey": "d33ee240-dc59-11e8-a29f-0242ac130000", # LE GRAND REX PARIS
        "rights": "admin",
        "userId": humanize(1000), # pctest.pro.1@btmx.fr
        # "userKey": "d33ee240-dc59-11e8-a29f-0242ac130003" # pctest.pro.1@btmx.fr
    },
    {
        "id": humanize(999),
        # "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "offererId": humanize(999), # THEATRE DE L ODEON
        # "offererKey": "d33ee240-dc59-11e8-a29f-0242ac130001", # THEATRE DE L ODEON
        "rights": "editor",
        "userId": humanize(1000), # pctest.pro.1@btmx.fr
        # "userKey": "d33ee240-dc59-11e8-a29f-0242ac130003" # pctest.pro.1@btmx.fr
    },
    {
        "id": humanize(998),
        # "key": "d33ee240-dc59-11e8-a29f-0242ac130002",
        "offererId": humanize(998), # THEATRE DU SOLEIL
        # "offererKey": "d33ee240-dc59-11e8-a29f-0242ac130002", # THEATRE DU SOLEIL
        "rights": "editor",
        "userId": humanize(1000), # pctest.pro.1@btmx.fr
        # "userKey": "d33ee240-dc59-11e8-a29f-0242ac130003" # pctest.pro.1@btmx.fr
    }
]
USER_OFFERER_MOCKS += SCRATCH_USER_OFFERER_MOCKS
