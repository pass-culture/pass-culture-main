from pprint import pprint
import traceback

import click
from flask import Blueprint

from pcapi.sandboxes.scripts.save_sandbox import save_sandbox
from pcapi.sandboxes.scripts.testcafe_helpers import print_all_testcafe_helpers
from pcapi.sandboxes.scripts.testcafe_helpers import print_testcafe_helper
from pcapi.sandboxes.scripts.testcafe_helpers import print_testcafe_helpers


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("sandbox")
@click.option("-n", "--name", help="Sandbox name", default="classic")
@click.option("-c", "--clean", help="Clean database first", default="true")
def sandbox(name, clean):
    with_clean = clean == "true"
    save_sandbox(name, with_clean)


@blueprint.cli.command("sandbox_to_testcafe")
@click.option("-n", "--name", help="Sandboxes getters module name", default=None)
@click.option("-g", "--getter", help="Sandboxes getters function name", default=None)
def sandbox_to_testcafe(name, getter):
    try:
        if name is None:
            print_all_testcafe_helpers()
        elif getter is None:
            print_testcafe_helpers(name)
        else:
            print_testcafe_helper(name, getter)
    except Exception as e:  # pylint: disable=broad-except
        print("ERROR: " + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
