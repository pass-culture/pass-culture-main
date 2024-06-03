import logging

from flask import request

from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.history import api as history_api
from pcapi.core.users.repository import find_user_by_email
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


def _toggle_marketing_email_subscription(subscribe: bool) -> None:
    user_email = request.json.get("email")  # type: ignore[union-attr]
    if not user_email:
        raise ApiErrors(
            {"email": "Email missing in request payload"},
            status_code=400,
        )

    user = find_user_by_email(user_email)
    if user is None:
        raise ApiErrors({"User": "user not found for email %s" % user_email}, status_code=400)

    history_api.ObjectUpdateSnapshot(user, user).trace_update(
        {"marketing_email": subscribe},
        target=user.get_notification_subscriptions(),
        field_name_template="notificationSubscriptions.{}",
    ).add_action()

    user.set_marketing_email_subscription(subscribe)

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
    logger.info("ContactsApi->import_contacts finished", extra={"list_id": list_id, "iteration": iteration})
