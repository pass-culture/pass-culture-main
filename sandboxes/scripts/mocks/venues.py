""" venue """
from sandboxes.scripts.mocks.utils.generators import get_all_venue_mocks
from sandboxes.scripts.mocks.offerers import ALL_OFFERER_MOCKS

VENUE_MOCKS = []

ALL_VENUE_MOCKS = get_all_venue_mocks(ALL_OFFERER_MOCKS)
VENUE_MOCKS += ALL_VENUE_MOCKS

SCRATCH_MOCKS = [
    {
        "address": "1 BD POISSONNIERE",
        "bookingEmail": "fake@email.com",
        "city": "Paris",
        "departementCode": "75",
        "latitude": 48.870665,
        "longitude": 2.3478,
        "key": 'd33ee240-dc59-11e8-a29f-0242ac130002',
        "name": "LE GRAND REX PARIS",
        "offererName": "LE GRAND REX PARIS",
        "postalCode": "75002",
        "siret": "50763357600016"
    },
    {
        "isVirtual": True,
        "key": 'd33ee240-dc59-11e8-a29f-0242ac130003',
        "name": "Offre en ligne",
        "offererName": "LE GRAND REX PARIS"
    },
    {
        "address": "6 rue Grolee",
        "bookingEmail": "fake2@email.com",
        "city": "Lyon",
        "departementCode": "69",
        "latitude": 45.762606,
        "longitude": 4.836694,
        "key": 'd33ee240-dc59-11e8-a29f-0242ac130004',
        "name": "THEATRE DE L ODEON",
        "offererName": "THEATRE DE L ODEON",
        "postalCode": "69002",
        "siret": "75050570300025"
    },
    {
        "isVirtual": True,
        "key": 'd33ee240-dc59-11e8-a29f-0242ac130005',
        "name": "Offre en ligne",
        "offererName": "THEATRE DE L ODEON"
    },
    {
        "isVirtual": True,
        "key": 'd33ee240-dc59-11e8-a29f-0242ac130006',
        "name": "Offre en ligne",
        "offererName": "THEATRE DU SOLEIL"
    }
]

VENUE_MOCKS += SCRATCH_MOCKS
