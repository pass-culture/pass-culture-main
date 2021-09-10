import ipaddress

from flask import request

from pcapi import settings
from pcapi.flask_app import api
from pcapi.flask_app import public_api
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.serialization.decorator import spectree_serialize


SENDINBLUE_IP_RANGE = ipaddress.IPv4Network("185.107.232.0/24")


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
