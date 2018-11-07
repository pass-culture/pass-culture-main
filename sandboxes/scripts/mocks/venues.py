""" venue """
from sandboxes.scripts.utils.generators import get_all_venue_mocks
from sandboxes.scripts.mocks.offerers import ALL_OFFERER_MOCKS
from utils.human_ids import dehumanize, humanize

VENUE_MOCKS = []

SCRATCH_VENUE_MOCKS = [
    {
        "address": "1 BD POISSONNIERE",
        "bookingEmail": "fake@email.com",
        "city": "Paris",
        "departementCode": "75",
        "id": humanize(1),
        "latitude": 48.870665,
        "longitude": 2.3478,
        "managingOffererId": humanize(1), # LE GRAND REX PARIS,
        "name": "LE GRAND REX PARIS",
        "postalCode": "75002",
        "siret": "50763357600016"
    },
    {
        "isVirtual": True,
        "id": humanize(2),
        "managingOffererId": humanize(1), # LE GRAND REX PARIS
        "name": "Offre en ligne",
    },
    {
        "address": "6 rue Grolee",
        "bookingEmail": "fake2@email.com",
        "city": "Lyon",
        "departementCode": "69",
        "id": humanize(3),
        "latitude": 45.762606,
        "longitude": 4.836694,
        "managingOffererId": humanize(2), # "THEATRE DE L ODEON"
        "name": "THEATRE DE L ODEON",
        "postalCode": "69002",
        "siret": "75050570300025"
    },
    {
        "isVirtual": True,
        "id": humanize(4),
        "managingOffererId": humanize(2), # "THEATRE DE L ODEON"
        "name": "Offre en ligne",
    },
    {
        "isVirtual": True,
        "id": humanize(5),
        "managingOffererId": humanize(3), # "THEATRE DU SOLEIL"
        "name": "Offre en ligne",
    }
]
VENUE_MOCKS += SCRATCH_VENUE_MOCKS

ALL_VENUE_MOCKS = get_all_venue_mocks(
    ALL_OFFERER_MOCKS,
    starting_id=dehumanize(VENUE_MOCKS[-1]['id']) + 1
)
VENUE_MOCKS += ALL_VENUE_MOCKS
