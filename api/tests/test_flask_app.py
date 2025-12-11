import logging

import pytest
from flask import url_for
from werkzeug.routing import IntegerConverter
from werkzeug.routing import PathConverter
from werkzeug.routing import UnicodeConverter

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_log_request_details(client, caplog):
    user = users_factories.BeneficiaryGrant18Factory(email="email@example.com")
    client.with_token(user)

    with caplog.at_level(logging.INFO):
        client.get(
            "/native/v1/me",
            headers={
                "device-id": "B35033A8-F7D9-4417-8A99-AC43F1ACC552",
                "request-id": "abcd",
                "X-Forwarded-For": "82.65.58.211, front1, front2",
                "app-version": "1.230.0",
                "code-push-id": "1234",
                "commit-hash": "abcefgh",
                "platform": "ios",
            },
        )
        assert caplog.records[0].extra["deviceId"] == "B35033A8-F7D9-4417-8A99-AC43F1ACC552"
        assert caplog.records[0].extra["requestId"] == "abcd"
        assert caplog.records[0].extra["sourceIp"] == "82.65.58.211"
        assert caplog.records[0].extra["route"] == "/native/v1/me"
        assert caplog.records[0].extra["path"] == "/native/v1/me"
        assert caplog.records[0].extra["appVersion"] == "1.230.0"
        assert caplog.records[0].extra["codePushId"] == "1234"
        assert caplog.records[0].extra["commitHash"] == "abcefgh"
        assert caplog.records[0].extra["platform"] == "ios"


KNOWN_PUBLIC_ENDPOINTS = [
    "adage_iframe.create_adage_jwt_fake_token",  # → response.status_code = 200
    "auth.discord_call_back",  # → response.status_code = 303
    "auth.discord_signin",  # → response.status_code = 200
    "auth.discord_success",  # → response.status_code = 303
    "native.native_v1.email_validation_remaining_resends",  # → response.status_code = 200
    "native.native_v1.empty_email_validation_remaining_resends",  # → response.status_code = 200
    "native.native_v1.get_artist",  # → response.status_code = 404
    "native.native_v1.get_categories",  # → response.status_code = 200
    "native.native_v1.get_movie_screenings_by_venue",  # → response.status_code = 200
    "native.native_v1.get_offer",  # → response.status_code = 404
    "native.native_v1.get_offerer_headline_offer",  # → response.status_code = 404
    "native.native_v1.get_settings",  # → response.status_code = 200
    "native.native_v1.get_subcategories_v2",  # → response.status_code = 200
    "native.native_v1.get_venue",  # → response.status_code = 404
    "native.native_v1.google_oauth_state",  # → response.status_code = 200
    "native.native_v1.offer_chronicles",  # → response.status_code = 404
    "native.native_v1.similar_offers",  # → response.status_code = 200
    "native.native_v2.get_offer_v2",  # → response.status_code = 404
    "native.native_v2.get_venue_v2",  # → response.status_code = 404
    "Private API.clear_email_list",  # → response.status_code = 200
    "Private API.testing_route_with_common_errors",
    "Private API.testing_route_with_validation_errors",
    "pro_private_api.check_activation_token_exists",  # → response.status_code = 404
    "Private API.connect_as",  # → response.status_code = 403
    "pro_private_api.openapi_pro",  # → response.status_code = 200
    "Private API.validate_user",  # → response.status_code = 404 (PATCH)
    "Public API.apple_app_site_association",  # → response.status_code = 200
    "Public API.asset_links",  # → response.status_code = 200
    "Public API.get_offers_by_tag",  # → response.status_code = 200
    "Public API.health_api",  # → response.status_code = 200
    "Public API.health_database",  # → response.status_code = 200
    "Public API.list_educational_domains",  # → response.status_code = 200
    "Public API.list_features",  # → response.status_code = 200
    "Public API.openapi_apidoc",  # → response.status_code = 200
    "Public API.send_storage_file",  # →  response.status_code = 404
    "Public API.sendinblue_notify_importcontacts",  # →  response.status_code = 204
    "Public API.brevo_get_user_recommendations",  # →  response.status_code = 200
    "public_api_deprecated.openapi_/deprecated_collective",  # → response.status_code = 200
    "saml_blueprint.on_educonnect_authentication_response",  # → response.status_code = 302
    "static",  # →  response.status_code = 404
    "test_blueprint.spectree_get_test_endpoint",  # → response.status_code = 204
    "test_blueprint.spectree_post_test_endpoint",  # → response.status_code = 204
    "test_bookings_blueprint.spectree_get_booking_test_endpoint",  # → response.status_code = 204
    "test_bookings_blueprint.spectree_post_booking_test_endpoint",  # → response.status_code = 204
    "test_extended_spec_tree_blueprint.spectree_inactive_ff_test_endpoint",  # → response.status_code = 404
    "test_extended_spec_tree_blueprint.spectree_active_ff_test_endpoint",  # → response.status_code = 204
    "test_blueprint.spectree_get_test_ff_inactive_endpoint",  # → response.status_code = 404
    "test_blueprint.spectree_get_test_ff_active_endpoint",  # → response.status_code = 204
    "test_extended_spec_tree_blueprint.openapi_apidoc",  # → response.status_code = 200
    "test_extended_spec_tree_blueprint.spectree_get_test_endpoint",  # → response.status_code = 204
    "test_extended_spec_tree_blueprint.spectree_post_test_endpoint",  # → response.status_code = 204
]

SUFFIX_WHITE_LIST = [
    # swagger, redoc and scalar are available through spectree
    "_swagger",
    "_redoc",
    "_scalar",
    "oauth2-redirect_html",
    "openapi_/",
    "openapi_/deprecated",
    "openapi_/event",
]

PREFIX_WHITE_LIST = [
    "Cloud task internal API",
]

IGNORE_ERROR_500_LIST = [
    "Private API.testing_route_with_common_errors",
    "Private API.testing_route_with_validation_errors",
]


IGNORE_LIST = [
    "Private API.get_unique_email",  # ignore this endpoint because it raises an 500 error and it slows down the test (up to 1min)
]


def test_endpoints_require_authentication(client, app):
    errors = []

    for rule in app.url_map._rules:
        if rule.endpoint in IGNORE_LIST:
            continue

        values = {}
        for argument_name, converter in rule._converters.items():
            if isinstance(converter, IntegerConverter):
                values[argument_name] = 1
            elif isinstance(converter, UnicodeConverter):
                values[argument_name] = "a1b2c3d4e"
            elif isinstance(converter, PathConverter):
                values[argument_name] = ""
        url = url_for(rule.endpoint, **values)

        for method in rule.methods:
            if method in ("OPTIONS", "HEAD"):
                continue
            response = client.open(url, method=method, json={})
            if response.status_code // 100 == 5 and rule.endpoint not in IGNORE_ERROR_500_LIST:
                errors.append(
                    f"Endpoint '{rule.endpoint}' returns a response with status code = {response.status_code}. Is this normal?"
                )
            elif (
                response.status_code not in (401, 400)
                and rule.endpoint not in KNOWN_PUBLIC_ENDPOINTS
                and not any(rule.endpoint.endswith(suffix) for suffix in SUFFIX_WHITE_LIST)
            ):
                errors.append(
                    f"Endpoint '{rule.endpoint}' is publicly reachable with method {method.upper()} status: {response.status_code}. "
                    "Is this normal? If so add it to the endpoints whitelist in `tests.flask_app.KNOWN_PUBLIC_ENDPOINTS`."
                )
    assert len(errors) == 0, f"Found {len(errors)} endpoint publicly reachable:\n" + "\n".join(errors)
