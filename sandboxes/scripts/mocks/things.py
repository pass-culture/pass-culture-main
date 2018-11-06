""" things """
from sandboxes.scripts.mocks import get_all_typed_thing_mocks
from utils.human_ids import humanize

THING_MOCKS = []

ALL_TYPED_THING_MOCKS = get_all_typed_thing_mocks()
THING_MOCKS += ALL_TYPED_THING_MOCKS

SCRATCH_THING_MOCKS = [
    {
        "id": humanize(0),
        "name": "Ravage",
        "type": "ThingType.LIVRE_EDITION"
    },
    {
        "id": humanize(1),
        "name": "Le Monde Diplomatique",
        "type": "ThingType.PRESSE_ABO"
    },
]
THING_MOCKS += SCRATCH_THING_MOCKS
