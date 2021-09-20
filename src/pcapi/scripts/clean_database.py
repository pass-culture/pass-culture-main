from pprint import pprint
import traceback

from flask import Blueprint

from pcapi.repository.clean_database import clean_all_database


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command
def clean():
    try:
        clean_all_database()
    except Exception as e:  # pylint: disable=broad-except
        print("ERROR: " + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
