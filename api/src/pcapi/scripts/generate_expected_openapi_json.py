import copy
import json
import logging

import click

from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


_EXPECTED_OPENAPI_JSON_PATH = "./tests/routes/public/expected_openapi.json"


def _get_existing_expected_openapi_json() -> dict:
    """Load existing Open API json from disk"""
    data = {}

    with open(_EXPECTED_OPENAPI_JSON_PATH, "r", encoding="UTF-8") as f:
        data = json.load(f)

    return data


def _fetch_openapi_json() -> dict:
    """Get Open API json from flask server"""
    # to avoid circular import
    from pcapi.app import app

    client = app.test_client()
    r = client.get("/openapi.json")

    return copy.deepcopy(r.json)  # type: ignore[arg-type]


def _update_with_existing_datetime_example(new_openapi_json: dict, old_openapi_json: dict) -> dict:
    old_schemas = old_openapi_json["components"]["schemas"]

    old_schemas_keys = set(old_openapi_json["components"]["schemas"].keys())
    new_schemas_keys = set(new_openapi_json["components"]["schemas"].keys())

    shared_keys = old_schemas_keys.intersection(new_schemas_keys)

    for schema_name in shared_keys:
        schema_properties = old_schemas[schema_name].get("properties", {})

        for _, property_name in enumerate(schema_properties):
            existing_example = schema_properties[property_name].get("example")
            property_format = schema_properties[property_name].get("format")

            if property_format == "date-time" and existing_example:
                new_openapi_json["components"]["schemas"][schema_name]["properties"][property_name][
                    "example"
                ] = existing_example

    return new_openapi_json


def _dump_openapi_json(json_dict: dict) -> None:
    with open(_EXPECTED_OPENAPI_JSON_PATH, "w", encoding="UTF-8") as f:
        json.dump(json_dict, f, indent=4, sort_keys=True)


@blueprint.cli.command("generate_expected_openapi_json")
@click.option("--skip-existing-datetime-examples", type=bool, required=False, default=True)
def generate_expected_openapi_json(skip_existing_datetime_examples: bool) -> None:
    """
    Regenerate the expected_openapi.json used in the blueprint_openapi_test

    :skip_existing_datetime_examples: if set to `True` the datetime examples are replaced by
                                      existing datetime examples to avoid updating `expected_openapi.json`
                                      with changes that are due to examples varying over time
    """
    new_json = _fetch_openapi_json()

    if skip_existing_datetime_examples:
        old_json = _get_existing_expected_openapi_json()
        _update_with_existing_datetime_example(new_json, old_json)

    _dump_openapi_json(new_json)
