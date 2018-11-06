""" venue """
from sandboxes.scripts.mocks.utils.generators import get_all_venue_mocks
from sandboxes.scripts.mocks.offerers import ALL_OFFERER_MOCKS
from utils.human_ids import humanize

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
        "id": humanize(0),
        "name": "LE GRAND REX PARIS",
        "offererId": humanize(1000), # LE GRAND REX PARIS,
        "postalCode": "75002",
        "siret": "50763357600016"
    },
    {
        "isVirtual": True,
        "id": humanize(1),
        "name": "Offre en ligne",
        "offererId": humanize(1000) # LE GRAND REX PARIS
    },
    {
        "address": "6 rue Grolee",
        "bookingEmail": "fake2@email.com",
        "city": "Lyon",
        "departementCode": "69",
        "id": humanize(2),
        "latitude": 45.762606,
        "longitude": 4.836694,
        "name": "THEATRE DE L ODEON",
        "offererId": humanize(999), # "THEATRE DE L ODEON"
        "postalCode": "69002",
        "siret": "75050570300025"
    },
    {
        "isVirtual": True,
        "id": humanize(3),
        "name": "Offre en ligne",
        "offererId": humanize(999) # "THEATRE DE L ODEON"
    },
    {
        "isVirtual": True,
        "id": humanize(4),
        "name": "Offre en ligne",
        "offererId": humanize(999) # "THEATRE DU SOLEIL"
    }
]

VENUE_MOCKS += SCRATCH_MOCKS
