""" offerers """
from sandboxes.scripts.mocks.utils.generators import get_all_offerer_mocks

OFFERER_MOCKS = []

ALL_OFFERER_MOCKS = get_all_offerer_mocks()
OFFERER_MOCKS += ALL_OFFERER_MOCKS

SCRATCH_OFFERER_MOCKS = [
    {
        "address": "1 BD POISSONNIERE",
        "city": "Paris",
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "name": "LE GRAND REX PARIS",
        "postalCode": "75002",
        "siren": "507633576"
    },
    {
        "address": "6 RUE GROLEE",
        "city": "Lyon",
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "name": "THEATRE DE L ODEON",
        "postalCode": "69002",
        "siren": "750505703"
    },
    {
        "address": "LIEU DIT CARTOUCHERIE",
        "city": "Paris 12",
        "key": "d33ee240-dc59-11e8-a29f-0242ac130002",
        "name": "THEATRE DU SOLEIL",
        "postalCode": "75012",
        "siren": "784340093"
    }
]
OFFERER_MOCKS += SCRATCH_OFFERER_MOCKS
