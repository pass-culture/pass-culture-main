"""A wrapper around the Google Drive API."""

import logging
import typing
from dataclasses import dataclass

from google.api_core import exceptions as google_exceptions
from google.cloud import secretmanager
from google.cloud.secretmanager_v1.types import resources as google_types


if typing.TYPE_CHECKING:
    from secretmanager_v1.services.secret_manager_service.client import SecretManagerServiceClient

logger = logging.getLogger(__name__)


class SecretManagerException(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Secret:
    name: str
    creation_timestamp: int
    value: str


class SecretManagerBackend:
    @property
    def _gcp_client(self) -> "SecretManagerServiceClient":
        if not hasattr(self, "_gcp_client_instance"):
            self._gcp_client_instance = secretmanager.SecretManagerServiceClient(transport="rest")
        return self._gcp_client_instance

    def _get_secret_version(self, name: str) -> str:
        request = secretmanager.AccessSecretVersionRequest(name=name)
        return self._gcp_client.access_secret_version(request=request).payload.data.decode()

    def _get_all_secret_versions(self, secret_name: str) -> typing.Generator[google_types.SecretVersion]:
        token = None
        while token != "":
            try:
                page = self._gcp_client.list_secret_versions(
                    request=secretmanager.ListSecretVersionsRequest(
                        parent=secret_name,
                        page_token=token,
                    ),
                )
            except ValueError as exc:
                raise ValueError("could not retrieve versions list from gcp") from exc

            for version in page:
                yield version

            token = page.next_page_token

    def get_last_secret_version(self, secret_name: str) -> Secret:
        return next(self.get_last_secret_versions(secret_name=secret_name, limit=1))

    def get_last_secret_versions(self, secret_name: str, limit: int = 0) -> typing.Generator[Secret]:
        counter = 0
        try:
            for version in self._get_all_secret_versions(secret_name):
                if version.state != google_types.SecretVersion.State.ENABLED:
                    # ignore DISABLED and DESTROYED versions
                    continue
                try:
                    yield Secret(
                        name=version.name,
                        creation_timestamp=int(version.create_time.timestamp()),  # type: ignore [attr-defined]
                        value=self._get_secret_version(name=version.name),
                    )
                except google_exceptions.BadRequest:
                    # The secret has been DISABLED or DESTROYED since last call to self._get_all_secret_versions
                    continue
                counter += 1
                if limit and counter >= limit:
                    break

        except Exception as exp:
            logger.exception("Error while extracting versions for secret %s" % secret_name)  # nosemgrep
            raise SecretManagerException() from exp
