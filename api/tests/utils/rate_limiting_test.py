from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.utils import rate_limiting


@override_settings(
    RATE_LIMIT_BY_IP="2/minute",
    # Rate limiting is disabled by default when running tests, because
    # it makes an extra SQL query to fetch the `WIP_ENABLE_RATE_LIMITING`
    # feature flag.
    IS_RUNNING_TESTS=False,
)
def test_rate_limiting(app, client):
    @app.route("/")
    @rate_limiting.ip_rate_limiter()
    def func():
        return "hello"

    assert client.get("/").data == b"hello"
    assert client.get("/").data == b"hello"
    response = client.get("/")
    error = response.json["global"][0]
    assert error.startswith("Nombre de tentatives de connexion dépassé")
    assert response.status_code == 429

    with override_features(WIP_ENABLE_RATE_LIMITING=False):
        assert client.get("/").data == b"hello"
