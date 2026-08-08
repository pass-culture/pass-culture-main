import logging

from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.structure_signup_api import build_signup_structure_params
from pcapi.core.users.models import User


logger = logging.getLogger(__name__)


def get_email_validation_to_pro_email_data(
    token: str, structure_simulation_infos: offerers_models.StructureSimulationInfos | None
) -> models.TransactionalEmailData:
    query_string = (
        build_signup_structure_params(**structure_simulation_infos) if structure_simulation_infos is not None else None
    )
    encoded_params = f"?{query_string}" if query_string else ""
    email_validation_link = f"{settings.PRO_URL}/inscription/compte/confirmation/{token}{encoded_params}"

    if settings.IS_DEV or settings.IS_TESTING:
        logger.info("Link for signup confirmation: %s", email_validation_link)

    return models.TransactionalEmailData(
        template=TransactionalEmail.SIGNUP_EMAIL_CONFIRMATION_TO_PRO.value,
        params={
            "EMAIL_VALIDATION_LINK": email_validation_link,
        },
    )


def send_signup_email_confirmation_to_pro(
    user: User, token: str, structure_simulation_infos: offerers_models.StructureSimulationInfos | None = None
) -> None:
    data = get_email_validation_to_pro_email_data(token, structure_simulation_infos)
    mails.send(recipients=[user.email], data=data)
