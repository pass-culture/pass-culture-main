from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.repository import find_new_offerer_user_email


def get_new_offerer_validation_email_data(
    offerer: offerers_models.Offerer, venue: offerers_models.Venue | None
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.NEW_OFFERER_VALIDATION.value,
        params={"OFFERER_NAME": venue.publicName if venue else offerer.name},
    )


# TODO (prouzet): remove when offerers are no longer validated
def send_new_offerer_validation_email_to_pro(offerer: offerers_models.Offerer) -> None:
    offerer_email = find_new_offerer_user_email(offerer.id)
    data = get_new_offerer_validation_email_data(offerer, None)
    mails.send(recipients=[offerer_email], data=data)


def send_new_venue_validation_email_to_pro(venue: offerers_models.Venue) -> None:
    offerer_email = find_new_offerer_user_email(venue.managingOfferer.id)
    data = get_new_offerer_validation_email_data(venue.managingOfferer, venue)
    mails.send(recipients=[offerer_email], data=data)


def get_new_offerer_rejection_email_data(
    offerer: offerers_models.Offerer,
    venue: offerers_models.Venue | None,
    rejection_reason: offerers_models.OffererRejectionReason | None = None,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.NEW_OFFERER_REJECTION.value,
        params={
            "OFFERER_NAME": venue.publicName if venue else offerer.name,
            "REJECTION_REASON": rejection_reason.name if rejection_reason else "",
        },
    )


# TODO (prouzet): remove when offerers are no longer validated
def send_new_offerer_rejection_email_to_pro(
    offerer: offerers_models.Offerer, rejection_reason: offerers_models.OffererRejectionReason | None
) -> None:
    offerer_email = find_new_offerer_user_email(offerer.id)
    data = get_new_offerer_rejection_email_data(offerer, None, rejection_reason)
    mails.send(recipients=[offerer_email], data=data)


def send_new_venue_rejection_email_to_pro(
    venue: offerers_models.Venue, rejection_reason: offerers_models.OffererRejectionReason | None
) -> None:
    offerer_email = find_new_offerer_user_email(venue.managingOfferer.id)
    data = get_new_offerer_rejection_email_data(venue.managingOfferer, venue, rejection_reason)
    mails.send(recipients=[offerer_email], data=data)
