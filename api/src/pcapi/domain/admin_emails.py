from pcapi import settings
from pcapi.connectors import sirene
from pcapi.core import mails
import pcapi.core.offerers.models as offerers_models
from pcapi.models.feature import FeatureToggle
from pcapi.utils.mailing import make_offerer_internal_validation_email
from pcapi.utils.mailing import make_suspended_fraudulent_beneficiary_by_ids_notification_email


def maybe_send_offerer_validation_email(
    offerer: offerers_models.Offerer,
    user_offerer: offerers_models.UserOfferer,
    siren_info: sirene.SirenInfo | None,
) -> bool:
    if FeatureToggle.TEMP_DISABLE_OFFERER_VALIDATION_EMAIL.is_active():
        return True
    if offerer.isValidated and user_offerer.isValidated:
        return True
    email = make_offerer_internal_validation_email(offerer, user_offerer, siren_info)
    recipients = [settings.ADMINISTRATION_EMAIL_ADDRESS]
    return mails.send(recipients=recipients, data=email)


def send_suspended_fraudulent_users_email(fraudulent_users: dict, nb_cancelled_bookings: int, recipient: str) -> bool:
    email = make_suspended_fraudulent_beneficiary_by_ids_notification_email(fraudulent_users, nb_cancelled_bookings)
    return mails.send(recipients=[recipient], data=email)
