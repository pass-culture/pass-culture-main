""" offerers """
from sandboxes.scripts.utils.generators import get_all_offerer_mocks
from utils.human_ids import dehumanize, humanize

OFFERER_MOCKS = []

SCRATCH_OFFERER_MOCKS = [
    {
        "address": "1 BD POISSONNIERE",
        "city": "Paris",
        "id": humanize(1),
        "name": "LE GRAND REX PARIS",
        "postalCode": "75002",
        "siren": "507633576"
    },
    {
        "address": "6 RUE GROLEE",
        "city": "Lyon",
        "id": humanize(2),
        "name": "THEATRE DE L ODEON",
        "postalCode": "69002",
        "siren": "750505703"
    },
    {
        "address": "LIEU DIT CARTOUCHERIE",
        "city": "Paris 12",
        "id": humanize(3),
        "name": "THEATRE DU SOLEIL",
        "postalCode": "75012",
        "siren": "784340093"
    }
]
OFFERER_MOCKS += SCRATCH_OFFERER_MOCKS

ALL_OFFERER_MOCKS = get_all_offerer_mocks(
    starting_id=dehumanize(OFFERER_MOCKS[-1]['id']) + 1
)
OFFERER_MOCKS += ALL_OFFERER_MOCKS
