from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.mailing import build_pc_pro_offer_link


def retrieve_data_for_offer_approval_email(offer: Offer) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_APPROVAL_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
        },
    )


def retrieve_data_for_offer_rejection_email(offer: Offer) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_REJECTION_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
        },
    )


def send_offer_validation_status_update_email(
    offer: Offer, validation_status: OfferValidationStatus, recipient_emails: list[str]
) -> bool:
    if validation_status is OfferValidationStatus.APPROVED:
        offer_data = retrieve_data_for_offer_approval_email(offer)
        return mails.send(recipients=recipient_emails, data=offer_data)

    if validation_status is OfferValidationStatus.REJECTED:
        offer_data = retrieve_data_for_offer_rejection_email(offer)
        return mails.send(recipients=recipient_emails, data=offer_data)
    return True
