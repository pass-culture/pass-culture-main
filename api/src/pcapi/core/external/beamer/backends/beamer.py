import logging
import typing

from pcapi import settings
from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.external.beamer.backends.base import BaseBackend
from pcapi.core.external.beamer.serialization import format_pro_attributes
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class BeamerBackend(BaseBackend):
    url = "https://api.getbeamer.com/v0"
    api_key = settings.BEAMER_API_KEY

    def update_pro_user(self, pro_attributes: attributes_models.ProAttributes) -> None:
        """Upserts the user into the Beamer database"""
        if not pro_attributes.user_id:
            # these pro attributes are linked to an email that is linked to venues, not to a user
            return

        put_users_url = f"{self.url}/users"
        try:
            response = requests.put(
                put_users_url,
                headers={"Beamer-Api-Key": self.api_key},
                json=format_pro_attributes(pro_attributes),
            )
        except requests.exceptions.RequestException as exc:
            logger.exception(
                "Network error on Beamer API",
                extra={"exc": exc, "url": put_users_url, "userId": pro_attributes.user_id},
            )
            raise BeamerException("Network error on Beamer API") from exc

        if not response.ok:
            raise BeamerException(
                f"Unexpected {response.status_code} response from Beamer for user {pro_attributes.user_id}"
            )

    def delete_pro_user(self, user_id: int) -> None:
        """delete the user from the Beamer database"""
        del_user_url = f"{self.url}/users"
        try:
            response = requests.delete(
                del_user_url, headers={"Beamer-Api-Key": self.api_key}, params={"userId": user_id}
            )
        except requests.exceptions.RequestException as exc:
            logger.exception(
                "Network error on Beamer API",
                extra={"exc": exc, "url": del_user_url, "userId": user_id},
            )
            raise BeamerException("Network error on Beamer API") from exc

        if not response.ok:
            raise BeamerException(f"Unexpected {response.status_code} response from Beamer for user {user_id}")


class BeamerException(requests.ExternalAPIException):
    def __init__(self, *args: typing.Any) -> None:
        super().__init__(True, *args)
