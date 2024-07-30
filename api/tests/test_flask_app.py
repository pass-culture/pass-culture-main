import logging

from flask import url_for
import pytest
from werkzeug.routing import IntegerConverter
from werkzeug.routing import PathConverter
from werkzeug.routing import UnicodeConverter

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_log_request_details(client, caplog):
    users_factories.BeneficiaryGrant18Factory(email="email@example.com")
    client.with_token("email@example.com")

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
    "adage_iframe.create_adage_jwt_fake_token",
    "auth.discord_call_back",
    "auth.discord_signin",
    "native.native_v1.email_validation_remaining_resends",
    "native.native_v1.get_offer",  # → response.status_code = 404
    "native.native_v1.get_settings",
    "native.native_v1.get_subcategories_v2",
    "native.native_v1.get_venue",  # → response.status_code = 404
    "native.native_v1.google_oauth_state",
    "native.native_v1.similar_offers",
    "native.native_v2.get_offer_v2",  # → response.status_code = 404
    "Private API.testing_route_with_common_errors",
    "Private API.testing_route_with_validation_errors",
    "pro_private_api.check_activation_token_exists",  # → response.status_code = 404
    "pro_private_api.openapi_pro",
    "pro_private_api.validate_user",  # → response.status_code = 404
    "Public API.apple_app_site_association",
    "Public API.asset_links",
    "Public API.get_offers_by_tag",
    "Public API.health_api",
    "Public API.health_database",
    "Public API.list_educational_domains",
    "Public API.list_features",
    "Public API.openapi_apidoc",
    "Public API.send_storage_file",  # →  response.status_code = 404
    "Public API.sendinblue_notify_importcontacts",
    "saml_blueprint.on_educonnect_authentication_response",  # → response.status_code = 302
    "static",
    "test_blueprint.spectree_form_validation",
    "test_blueprint.spectree_get_test_endpoint",  # → response.status_code = 204
    "test_blueprint.spectree_post_test_endpoint",  # → response.status_code = 204
    "test_bookings_blueprint.spectree_get_booking_test_endpoint",  # → response.status_code = 204
    "test_bookings_blueprint.spectree_post_booking_test_endpoint",  # → response.status_code = 204
    "test_extended_spec_tree_blueprint.openapi_apidoc",
    "test_extended_spec_tree_blueprint.spectree_get_test_endpoint",
    "test_extended_spec_tree_blueprint.spectree_post_test_endpoint",
]

SUFFIX_WHITE_LIST = [
    "_swagger",
    "_redoc",
    "oauth2-redirect_html",
    "openapi_/",
    "openapi_/deprecated",
    "openapi_/event",
]


def test_endpoints_require_authentication(client, app):
    errors = []

    for rule in app.url_map._rules:
        if rule.endpoint in KNOWN_PUBLIC_ENDPOINTS:
            continue
        if any(rule.endpoint.endswith(suffix) for suffix in SUFFIX_WHITE_LIST):
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
            # TODO no more 403 should be allowed here
            if response.status_code not in (401, 400, 403):
                errors.append(
                    f"Endpoint '{rule.endpoint}' is publicly reachable with method {method.upper()} status: {response.status_code}. "
                    "Is this normal? If so add it to the endpoints whitelist in `tests.flask_app.KNOWN_PUBLIC_ENDPOINTS`."
                )
    assert len(errors) == 0, "\n".join(errors)
