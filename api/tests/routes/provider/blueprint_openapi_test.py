import copy
import json


def _get_expected_json():
    data = {}
    with open("./documentation/static/openapi.json", "r", encoding="UTF-8") as f:
        data = json.load(f)

    return data


def test_public_api_openapi_json(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200

    # JSON to be tested
    response_json = copy.deepcopy(response.json)

    # To regenerate the expected JSON use the command `flask generate_public_api_openapi_json` (in `/usr/src/app/`)
    # (if you are using docker, the command is `pc generate_public_api_openapi_json`)
    expected = _get_expected_json()

    # Test paths key (assertions are split for better error readability)
    # Step 1 : Test sub keys are the same
    expected_paths_sub_keys = set(expected["paths"].keys())
    response_paths_sub_keys = set(response_json["paths"].keys())

    assert response_paths_sub_keys == expected_paths_sub_keys

    # Step 2 : Test sub keys contents are equal
    for path in expected_paths_sub_keys:
        assert response_json["paths"][path] == expected["paths"][path]

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
