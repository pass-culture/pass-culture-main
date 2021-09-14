import ipaddress

from flask import request

from pcapi import settings
from pcapi.flask_app import api
from pcapi.flask_app import public_api
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.serialization.decorator import spectree_serialize


# Defined from https://developers.sendinblue.com/docs/how-to-use-webhooks#securing-your-webhooks
# and https://developers.sendinblue.com/docs/additional-ips-to-be-whitelisted
SENDINBLUE_IP_RANGE = [
    *ipaddress.IPv4Network("185.107.232.0/24"),
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


@public_api.route("/webhooks/sendinblue/unsubscribe", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    api=api,
)  # type: ignore
def unsubscribe_user():
    source_ip = ipaddress.IPv4Address(request.headers.get("X-Forwarded-For", "0.0.0.0"))
    if source_ip not in SENDINBLUE_IP_RANGE and settings.IS_DEV is False:
        raise ApiErrors(
            {"IP": "Source IP address is not whitelisted"},
            status_code=401,
        )

    user_email = request.json.get("email")
    if not user_email:
        raise ApiErrors(
            {"email": "Email missing in request payload"},
            status_code=400,
        )

    user_to_unsubscribe = find_user_by_email(user_email)
    if user_to_unsubscribe is None:
        raise ApiErrors({"User": "user not found for email %s" % user_email}, status_code=400)

    user_to_unsubscribe.notificationSubscriptions = (
        {**user_to_unsubscribe.notificationSubscriptions, "marketing_email": False}
        if user_to_unsubscribe.notificationSubscriptions is not None
        else {"marketing_email": False}
    )
    repository.save(user_to_unsubscribe)
