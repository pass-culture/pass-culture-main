from typing import Union

from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.utils import offer_app_redirect_link
from pcapi.core.users.models import User
from pcapi.models.feature import FeatureToggle


def get_offer_link_to_ios_user_email_data(user: User, offer: Offer) -> Union[dict, SendinblueTransactionalEmailData]:
    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        return {
            "MJ-TemplateID": 2826195,
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_webapp_link": offer_app_redirect_link(offer),
                "user_first_name": user.firstName,
                "offer_name": offer.name,
                "venue_name": offer.venue.name,
            },
        }

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.OFFER_WEBAPP_LINK_TO_IOS_USER.value,
        params={
            "OFFER_WEBAPP_LINK": offer_app_redirect_link(offer),
            "FIRSTNAME": user.firstName,
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
        },
    )


def send_offer_link_to_ios_user_email(user: User, offer: Offer) -> bool:
    data = get_offer_link_to_ios_user_email_data(user, offer)
    return mails.send(recipients=[user.email], data=data)
