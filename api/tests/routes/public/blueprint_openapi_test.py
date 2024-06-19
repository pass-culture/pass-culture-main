import copy
import json


def _get_expected_json():
    data = {}
    with open("./tests/routes/public/expected_openapi.json", "r", encoding="UTF-8") as f:
        data = json.load(f)

    return data


def test_redirect_to_new_swagger(client, app):
    response_collective = client.get("/v2/swagger")
    assert response_collective.status_code == 301
    assert response_collective.location == "http://localhost/swagger"

    response_product = client.get("/public/offers/v1/swagger")
    assert response_product.status_code == 301
    assert response_product.location == "http://localhost/swagger"

    response_event = client.get("/public/offers/v1/event/swagger")
    assert response_event.status_code == 301
    assert response_event.location == "http://localhost/swagger"

    response_booking = client.get("/public/bookings/v1/swagger")
    assert response_booking.status_code == 301
    assert response_booking.location == "http://localhost/swagger"


def test_public_api_openapi_json(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200

    # JSON to be tested
    response_json = copy.deepcopy(response.json)

    # To regenerate the expected JSON use the command `flask generate_expected_openapi_json` (in `/usr/src/app/`)
    expected = _get_expected_json()

    # Test paths key (assertions are split for better error readability)
    # Step 1 : Test sub keys are the same
    expected_paths_sub_keys = set(expected["paths"].keys())
    response_paths_sub_keys = set(response_json["paths"].keys())

    assert response_paths_sub_keys == expected_paths_sub_keys

    # Step 2 : Test sub keys contents are equal
    for path in expected_paths_sub_keys:
        assert response_json["paths"][path] == expected["paths"][path]

    # Drop datetime examples (because they vary over time)
    _drop_openapi_datetime_examples(response_json)
    _drop_openapi_datetime_examples(expected)

    # Test components keys
    # -- Tests components.securitySchemes
    assert response_json["components"]["securitySchemes"] == expected["components"]["securitySchemes"]
    # -- Tests components.schemas (assertions are split for better error readability)
    # -- Step 1 : Test sub keys are the same
    expected_schemas_sub_keys = set(expected["components"]["schemas"].keys())
    response_schemas_sub_keys = set(response_json["components"]["schemas"].keys())

    assert response_schemas_sub_keys == expected_schemas_sub_keys

    # -- Step 2 : Test sub keys contents are equal
    for schema in expected_schemas_sub_keys:
        assert response_json["components"]["schemas"][schema] == expected["components"]["schemas"][schema]

    # Test other keys
    assert response_json["info"] == expected["info"]
    assert response_json["tags"] == expected["tags"]
    assert response_json["servers"] == expected["servers"]
    assert response_json["openapi"] == expected["openapi"]
    assert response_json["security"] == expected["security"]


def _drop_openapi_datetime_examples(openapi_json_dict: dict) -> dict:
    schemas = openapi_json_dict["components"]["schemas"]

    for _, schema_name in enumerate(schemas):
        schema_properties = schemas[schema_name].get("properties", {})

        for _, property_name in enumerate(schema_properties):
            if schema_properties[property_name].get("format") == "date-time":
                openapi_json_dict["components"]["schemas"][schema_name]["properties"][property_name].pop(
                    "example", None
                )

    return openapi_json_dict
