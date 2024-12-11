import logging
import typing

from pcapi import settings
from pcapi.core.external.attributes import models as attributes_models
from pcapi.utils import requests
from pcapi.utils.module_loading import import_string


logger = logging.getLogger(__name__)


def update_beamer_user(pro_attributes: attributes_models.ProAttributes) -> None:
    _get_backend().update_pro_user(pro_attributes)


def delete_beamer_user(user_id: int) -> None:
    _get_backend().delete_pro_user(user_id)


def _get_backend() -> "BaseBackend":
    backend_class = import_string(settings.BEAMER_BACKEND)
    return backend_class()


class BaseBackend:
    def update_pro_user(self, pro_attributes: attributes_models.ProAttributes) -> None:
        """Upserts the user into the Beamer database"""
        raise NotImplementedError()

    def delete_pro_user(self, user_id: int) -> None:
        """delete the user from the Beamer database"""
        raise NotImplementedError()


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


class LoggerBackend(BaseBackend):
    def update_pro_user(self, pro_attributes: attributes_models.ProAttributes) -> None:
        request_data = format_pro_attributes(pro_attributes)

        if not pro_attributes.user_id:
            logger.info("Pro attributes %s not linked to a user, skipping", request_data)
            return

        logger.info("Updated pro user data on Beamer: %s", request_data)

    def delete_pro_user(self, user_id: int) -> None:
        logger.info("Updated pro user data on Beamer: %s", user_id)


def format_pro_attributes(pro_attributes: attributes_models.ProAttributes) -> dict:
    return {
        "userId": pro_attributes.user_id,
        "DMS_APPLICATION_APPROVED": pro_attributes.dms_application_approved,
        "DMS_APPLICATION_SUBMITTED": pro_attributes.dms_application_submitted,
        "HAS_BANNER_URL": pro_attributes.has_banner_url,
        "HAS_BOOKINGS": pro_attributes.has_bookings,
        "HAS_OFFERS": pro_attributes.has_offers,
        "HAS_INDIVIDUAL_OFFERS": pro_attributes.has_individual_offers,
        "IS_ACTIVE_PRO": pro_attributes.is_active_pro,
        "IS_BOOKING_EMAIL": pro_attributes.is_booking_email,
        "IS_EAC": pro_attributes.is_eac,
        "IS_PERMANENT": pro_attributes.isPermanent,
        "IS_OPEN_TO_PUBLIC": pro_attributes.isOpenToPublic,
        "IS_PRO": pro_attributes.is_pro,
        "IS_VIRTUAL": pro_attributes.isVirtual,
        "OFFERER_NAME": ";".join(pro_attributes.offerers_names),
        "OFFERER_TAG": ";".join(pro_attributes.offerers_tags),
        "USER_IS_ATTACHED": pro_attributes.user_is_attached,
        "VENUE_LABEL": ";".join(pro_attributes.venues_labels),
        "VENUE_TYPE": ";".join(pro_attributes.venues_types),
    }


class BeamerException(requests.ExternalAPIException):
    def __init__(self, *args: typing.Any) -> None:
        super().__init__(True, *args)
