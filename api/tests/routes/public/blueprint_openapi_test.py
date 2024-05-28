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

    # To regenerate the expected JSON use the generate_openapi_json function
    expected = _get_expected_json()

    # Test paths key
    for _, path in enumerate(expected["paths"]):
        # Check path exists
        assert response.json["paths"][path] is not None

        for _, http_method in enumerate(expected["paths"][path]):
            # Check path http_method has not changed
            assert response.json["paths"][path][http_method] == expected["paths"][path][http_method]

    # Test other keys
    _assert_dicts_are_equal(response.json["components"], expected["components"], ["example"])
    assert response.json["info"] == expected["info"]
    assert response.json["tags"] == expected["tags"]
    assert response.json["servers"] == expected["servers"]
    assert response.json["openapi"] == expected["openapi"]
    assert response.json["security"] == expected["security"]


def _assert_dicts_are_equal(to_check, expected, keys_to_skip=None):
    keys_to_skip = keys_to_skip or []

    for _, key in enumerate(expected):
        # Check key exists
        assert key in to_check

        if isinstance(expected[key], dict):
            # Check value is also a dict
            assert isinstance(to_check[key], dict)

            # Check sub dict
            _assert_dicts_are_equal(to_check[key], expected[key], keys_to_skip)
        else:
            if key not in keys_to_skip:
                assert expected[key] == to_check[key]
