from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer


def get_highlight_communication_email_data(offer: Offer) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.HIGHLIGHT_COMMUNICATION_TO_PRO.value, params={"OFFER_NAME": offer.name}
    )


def send_highlight_communication_email_to_pro(offer: Offer) -> None:
    recipient = offer.venue.bookingEmail
    if not recipient:
        return
    data = get_highlight_communication_email_data(offer)
    mails.send(recipients=[recipient], data=data)
