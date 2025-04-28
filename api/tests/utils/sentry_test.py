from unittest.mock import patch

from pydantic.v1 import BaseModel
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.routes.apis import private_api
from pcapi.utils.sentry import before_send
from pcapi.utils.sentry import init_sentry_sdk


original_before_send = before_send


def before_send_wrapper(*args, **kwargs):
    """Wrapper around the `before_send` sentry hook to ensure
    it behaves as we want given different exceptions.
    """
    event = original_before_send(*args, **kwargs)
    assert not event.get("fingerprint")


def before_send_wrapper_with_custom_fingerprint(*args, **kwargs):
    """Wrapper around the `before_send` sentry hook to ensure
    it behaves as we want given specific exceptions.
    """
    event = original_before_send(*args, **kwargs)
    assert event["fingerprint"][0] == "{{ default }}"
    assert event["fingerprint"][1]


@private_api.route("/test/route", methods=["GET"])
def testing_route_with_common_errors(*args, **kwargs):
    """Route for test purpose that raise common exception
    with default fingerprint.
    """
    1 / 0


@private_api.route("/test/route-with-validation-error/<field_name>", methods=["GET"])
def testing_route_with_validation_errors(field_name, *args, **kwargs):
    """Route for test purpose that raise specific exception, ValidationError,
    which should be stamped with a custom fingerprint (content of exc.errors())
    """

    class TestSerializer(BaseModel):
        field_1: int
        field_2: int

    payload = {field_name: 0}
    TestSerializer(**payload)


@pytest.mark.settings(IS_DEV=False)
def test_init_sentry_sdk():
    # There is not much to test here, except that the call does not
    # fail.
    init_sentry_sdk()


@pytest.mark.usefixtures("db_session")
@patch("pcapi.utils.sentry.before_send")
@pytest.mark.settings(IS_DEV=False)
def test_common_errors_use_default_fingerprint(mocked_before_send, client):
    mocked_before_send.side_effect = before_send_wrapper

    init_sentry_sdk()

    pro = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
    client = client.with_session_auth(pro.email)

    client.get("/test/route")

    mocked_before_send.assert_called_once()


@pytest.mark.usefixtures("db_session")
@patch("pcapi.utils.sentry.before_send")
@pytest.mark.settings(IS_DEV=False)
def test_validation_erros_are_stamped_with_custom_fingerprint(mocked_before_send, client):
    mocked_before_send.side_effect = before_send_wrapper_with_custom_fingerprint

    init_sentry_sdk()

    pro = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
    client = client.with_session_auth(pro.email)

    client.get("/test/route-with-validation-error/field_2")

    mocked_before_send.assert_called_once()
