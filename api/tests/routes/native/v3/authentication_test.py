import datetime
import json
import logging
import secrets
import time
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.core.history import factories as history_factories
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")
SESSION_KEY_PATTERN = "pcapi:token:native_auth_session:%s"
USER_BAN_REDIS_KEY = "native:user:authantication_forbidden:%s"
DEVICE_INFO = {
    "os": "iOS",
    "device_id": "ID",
    "source": "app",
}


def _check_mfa_offer(mfa_offer: dict, endpoint: str, name: str) -> str:
    assert mfa_offer["type"] == name
    token = mfa_offer["endpoint"].split("/")[-1]
    assert "/".join(mfa_offer["endpoint"].split("/")[:-1]) == endpoint
    return token


class SigninTest:
    url = "/native/v3/signin"
    device_info = {
        "os": "iOS",
        "deviceId": "ID",
        "source": "app",
    }

    def test_account_is_active_account_state(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        response = client.post(self.url, json=data)
        assert response.status_code == 200

        assert response.json["expiration"] in (int(time.time()) + 900, int(time.time()) + 899)
        assert len(response.json.get("mfaOffers")) == 1
        token = _check_mfa_offer(response.json["mfaOffers"][0], endpoint="/native/v3/otp_mail", name="OTP_MAIL")

        assert clear_redis.ttl(SESSION_KEY_PATTERN % token) in (899, 900)
        session = json.loads(clear_redis.get(SESSION_KEY_PATTERN % token))
        assert session["user_id"] == user.id
        assert session["expiration"] == response.json["expiration"]
        assert set(session["available_second_factor"]) == set(o["type"] for o in response.json["mfaOffers"])
        assert session["current_step"] is None
        assert session["device_info"] == DEVICE_INFO

    def test_account_anonymized_user_request_blocked(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.AnonymizedUserFactory(
            email=data["identifier"],
            password=data["password"],
        )
        response = client.post(self.url, json=data)

        assert response.status_code == 401
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    def test_account_deleted_account_blocked(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = client.post(self.url, json=data)
        assert response.status_code == 401
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    def test_account_suspended_upon_user_request_can_continue(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        response = client.post(self.url, json=data)
        assert response.status_code == 200

    def test_account_suspended_by_user_for_suspicious_login_can_continue(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        )

        response = client.post(self.url, json=data)
        assert response.status_code == 200

    def test_account_suspended_by_user_for_anonymization_can_continue(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.WAITING_FOR_ANONYMIZATION
        )

        response = client.post(self.url, json=data)
        assert response.status_code == 200

    def test_allow_inactive_user_sign(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=False)

        response = client.post(self.url, json=data)
        assert response.status_code == 200

    def test_user_logs_in_with_wrong_password(self, client, caplog, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        # signin with invalid password and ensures the result messsage is generic
        data["password"] = data["password"][:-2]
        with caplog.at_level(logging.INFO):
            response = client.post(self.url, json=data)
        assert response.status_code == 401
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert "Failed authentication attempt" in caplog.messages
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    def test_unknown_user_logs_in(self, client, caplog, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }

        # signin with invalid password and ensures the result messsage is generic
        with caplog.at_level(logging.INFO):
            response = client.post(self.url, json=data)
        assert response.status_code == 401
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert "Failed authentication attempt" in caplog.messages
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    def test_user_without_password_logs_in(self, client, caplog, clear_redis):
        user = users_factories.UserFactory(password=None, isActive=True)

        response = client.post(
            self.url,
            json={
                "identifier": user.email,
                "password": settings.TEST_DEFAULT_PASSWORD,
                "device_info": self.device_info,
            },
        )

        assert response.status_code == 401
        # generic message to prevent enumeration attack
        assert response.json == {"general": ["Identifiant ou Mot de passe incorrect"]}
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    def test_user_logs_in_with_missing_fields(self, client, clear_redis):
        response = client.post(self.url, json={})
        assert response.status_code == 400
        assert response.json == {
            "identifier": ["Ce champ est obligatoire"],
            "password": ["Ce champ est obligatoire"],
            "deviceInfo": ["Ce champ est obligatoire"],
        }
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    @pytest.mark.settings(RECAPTCHA_IGNORE_VALIDATION=0)
    @pytest.mark.features(ENABLE_NATIVE_APP_RECAPTCHA=False)
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def should_not_check_recaptcha_when_feature_flag_is_disabled(
        self, mocked_recaptcha_validation, client, clear_redis
    ):
        mocked_recaptcha_validation.return_value = {"success": False, "error-codes": []}
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "invalid_token",
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post(self.url, json=data)

        assert response.status_code == 200

    @pytest.mark.settings(RECAPTCHA_IGNORE_VALIDATION=0)
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    @pytest.mark.parametrize("error", ["invalid-input-response", "timeout-or-duplicate"])
    def test_fail_when_recaptcha_token_is_invalid(self, mocked_recaptcha_validation, error, client, clear_redis):
        mocked_recaptcha_validation.return_value = {"success": False, "error-codes": [error]}
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "invalid_token",
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post(self.url, json=data)

        assert response.status_code == 401
        assert response.json == {"token": "Le token est invalide"}
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    @pytest.mark.settings(RECAPTCHA_IGNORE_VALIDATION=0)
    def test_fail_when_recaptcha_token_is_missing(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post(self.url, json=data)

        assert response.status_code == 401
        assert response.json == {"token": "Le token est invalide"}
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_success_when_recaptcha_token_is_valid(self, mocked_check_recaptcha_token_is_valid, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "token": "valid_token",
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"])

        response = client.post(self.url, json=data)

        mocked_check_recaptcha_token_is_valid.assert_called()
        assert response.status_code == 200

    def test_fail_when_missing_device_info(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        response = client.post(self.url, json=data)
        assert response.status_code == 400
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "deviceInfo": {
                "os": "Windows XP",
                "source": "app",
            },
        }
        response = client.post(self.url, json=data)
        assert response.status_code == 400
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    def test_fail_when_extra_device_info(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "deviceInfo": {
                "os": "Windows XP",
                "deviceId": "ID",
                "source": "app",
                "fontScale": -1,
                "resolution": "750x1334",
                "screenZoomLevel": None,
            },
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        response = client.post(self.url, json=data)
        assert response.status_code == 400
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []

    def test_user_is_blocked(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        user = users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)
        clear_redis.set(USER_BAN_REDIS_KEY % user.id, "1")

        response = client.post(self.url, json=data)
        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []


class OtpMfaHelper:
    url = "/native/v3/otp_mail/%s"
    default_token = secrets.token_urlsafe(64)  # reuse the same token for all tests and avoir security warning

    def _generate_session(self, user_id, redis, second_factor=None, current_step=None):
        redis.set(
            SESSION_KEY_PATTERN % self.default_token,
            json.dumps(
                {
                    "user_id": user_id,
                    "expiration": (int(time.time()) + 900),
                    "available_second_factor": second_factor if second_factor is not None else ["OTP_MAIL"],
                    "current_step": current_step,
                    "device_info": DEVICE_INFO,
                },
            ),
            ex=123,
        )


class GetOtpMailTest(OtpMfaHelper):
    def test_nominal(self, client, clear_redis):
        user = users_factories.UserFactory()
        self._generate_session(user.id, redis=clear_redis)

        response = client.get(self.url % self.default_token)
        assert response.status_code == 200

        response_endpoint = "/".join(response.json["responseEndpoint"].split("/")[:-1])
        token = response.json["responseEndpoint"].split("/")[-1]
        assert response.json["newEmailSent"] == True
        assert response.json["expiration"] >= (time.time() + 899)
        assert response.json["expiration"] <= (time.time() + 900)
        assert response.json["renewalEmail"] >= (time.time() + 59)
        assert response.json["renewalEmail"] <= (time.time() + 60)
        assert response.json["retryLeft"] == 3
        assert response.json["charCount"] == 6
        assert response_endpoint == "/native/v3/otp_mail"

        session = json.loads(clear_redis.get(SESSION_KEY_PATTERN % token))
        assert session["user_id"] == user.id
        assert session["expiration"] == response.json["expiration"]
        assert session["available_second_factor"] == ["OTP_MAIL"]
        assert session["device_info"] == DEVICE_INFO
        assert session["current_step"]["otp"]
        assert session["current_step"]["renewal_email"] == response.json["renewalEmail"]
        assert session["current_step"]["retry_left"] == response.json["retryLeft"]

    def test_new_otp(self, client, clear_redis):
        user = users_factories.UserFactory()
        self._generate_session(
            user.id,
            redis=clear_redis,
            current_step={"otp": "AZERTY", "renewal_email": int(time.time()), "retry_left": 1},
        )

        response = client.get(self.url % self.default_token)
        assert response.status_code == 200

        response_endpoint = "/".join(response.json["responseEndpoint"].split("/")[:-1])
        token = response.json["responseEndpoint"].split("/")[-1]
        assert response.json["newEmailSent"] == True
        assert response.json["expiration"] >= (time.time() + 899)
        assert response.json["expiration"] <= (time.time() + 900)
        assert response.json["renewalEmail"] >= (time.time() + 59)
        assert response.json["renewalEmail"] <= (time.time() + 60)
        assert response.json["retryLeft"] == 1
        assert response.json["charCount"] == 6
        assert response_endpoint == "/native/v3/otp_mail"

        session = json.loads(clear_redis.get(SESSION_KEY_PATTERN % token))
        assert session["user_id"] == user.id
        assert session["expiration"] == response.json["expiration"]
        assert session["available_second_factor"] == ["OTP_MAIL"]
        assert session["device_info"] == DEVICE_INFO
        assert session["current_step"]["otp"]
        assert session["current_step"]["renewal_email"] == response.json["renewalEmail"]
        assert session["current_step"]["retry_left"] == response.json["retryLeft"]

    def test_new_otp_too_early(self, client, clear_redis):
        user = users_factories.UserFactory()
        self._generate_session(
            user.id,
            redis=clear_redis,
            current_step={
                "otp": "AZERTY",
                "renewal_email": 4102441200,  #  01/01/2100
                "retry_left": 1,
            },
        )

        response = client.get(self.url % self.default_token)

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.ttl(USER_BAN_REDIS_KEY % user.id) in (3599, 3600)

    def test_invalid_session(self, client, clear_redis):
        response = client.get(self.url % self.default_token)

        assert response.status_code == 401
        assert clear_redis.keys("*") == []

    def test_user_blocked(self, client, clear_redis):
        user = users_factories.UserFactory()
        self._generate_session(user.id, redis=clear_redis)
        clear_redis.set(USER_BAN_REDIS_KEY % user.id, "1", ex=250)

        response = client.get(self.url % self.default_token)

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.ttl(USER_BAN_REDIS_KEY % user.id) in (249, 250)

    def test_invalid_second_factor(self, client, clear_redis):
        user = users_factories.UserFactory()
        self._generate_session(user.id, redis=clear_redis, second_factor=[])

        response = client.get(self.url % self.default_token)
        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.exists(USER_BAN_REDIS_KEY % user.id)


class PostOtpMailTest(OtpMfaHelper):
    def test_success(self, client, clear_redis):
        user = users_factories.UserFactory(
            isActive=True,
            lastConnectionDate=datetime.datetime(2020, 1, 1),
        )
        self._generate_session(
            user.id,
            redis=clear_redis,
            current_step={"otp": "AZERTY", "renewal_email": int(time.time()) + 20, "retry_left": 1},
        )

        response = client.post(self.url % self.default_token, json={"response": "AZERTY"})
        db.session.refresh(user)

        assert response.status_code == 200
        assert response.json["charCount"] == 0
        assert response.json["expiration"] == 0
        assert response.json["renewalEmail"] == 0
        assert response.json["responseEndpoint"] == ""
        assert response.json["retryLeft"] == 0
        assert response.json["sessionTokens"]["accountState"] == "ACTIVE"
        assert response.json["sessionTokens"]["accessToken"]
        assert response.json["sessionTokens"]["refreshToken"]

        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.keys(USER_BAN_REDIS_KEY % "*") == []

        db.session.query(users_models.TrustedDevice).filter(
            users_models.TrustedDevice.deviceId == DEVICE_INFO["device_id"]
        ).count() == 1
        assert user.lastConnectionDate.year > 2025

        # TODO check state in db

    def test_wrong_otp(self, client, clear_redis):
        user = users_factories.UserFactory(isActive=True)
        self._generate_session(
            user.id,
            redis=clear_redis,
            current_step={"otp": "AZERTY", "renewal_email": int(time.time()) + 20, "retry_left": 3},
        )

        response = client.post(self.url % self.default_token, json={"response": "FALSE2"})
        assert response.status_code == 200

        assert response.json["charCount"] == 6
        assert response.json["expiration"] >= (time.time() + 899)
        assert response.json["expiration"] <= (time.time() + 900)
        assert response.json["renewalEmail"] >= (time.time() + 19)
        assert response.json["renewalEmail"] <= (time.time() + 20)
        assert "/".join(response.json["responseEndpoint"].split("/")[:-1]) == "/native/v3/otp_mail"
        assert response.json["retryLeft"] == 2
        assert not response.json["sessionTokens"]

        token = response.json["responseEndpoint"].split("/")[-1]
        session = json.loads(clear_redis.get(SESSION_KEY_PATTERN % token))

        assert session["user_id"] == user.id
        assert session["expiration"] == response.json["expiration"]
        assert session["available_second_factor"] == ["OTP_MAIL"]
        assert session["current_step"] == {
            "otp": "AZERTY",
            "renewal_email": response.json["renewalEmail"],
            "retry_left": response.json["retryLeft"],
        }
        assert clear_redis.keys(USER_BAN_REDIS_KEY % "*") == []

    def test_wrong_otp_no_retry(self, client, clear_redis):
        user = users_factories.UserFactory(isActive=True)
        self._generate_session(
            user.id,
            redis=clear_redis,
            current_step={"otp": "AZERTY", "renewal_email": int(time.time()) + 20, "retry_left": 1},
        )

        response = client.post(self.url % self.default_token, json={"response": "FALSE2"})

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.exists(USER_BAN_REDIS_KEY % user.id)

    def test_invalid_token(self, client, clear_redis):
        response = client.post(self.url % self.default_token, json={"response": "FALSE2"})

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.keys(USER_BAN_REDIS_KEY % "*") == []

    def test_user_blocked(self, client, clear_redis):
        user = users_factories.UserFactory(isActive=True)
        self._generate_session(
            user.id,
            redis=clear_redis,
            current_step={"otp": "AZERTY", "renewal_email": int(time.time()) + 20, "retry_left": 3},
        )
        clear_redis.set(USER_BAN_REDIS_KEY % user.id, "1", ex=12)

        response = client.post(self.url % self.default_token, json={"response": "AZERTY"})

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.exists(USER_BAN_REDIS_KEY % user.id)

    def test_invalid_second_factor(self, client, clear_redis):
        user = users_factories.UserFactory(isActive=True)
        self._generate_session(user.id, redis=clear_redis, second_factor=[])

        response = client.post(self.url % self.default_token, json={"response": "AZERTY"})

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.exists(USER_BAN_REDIS_KEY % user.id)

    def test_never_called_get(self, client, clear_redis):
        user = users_factories.UserFactory(isActive=True)
        self._generate_session(
            user.id,
            redis=clear_redis,
        )

        response = client.post(self.url % self.default_token, json={"response": "AZERTY"})

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.exists(USER_BAN_REDIS_KEY % user.id)

    def test_user_deleted(self, client, clear_redis):
        self._generate_session(
            0,
            redis=clear_redis,
            current_step={"otp": "AZERTY", "renewal_email": int(time.time()) + 20, "retry_left": 3},
        )

        response = client.post(self.url % self.default_token, json={"response": "AZERTY"})

        assert response.status_code == 401
        assert clear_redis.keys(SESSION_KEY_PATTERN % "*") == []
        assert clear_redis.keys(USER_BAN_REDIS_KEY % "*") == []


class ScenarioTest:
    """
    Test full authentication scenario with multiple factors
    """

    device_info = {
        "os": "iOS",
        "deviceId": "ID",
        "source": "app",
    }

    def test_mail_otp(self, client, clear_redis):
        data = {
            "identifier": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "device_info": self.device_info,
        }
        users_factories.UserFactory(email=data["identifier"], password=data["password"], isActive=True)

        # first factor: login + password
        response = client.post("/native/v3/signin", json=data)
        assert response.status_code == 200

        next_step_url = [o["endpoint"] for o in response.json["mfaOffers"] if o["type"] == "OTP_MAIL"][0]
        # generate OTP  + send email
        response = client.get(next_step_url)
        assert response.status_code == 200
        assert response.json["retryLeft"] == 3

        # send wrong answer
        response = client.post(response.json["responseEndpoint"], json={"response": "++++++"})
        assert response.status_code == 200
        assert response.json["retryLeft"] == 2
        assert not response.json["sessionTokens"]

        token = response.json["responseEndpoint"].split("/")[-1]
        session = json.loads(clear_redis.get(SESSION_KEY_PATTERN % token))
        otp = session["current_step"]["otp"]
        # send good answer
        response = client.post(response.json["responseEndpoint"], json={"response": otp})
        assert response.status_code == 200

        assert response.json["responseEndpoint"] == ""  # no next step
        assert response.json["sessionTokens"]["accountState"] == "ACTIVE"
        assert response.json["sessionTokens"]["accessToken"]
        assert response.json["sessionTokens"]["refreshToken"]
