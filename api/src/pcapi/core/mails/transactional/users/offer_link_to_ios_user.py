from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.utils import offer_app_redirect_link
from pcapi.core.users.models import User


def get_offer_link_to_ios_user_email_data(user: User, offer: Offer) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFER_WEBAPP_LINK_TO_IOS_USER.value,
        params={
            "OFFER_WEBAPP_LINK": offer_app_redirect_link(offer),
            "FIRSTNAME": user.firstName,
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
        },
    )


def send_offer_link_to_ios_user_email(user: User, offer: Offer) -> None:
    data = get_offer_link_to_ios_user_email_data(user, offer)
    mails.send(recipients=[user.email], data=data)
