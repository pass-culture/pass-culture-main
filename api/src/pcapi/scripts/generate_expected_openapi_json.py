import json
import logging

from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("generate_expected_openapi_json")
def generate_expected_openapi_json() -> None:
    """
    Regenerate the expected_openapi.json used in the blueprint_openapi_test
    """
    # to avoid circular import
    from pcapi.app import app

    client = app.test_client()
    r = client.get("/openapi.json")

    json_dict = r.json

    with open("tests/routes/public/expected_openapi.json", "w", encoding="UTF-8") as f:
        json.dump(json_dict, f, indent=4, sort_keys=True)
