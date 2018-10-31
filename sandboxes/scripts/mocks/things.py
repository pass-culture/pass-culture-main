""" things """
from sandboxes.scripts.mocks import get_all_typed_thing_mocks

THING_MOCKS = []

ALL_TYPED_THING_MOCKS = get_all_typed_thing_mocks()
THING_MOCKS += ALL_TYPED_THING_MOCKS

SCRATCH_THING_MOCKS = [
    {
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "name": "Ravage",
        "type": "ThingType.LIVRE_EDITION"
    },
    {
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "name": "Le Monde Diplomatique",
        "type": "ThingType.PRESSE_ABO"
    },
]
THING_MOCKS += SCRATCH_THING_MOCKS
