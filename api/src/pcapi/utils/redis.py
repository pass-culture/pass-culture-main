import typing

import redis
from flask import current_app
from google import auth
from google.auth.transport import requests as google_auth_request
from google.cloud import iam_credentials_v1
from pydantic import RedisDsn

from pcapi import settings


class GoogleTokenProvider(redis.CredentialProvider):
    _gcp_service_account: str

    @property
    def gcp_service_account(self) -> str:
        if not getattr(self, "_gcp_service_account", False):
            credentials, _ = auth.default()
            email = credentials.service_account_email  # type: ignore [attr-defined]
            # if default SA has not been refreshed its email is 'default'
            if email.lower() == "default":
                credentials.refresh(request=google_auth_request.Request())
                email = credentials.service_account_email  # type: ignore [attr-defined]
            self._gcp_service_account = f"projects/-/serviceAccounts/{email}"
        return self._gcp_service_account

    # Generated IAM tokens are valid for 15 minutes
    def get_credentials(self) -> tuple[str, str]:
        """
        Derived from documentation
        https://docs.cloud.google.com/memorystore/docs/valkey/client-library-code-samples#iam_auth_and_in_transit_encryption
        """
        client = iam_credentials_v1.IAMCredentialsClient()
        request = iam_credentials_v1.GenerateAccessTokenRequest(
            name=self.gcp_service_account,
            scope=["https://www.googleapis.com/auth/cloud-platform"],
        )
        response = client.generate_access_token(request=request)
        return "default", response.access_token


def get_redis_client() -> "redis.Redis[str]":
    # set in connect_redis
    return current_app.redis_client  # type: ignore [attr-defined]


def connect_redis() -> None:
    parsed_redis = RedisDsn(settings.REDIS_URL)

    redis_dict: dict[str, typing.Any] = {
        "host": parsed_redis.host,
        "port": parsed_redis.port,
        "decode_responses": True,
    }

    if parsed_redis.path and len(parsed_redis.path) > 1:
        redis_dict["db"] = int(parsed_redis.path[1:])

    if settings.GCP_REDIS_CA_PATH:
        redis_dict["credential_provider"] = GoogleTokenProvider()
        redis_dict["ssl"] = True
        redis_dict["ssl_ca_certs"] = settings.GCP_REDIS_CA_PATH
    else:
        if parsed_redis.username:
            redis_dict["username"] = parsed_redis.username

        if parsed_redis.password:
            redis_dict["password"] = parsed_redis.password

    current_app.redis_client = redis.Redis(**redis_dict)  # type: ignore [attr-defined]
