from pprint import pprint
import traceback

from pcapi.repository.clean_database import clean_all_database
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("clean_database")
def clean():
    try:
        clean_all_database()
    except Exception as e:  # pylint: disable=broad-except
        print("ERROR: " + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
