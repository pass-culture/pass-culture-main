import copy
import json
import logging

from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


NATIVE_API_OPENAPI_JSON_PATH = "./tests/files/native_openapi.json"


def _fetch_openapi_json() -> dict:
    """Get Open API json from flask server"""
    # to avoid circular import
    from pcapi.app import app

    client = app.test_client()
    r = client.get("/native/openapi.json")

    return copy.deepcopy(r.json)  # type: ignore[arg-type]


def _dump_openapi_json(json_dict: dict) -> None:
    with open(NATIVE_API_OPENAPI_JSON_PATH, "w", encoding="UTF-8") as f:
        json.dump(json_dict, f, indent=4, sort_keys=True)


@blueprint.cli.command("generate_native_api_openapi_json")
def generate_native_api_openapi_json() -> None:
    """
    Regenerate the expected_openapi.json used in the native_openapi_test
    """
    new_json = _fetch_openapi_json()

    _dump_openapi_json(new_json)
