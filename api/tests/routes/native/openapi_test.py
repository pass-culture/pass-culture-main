import json

from pcapi.scripts.generate_native_api_openapi_json import NATIVE_API_OPENAPI_JSON_PATH


def test_native_openapi_json(client):
    # To regenerate the expected JSON use the command `flask generate_native_api_openapi_json`
    with open(NATIVE_API_OPENAPI_JSON_PATH, "r", encoding="UTF-8") as f:
        expected_json = json.load(f)

    response = client.get("/native/openapi.json")
    assert response.status_code == 200
    actual_json = response.json

    _assert_paths_are_equal(actual_json, expected_json)
    _assert_components_are_equal(actual_json, expected_json)

    already_tested_keys = ["paths", "components"]
    keys_to_test = set([key for key in expected_json.keys() if key not in already_tested_keys])
    for key in keys_to_test:
        assert actual_json[key] == expected_json[key]


def _assert_paths_are_equal(actual_json: dict, expected_json: dict) -> None:
    expected_paths_dict = expected_json["paths"]
    actual_paths_dict = actual_json["paths"]
    assert set(actual_paths_dict.keys()) == set(expected_paths_dict.keys())

    for path in expected_paths_dict.keys():
        assert actual_paths_dict[path] == expected_paths_dict[path]


def _assert_components_are_equal(actual_json: dict, expected_json: dict) -> None:
    assert actual_json["components"]["securitySchemes"] == expected_json["components"]["securitySchemes"]

    expected_schemas_dict = expected_json["components"]["schemas"]
    actual_schemas_dict = actual_json["components"]["schemas"]
    assert set(actual_schemas_dict.keys()) == set(expected_schemas_dict.keys())

    for schema in expected_schemas_dict.keys():
        assert actual_schemas_dict[schema] == expected_schemas_dict[schema]
