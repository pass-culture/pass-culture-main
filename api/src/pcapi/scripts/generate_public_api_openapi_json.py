import copy
import json
import logging

from flask import current_app as app

from pcapi.core.users.sessions import install_routed_login
from pcapi.routes import install_all_routes
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


_PUBLIC_API_OPENAPI_JSON_PATH = "./documentation/static/openapi.json"


def _fetch_openapi_json() -> dict:
    """Get Open API json from flask server"""
    install_all_routes(app)
    install_routed_login()

    client = app.test_client()
    r = client.get("/openapi.json")

    return copy.deepcopy(r.json)  # type: ignore[arg-type]


def _dump_openapi_json(json_dict: dict) -> None:
    with open(_PUBLIC_API_OPENAPI_JSON_PATH, "w", encoding="UTF-8") as f:
        json.dump(json_dict, f, indent=4, sort_keys=True)


@blueprint.cli.command("generate_public_api_openapi_json")
def generate_public_api_openapi_json() -> None:
    """
    Regenerate the expected_openapi.json used in the blueprint_openapi_test
    """
    new_json = _fetch_openapi_json()

    _dump_openapi_json(new_json)
