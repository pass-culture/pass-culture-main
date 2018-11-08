from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing

def create_scratch_things():

    things_by_name = {}

    things_by_name['Ravage'] = create_thing(
        thing_name="Ravage",
        thing_type="ThingType.LIVRE_EDITION"
    )

    things_by_name['Ravage'] = create_thing(
        thing_name="Le Monde Diplomatique",
        thing_type="ThingType.PRESSE_ABO"
    )

    return things_by_name
