""" things """
from sandboxes.scripts.mocks import get_all_thing_mocks_by_type

thing_mocks = [
    {
        "name": "Ravage",
        "type": "ThingType.LIVRE_EDITION"
    },
    {
        "name": "Le Monde Diplomatique",
        "type": "ThingType.PRESSE_ABO"
    },
] + get_all_thing_mocks_by_type()
