from pcapi.core import mails
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.urls import build_pc_pro_offer_link


def retrieve_data_for_offer_approval_email(
    offer: Offer | educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> models.TransactionalEmailData:
    if isinstance(offer, Offer) and offer.publicationDate:
        publication_date = offer.publicationDate.strftime("%d/%m/%Y %H:%M:%S")
    else:
        publication_date = None
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_APPROVAL_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "PUBLICATION_DATE": publication_date,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
        },
    )


def retrieve_data_for_offer_rejection_email(
    offer: Offer | educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_REJECTION_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
            "IS_COLLECTIVE_OFFER": not isinstance(offer, Offer),
        },
    )


def retrieve_data_for_pending_offer_rejection_email(
    offer: Offer | educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.publicName or offer.venue.name,
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
            "IS_COLLECTIVE_OFFER": not isinstance(offer, Offer),
        },
    )


def retrieve_data_for_validated_offer_rejection_email(
    offer: Offer | educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_VALIDATED_TO_REJECTED_TO_PRO.value,
        params={
            "OFFER_NAME": offer.name,
            "CREATION_DATE": offer.dateCreated.strftime("%d/%m/%Y"),
            "PC_PRO_OFFER_LINK": build_pc_pro_offer_link(offer),
            "IS_COLLECTIVE_OFFER": not isinstance(offer, Offer),
        },
    )


def send_offer_validation_status_update_email(
    offer: Offer | educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
    old_status: OfferValidationStatus,
    validation_status: OfferValidationStatus,
    recipient_emails: list[str],
) -> None:
    if validation_status is OfferValidationStatus.APPROVED:
        offer_data = retrieve_data_for_offer_approval_email(offer)
        mails.send(recipients=recipient_emails, data=offer_data)

    elif validation_status is OfferValidationStatus.REJECTED:
        if old_status is OfferValidationStatus.PENDING:
            offer_data = retrieve_data_for_pending_offer_rejection_email(offer)
        elif old_status is OfferValidationStatus.APPROVED:
            offer_data = retrieve_data_for_validated_offer_rejection_email(offer)
        else:
            offer_data = retrieve_data_for_offer_rejection_email(offer)
        mails.send(recipients=recipient_emails, data=offer_data)
