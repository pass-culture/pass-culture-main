from pcapi import settings
from pcapi.core import mails
from pcapi.core.categories import subcategories
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.mailing import make_offer_creation_notification_email
from pcapi.utils.mailing import make_offer_rejection_notification_email
from pcapi.utils.mailing import make_offerer_internal_validation_email
from pcapi.utils.mailing import make_suspended_fraudulent_beneficiary_by_ids_notification_email


def maybe_send_offerer_validation_email(
    offerer: offerers_models.Offerer,
    user_offerer: offerers_models.UserOfferer,
) -> bool:
    if offerer.isValidated and user_offerer.isValidated:
        return True
    email = make_offerer_internal_validation_email(offerer, user_offerer)
    recipients = [settings.ADMINISTRATION_EMAIL_ADDRESS]
    return mails.send(recipients=recipients, data=email)


def _check_offer_subcategory_before_send(offer: Offer) -> bool:
    return offer.subcategoryId not in (
        subcategories.ABO_JEU_VIDEO.id,
        subcategories.ABO_LIVRE_NUMERIQUE.id,
        subcategories.ACHAT_INSTRUMENT.id,
        subcategories.AUTRE_SUPPORT_NUMERIQUE.id,
        subcategories.BON_ACHAT_INSTRUMENT.id,
        subcategories.LIVRE_AUDIO_PHYSIQUE.id,
        subcategories.LIVRE_NUMERIQUE.id,
        subcategories.LIVRE_PAPIER.id,
        subcategories.LOCATION_INSTRUMENT.id,
        subcategories.MATERIEL_ART_CREATIF.id,
        subcategories.PARTITION.id,
        subcategories.SUPPORT_PHYSIQUE_FILM.id,
        subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id,
        subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
        subcategories.TELECHARGEMENT_MUSIQUE.id,
        subcategories.VOD.id,
    )


def send_offer_creation_notification_to_administration(
    offer: CollectiveOffer | CollectiveOfferTemplate | Offer,
) -> bool:
    email = make_offer_creation_notification_email(offer)
    return mails.send(recipients=[settings.ADMINISTRATION_EMAIL_ADDRESS], data=email)


def send_offer_rejection_notification_to_administration(offer: Offer) -> bool:
    data = make_offer_rejection_notification_email(offer)
    return mails.send(recipients=[settings.ADMINISTRATION_EMAIL_ADDRESS], data=data)


def send_offer_validation_notification_to_administration(
    validation_status: OfferValidationStatus, offer: Offer
) -> bool:
    if validation_status is OfferValidationStatus.APPROVED:
        if _check_offer_subcategory_before_send(offer) == True:
            return send_offer_creation_notification_to_administration(offer)
    if validation_status is OfferValidationStatus.REJECTED:
        return send_offer_rejection_notification_to_administration(offer)
    return True


def send_suspended_fraudulent_users_email(fraudulent_users: dict, nb_cancelled_bookings: int, recipient: str) -> bool:
    email = make_suspended_fraudulent_beneficiary_by_ids_notification_email(fraudulent_users, nb_cancelled_bookings)
    return mails.send(recipients=[recipient], data=email)
