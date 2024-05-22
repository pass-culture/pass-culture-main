import json

from pcapi.app import app


def generate_expected_openapi_json():
    """
    Regenerate the expected_openapi.json used in the blueprint_openapi_test
    """
    client = app.test_client()
    r = client.get("/openapi.json")

    with open("tests/routes/public/expected_openapi.json", "w", encoding="UTF-8") as f:
        json.dump(r.json, f, indent=4, sort_keys=True)
