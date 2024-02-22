import ipaddress
import logging

from flask import request

from pcapi import settings
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.users.repository import find_user_by_email
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize


# Defined from https://developers.sendinblue.com/docs/how-to-use-webhooks#securing-your-webhooks
# and https://developers.sendinblue.com/docs/additional-ips-to-be-whitelisted
SENDINBLUE_IP_RANGE = [
    *ipaddress.IPv4Network("185.107.232.0/24"),
    *ipaddress.IPv4Network("1.179.112.0/20"),
    ipaddress.IPv4Address("195.154.30.169"),
    ipaddress.IPv4Address("195.154.31.153"),
    ipaddress.IPv4Address("195.154.31.142"),
    ipaddress.IPv4Address("195.154.31.171"),
    ipaddress.IPv4Address("195.154.31.129"),
    ipaddress.IPv4Address("195.154.79.186"),
    ipaddress.IPv4Address("163.172.23.50"),
    ipaddress.IPv4Address("163.172.75.202"),
    ipaddress.IPv4Address("163.172.75.222"),
    ipaddress.IPv4Address("163.172.76.108"),
    ipaddress.IPv4Address("163.172.77.49"),
    ipaddress.IPv4Address("163.172.77.62"),
    ipaddress.IPv4Address("163.172.77.137"),
    ipaddress.IPv4Address("163.172.99.26"),
    ipaddress.IPv4Address("163.172.99.58"),
    ipaddress.IPv4Address("163.172.109.19"),
    ipaddress.IPv4Address("163.172.109.49"),
    ipaddress.IPv4Address("163.172.109.105"),
    ipaddress.IPv4Address("163.172.109.130"),
    ipaddress.IPv4Address("51.159.71.10"),
    ipaddress.IPv4Address("51.159.71.12"),
    ipaddress.IPv4Address("51.159.71.13"),
    ipaddress.IPv4Address("51.159.71.15"),
    ipaddress.IPv4Address("51.159.71.17"),
    ipaddress.IPv4Address("51.159.71.41"),
    ipaddress.IPv4Address("51.159.58.33"),
    ipaddress.IPv4Address("51.159.58.37"),
    ipaddress.IPv4Address("51.159.58.36"),
    ipaddress.IPv4Address("51.159.58.214"),
]


logger = logging.getLogger(__name__)


def _check_sendinblue_source_ip() -> None:
    source_ip = ipaddress.IPv4Address(request.remote_addr)
    if source_ip not in SENDINBLUE_IP_RANGE and not settings.IS_DEV:
        raise ApiErrors(
            {"IP": "Source IP address is not whitelisted"},
            status_code=401,
        )


def _toggle_marketing_email_subscription(subscribe: bool) -> None:
    _check_sendinblue_source_ip()

    user_email = request.json.get("email")  # type: ignore [union-attr]
    if not user_email:
        raise ApiErrors(
            {"email": "Email missing in request payload"},
            status_code=400,
        )

    user = find_user_by_email(user_email)
    if user is None:
        raise ApiErrors({"User": "user not found for email %s" % user_email}, status_code=400)

    user.notificationSubscriptions = (
        {**user.notificationSubscriptions, "marketing_email": subscribe}
        if user.notificationSubscriptions is not None
        else {"marketing_email": subscribe}
    )
    repository.save(user)

    # Sendinblue is already up-to-date from originating automation, update marketing preference in Batch
    update_external_user(user, skip_sendinblue=True)


@public_api.route("/webhooks/sendinblue/unsubscribe", methods=["POST"])
@spectree_serialize(on_success_status=204)
def sendinblue_unsubscribe_user() -> None:
    """
    Automation scenario is configured in Sendinblue to call this webhook after user unsubscribes.
    Blacklist status and MARKETING_EMAIL_SUBSCRIPTION are updated in the scenario, so we don't need to sync them again.
    """
    _toggle_marketing_email_subscription(False)


@public_api.route("/webhooks/sendinblue/subscribe", methods=["POST"])
@spectree_serialize(on_success_status=204)
def sendinblue_subscribe_user() -> None:
    """
    Automation scenario is configured in Sendinblue to call this webhook after user unsubscribes.
    Blacklist status and MARKETING_EMAIL_SUBSCRIPTION are updated in the scenario, so we don't need to sync them again.
    """
    _toggle_marketing_email_subscription(True)


@public_api.route("/webhooks/sendinblue/importcontacts/<int:list_id>/<int:iteration>", methods=["POST"])
@spectree_serialize(on_success_status=204)
def sendinblue_notify_importcontacts(list_id: int, iteration: int) -> None:
    """
    Called by Sendinblue once an import process is finished.
    https://developers.sendinblue.com/reference/importcontacts-1

    Unfortunately there is no information in query string and the body is empty, so we can't check a process id.
    The id of the list in Sendinblue is added to the URL when set in notifyUrl so we can at least print the list id.
    This webhook is for investigation purpose only.
    """
    _check_sendinblue_source_ip()

    logger.info("ContactsApi->import_contacts finished", extra={"list_id": list_id, "iteration": iteration})
