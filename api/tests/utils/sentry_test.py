import uuid
from unittest.mock import patch

import pytest
from pydantic.v1 import BaseModel

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.routes.apis import private_api
from pcapi.utils.sentry import SCRUBBED_INFO_PLACEHOLDER
from pcapi.utils.sentry import before_send
from pcapi.utils.sentry import before_send_transaction
from pcapi.utils.sentry import init_sentry_sdk


original_before_send = before_send

original_before_send_transaction = before_send_transaction


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


def before_send_transaction_wrapper(*args, **kwargs):
    """Wrapper around the `before_send_transaction` sentry hook to ensure
    it behaves as we want given different exceptions.
    """
    original_before_send_transaction(*args, **kwargs)


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


@patch("pcapi.utils.sentry.before_send")
@patch("uuid.uuid4", return_value=uuid.uuid4())
@patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
@pytest.mark.features(WIP_2025_AUTOLOGIN=True)
@pytest.mark.settings(IS_DEV=False)
@pytest.mark.usefixtures("db_session")
@pytest.mark.usefixtures("rsa_keys")
def test_remove_token_from_sentry_event_in_before_send(
    mocked_send_signup_email,
    mocked_uuid,
    mocked_before_send,
    rsa_keys,
    client,
    settings,
):
    mocked_before_send.side_effect = before_send_wrapper
    init_sentry_sdk()

    private_key_pem_file, public_key_pem_file = rsa_keys
    settings.PASSWORDLESS_LOGIN_PRIVATE_KEY = private_key_pem_file
    settings.PASSWORDLESS_LOGIN_PUBLIC_KEY = public_key_pem_file
    user_data = {
        "email": "pro@example.com",
        "firstName": "Toto",
        "lastName": "Pro",
        "password": "__v4l1d_P455sw0rd__",
        "contactOk": False,
        "token": "token",
        "phoneNumber": "0102030405",
    }
    client.post("/users/signup", json=user_data)

    args, _ = mocked_send_signup_email.call_args
    passwordless_login_token = args[1]

    client.patch(f"/users/validate_signup/{passwordless_login_token}")

    client.patch(f"/users/validate_signup/{passwordless_login_token}")
    assert (
        mocked_before_send.mock_calls[0]
        .args[0]["request"]["url"]
        .endswith("/users/validate_signup/" + SCRUBBED_INFO_PLACEHOLDER)
    )


@patch("pcapi.utils.sentry.before_send_transaction")
@patch("uuid.uuid4", return_value=uuid.uuid4())
@patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
@pytest.mark.features(WIP_2025_AUTOLOGIN=True)
@pytest.mark.settings(IS_DEV=False)
@pytest.mark.usefixtures("db_session")
@pytest.mark.usefixtures("rsa_keys")
def test_remove_token_from_sentry_event_in_before_send_transaction(
    mocked_send_signup_email,
    mocked_uuid,
    mocked_before_send_transaction,
    rsa_keys,
    client,
    settings,
):
    mocked_before_send_transaction.side_effect = before_send_transaction_wrapper
    init_sentry_sdk()

    private_key_pem_file, public_key_pem_file = rsa_keys
    settings.PASSWORDLESS_LOGIN_PRIVATE_KEY = private_key_pem_file
    settings.PASSWORDLESS_LOGIN_PUBLIC_KEY = public_key_pem_file
    user_data = {
        "email": "pro@example.com",
        "firstName": "Toto",
        "lastName": "Pro",
        "password": "__v4l1d_P455sw0rd__",
        "contactOk": False,
        "token": "token",
        "phoneNumber": "0102030405",
    }
    client.post("/users/signup", json=user_data)

    args, _ = mocked_send_signup_email.call_args
    passwordless_login_token = args[1]

    client.patch(f"/users/validate_signup/{passwordless_login_token}")

    client.patch("/offers/123")
    assert (
        mocked_before_send_transaction.mock_calls[1]
        .args[0]["request"]["url"]
        .endswith("/users/validate_signup/" + SCRUBBED_INFO_PLACEHOLDER)
    )
