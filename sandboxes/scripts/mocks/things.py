""" things """
from sandboxes.scripts.mocks import get_all_typed_thing_mocks
from utils.human_ids import dehumanize, humanize

THING_MOCKS = []

SCRATCH_THING_MOCKS = [
    {
        "id": humanize(1),
        "name": "Ravage",
        "type": "ThingType.LIVRE_EDITION"
    },
    {
        "id": humanize(2),
        "name": "Le Monde Diplomatique",
        "type": "ThingType.PRESSE_ABO"
    },
]
THING_MOCKS += SCRATCH_THING_MOCKS

ALL_TYPED_THING_MOCKS = get_all_typed_thing_mocks(
    starting_id=dehumanize(THING_MOCKS[-1]['id']) + 1
)
THING_MOCKS += ALL_TYPED_THING_MOCKS
