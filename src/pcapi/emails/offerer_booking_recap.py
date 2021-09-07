from pcapi.core.bookings.conf import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.conf import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.models import Booking
from pcapi.core.categories import subcategories
from pcapi.models.feature import FeatureToggle
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


# TODO(yacine) old template should be removed after enabling FF ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS
OLD_MAILJET_TEMPLATE_ID = 2843165
NEW_MAILJET_TEMPLATE_ID = 3095147


def retrieve_data_for_offerer_booking_recap_email(booking: Booking) -> dict:
    mailjet_template_id = (
        NEW_MAILJET_TEMPLATE_ID
        if FeatureToggle.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS.is_active()
        else OLD_MAILJET_TEMPLATE_ID
    )
    offer = booking.stock.offer
    venue = offer.venue
    venue_name = venue.publicName if venue.publicName else venue.name
    offer_name = offer.name
    price = "Gratuit" if booking.stock.price == 0 else f"{booking.stock.price} €"
    quantity = booking.quantity
    user_email = booking.user.email
    user_firstname = booking.user.firstName
    user_lastname = booking.user.lastName
    user_phoneNumber = booking.user.phoneNumber or ""
    departement_code = venue.departementCode or "numérique"
    is_event = int(offer.isEvent)

    if (
        booking.stock.canHaveActivationCodes
        and booking.activationCode
        and FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS.is_active()
    ):
        can_expire = 0
        is_booking_autovalidated = 1
    else:
        can_expire = int(offer.subcategory.can_expire)
        is_booking_autovalidated = 0

    expiration_delay = BOOKINGS_AUTO_EXPIRY_DELAY.days
    if (
        FeatureToggle.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS.is_active()
        and offer.subcategoryId == subcategories.LIVRE_PAPIER.id
    ):
        expiration_delay = BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days

    offer_link = build_pc_pro_offer_link(offer)

    if booking.stock.price == 0 or booking.activationCode or is_booking_autovalidated:
        must_use_token_for_payment = 0
    else:
        must_use_token_for_payment = 1

    mailjet_json = {
        "MJ-TemplateID": mailjet_template_id,
        "MJ-TemplateLanguage": True,
        "Headers": {
            "Reply-To": user_email,
        },
        "Vars": {
            "nom_offre": offer_name,
            "nom_lieu": venue_name,
            "is_event": is_event,
            "ISBN": "",
            # FIXME: change MJ template variable name
            "offer_type": offer.subcategoryId,
            "date": "",
            "heure": "",
            "quantity": quantity,
            "contremarque": booking.token,
            "prix": price,
            "user_firstName": user_firstname,
            "user_lastName": user_lastname,
            "user_phoneNumber": user_phoneNumber,
            "user_email": user_email,
            "lien_offre_pcpro": offer_link,
            "departement": departement_code,
            "can_expire"
            if FeatureToggle.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS.is_active()
            else "can_expire_after_30_days": can_expire,
            "expiration_delay": expiration_delay,
            "is_booking_autovalidated": is_booking_autovalidated,
            "must_use_token_for_payment": must_use_token_for_payment,
        },
    }

    if "isbn" in offer.subcategory.conditional_fields:
        mailjet_json["Vars"]["ISBN"] = (
            offer.extraData["isbn"] if offer.extraData is not None and "isbn" in offer.extraData else ""
        )
        mailjet_json["Vars"]["offer_type"] = "book"

    offer_is_an_event = is_event == 1
    if offer_is_an_event:
        mailjet_json["Vars"]["date"] = format_booking_date_for_email(booking)
        mailjet_json["Vars"]["heure"] = format_booking_hours_for_email(booking)

    return mailjet_json
