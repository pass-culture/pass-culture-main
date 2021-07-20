import itertools
from urllib.parse import urlsplit

import dotenv
from flask import Flask
from flask_cors import CORS
import pytest

from tests.conftest import TestClient


def get_cors_allowed_origins(env, settings_key):
    dotenv_file = dotenv.find_dotenv(f".env.{env}")
    return dotenv.dotenv_values(dotenv_file)[settings_key].split(",")


def build_permutations(request_origins):
    """
    Creates permutations, which are urls that are similar to allowed origins but try to circumvent CORS settings
    Read https://www.bedefended.com/papers/cors-security-guide section 3.4.6 for more background
    """
    permutations = []
    for origin in request_origins:
        base_url = "{0.scheme}://{0.netloc}".format(urlsplit(origin))
        bypass = ["", "-", '"', "{", "}", "+", "_", "^", "%60", "!", "~", "`", ";", "|", "&", "'", "(", ")", "*", ",",
                  "$", "=", "+", "%0b"]  # fmt: skip
        domains = ["https://localhost", "http://localhost", base_url]
        permutations = [base_url + "evil.com", base_url + "evil.com"]
        for r in itertools.product(domains, bypass):
            attempt = r[0] + r[1] + ".evil.com"
            permutations.append(attempt)
        permutations.append("null")
    return permutations


TESTING_ALLOWED_ORIGINS = (
    "https://pro.testing.passculture.team",
    "https://web.testing.passculture.team",
    "https://app.passculture-testing.beta.gouv.fr",
    "https://pro.passculture-testing.beta.gouv.fr",
)
STAGING_ALLOWED_ORIGINS = (
    "https://web.staging.passculture.team",
    "https://pro.staging.passculture.team",
    "https://app.passculture-staging.beta.gouv.fr",
    "https://pro.passculture-staging.beta.gouv.fr",
)
PRODUCTION_ALLOWED_ORIGINS = (
    "https://web.passculture.app",
    "https://passculture.pro",
    "https://app.passculture.beta.gouv.fr",
    "https://pro.passculture.beta.gouv.fr",
)
INTEGRATION_ALLOWED_ORIGINS = (
    "https://web.integration.passculture.app",
    "https://integration.passculture.app",
    "https://integration.passculture.pro",
    "https://app.passculture-integration.beta.gouv.fr",
    "https://pro.passculture-integration.beta.gouv.fr",
)

TESTING_ALLOWED_ORIGINS_NATIVE = ("https://app.testing.passculture.team",)
STAGING_ALLOWED_ORIGINS_NATIVE = ("https://app.staging.passculture.team",)
PRODUCTION_ALLOWED_ORIGINS_NATIVE = ("https://passculture.app",)


def create_app(test_data, settings_key):
    """Create a new app from scratch to re-define CORS"""
    app = Flask(__name__)

    @app.route("/simple", methods=["GET"])
    def index():
        return "Hello, World"

    CORS(
        app,
        origins=get_cors_allowed_origins(test_data["env"], settings_key),
        supports_credentials=True,
    )
    return app


@pytest.mark.parametrize(
    "test_data",
    [
        {"env": "production", "allowed_origins": PRODUCTION_ALLOWED_ORIGINS},
        {"env": "staging", "allowed_origins": STAGING_ALLOWED_ORIGINS},
        {"env": "testing", "allowed_origins": TESTING_ALLOWED_ORIGINS},
        {"env": "integration", "allowed_origins": INTEGRATION_ALLOWED_ORIGINS},
    ],
    ids=["PROD", "STAGING", "TESTING", "INTEGRATION"],
)
class CorsConfigPrivateApiTest:
    def test_allowed_origins(self, test_data):
        app = create_app(test_data, "CORS_ALLOWED_ORIGINS")
        for origin in test_data["allowed_origins"]:
            CORS(
                app,
                origins=get_cors_allowed_origins(test_data["env"], "CORS_ALLOWED_ORIGINS"),
                supports_credentials=True,
            )
            TestClient.LOCAL_ORIGIN_HEADERS["origin"] = origin
            client = TestClient(app.test_client())
            response = client.get("/simple")
            assert response.headers.get("Access-Control-Allow-Origin") == TestClient.LOCAL_ORIGIN_HEADERS["origin"]

    def test_not_allowed_origins(self, test_data):
        for _origin in test_data["allowed_origins"]:
            app = create_app(test_data, "CORS_ALLOWED_ORIGINS")
            CORS(
                app,
                origins=get_cors_allowed_origins(test_data["env"], "CORS_ALLOWED_ORIGINS"),
                supports_credentials=True,
            )
            for permutation in build_permutations(test_data["allowed_origins"]):
                TestClient.LOCAL_ORIGIN_HEADERS["origin"] = permutation
                client = TestClient(app.test_client())
                response = client.get("/simple")
                assert not response.headers.get("Access-Control-Allow-Origin")


@pytest.mark.parametrize(
    "test_data",
    [
        {"env": "production", "allowed_origins_native": PRODUCTION_ALLOWED_ORIGINS_NATIVE},
        {"env": "staging", "allowed_origins_native": STAGING_ALLOWED_ORIGINS_NATIVE},
        {"env": "testing", "allowed_origins_native": TESTING_ALLOWED_ORIGINS_NATIVE},
    ],
    ids=["PROD", "STAGING", "TESTING"],
)
class CorsConfigNativeTest:
    def test_allowed_origins_native(self, test_data):
        app = create_app(test_data, "CORS_ALLOWED_ORIGINS_NATIVE")
        for origin in test_data["allowed_origins_native"]:
            CORS(
                app,
                origins=get_cors_allowed_origins(test_data["env"], "CORS_ALLOWED_ORIGINS_NATIVE"),
                supports_credentials=True,
            )
            TestClient.LOCAL_ORIGIN_HEADERS["origin"] = origin
            client = TestClient(app.test_client())
            response = client.get("/simple")
            assert response.headers.get("Access-Control-Allow-Origin") == TestClient.LOCAL_ORIGIN_HEADERS["origin"]

    def test_not_allowed_origins_native(self, test_data):
        for _origin in test_data["allowed_origins_native"]:
            app = create_app(test_data, "CORS_ALLOWED_ORIGINS_NATIVE")
            CORS(
                app,
                origins=get_cors_allowed_origins(test_data["env"], "CORS_ALLOWED_ORIGINS_NATIVE"),
                supports_credentials=True,
            )
            for permutation in build_permutations(test_data["allowed_origins_native"]):
                TestClient.LOCAL_ORIGIN_HEADERS["origin"] = permutation
                client = TestClient(app.test_client())
                response = client.get("/simple")
                assert not response.headers.get("Access-Control-Allow-Origin")
