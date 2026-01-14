import logging

import sqlalchemy as sa
from markupsafe import Markup

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.zendesk.serialization import UpdateZendeskAttributesRequest
from pcapi.core.external.zendesk.serialization import ZendeskCheckUpdateRequestStatus
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils

from . import api


logger = logging.getLogger(__name__)


@celery_async_task(
    name="tasks.zendesk.default.update_contact_attributes",
    model=UpdateZendeskAttributesRequest,
)
def update_zendesk_attributes_task(payload: UpdateZendeskAttributesRequest) -> None:
    from .api import update_contact_attributes

    update_contact_attributes(
        payload.is_new_ticket, payload.ticket_id, payload.zendesk_user_id, payload.email, payload.phone_number
    )


@celery_async_task(
    name="tasks.zendesk.default.check_update_request_status",
    model=ZendeskCheckUpdateRequestStatus,
)
def check_update_request_status_task(payload: ZendeskCheckUpdateRequestStatus) -> None:
    update_request = (
        db.session.query(users_models.UserAccountUpdateRequest)
        .filter(
            sa.or_(
                users_models.UserAccountUpdateRequest.email == payload.email,
                users_models.UserAccountUpdateRequest.oldEmail == payload.email,
            )
        )
        .order_by(users_models.UserAccountUpdateRequest.dsApplicationId.desc())
        .first()
    )

    if update_request:
        html_body = Markup(
            "Bonjour {first_name},"
            "<br/>Ton dossier n°<b>{application_number}</b> déposé sur Démarche Numérique le {date_created} avec l'adresse email <b>{email}</b> "
            "est actuellement <b>{status}</b>."
            '<br/><a href="https://demarche.numerique.gouv.fr/dossiers/{application_number}" target="_blank">Clique ici</a> pour ouvrir ton dossier et visualiser les détails.'
        ).format(
            first_name=payload.first_name,
            email=payload.email,
            application_number=update_request.dsApplicationId,
            date_created=date_utils.get_date_formatted_for_email(update_request.dateCreated),
            status=update_request.status.value,
        )
        api.add_comment(payload.ticket_id, payload.zendesk_user_id, html_body, public=True, resolve=True)
    else:
        html_body = Markup(
            "Bonjour {first_name},"
            "<br/>Aucun dossier n'a été trouvé sur Démarche Numérique avec l'adresse email <b>{email}</b>."
        ).format(
            first_name=payload.first_name,
            email=payload.email,
        )
        api.add_comment(payload.ticket_id, payload.zendesk_user_id, html_body, public=True)
