""" things """
from sandboxes.scripts.mocks import get_all_typed_thing_mocks

THING_MOCKS = []

ALL_TYPED_THING_MOCKS = get_all_typed_thing_mocks()
THING_MOCKS += ALL_TYPED_THING_MOCKS

SCRATCH_THING_MOCKS = [
    {
        "name": "Ravage",
        "type": "ThingType.LIVRE_EDITION"
    },
    {
        "name": "Le Monde Diplomatique",
        "type": "ThingType.PRESSE_ABO"
    },
]
THING_MOCKS += SCRATCH_THING_MOCKS
