from pcapi.core.bookings.constants import BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.constants import BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.categories import subcategories
from pcapi.models.feature import FeatureToggle
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email


def retrieve_data_for_offerer_booking_recap_email(individual_booking: IndividualBooking) -> dict:
    booking = individual_booking.booking
    offer = booking.stock.offer
    venue = offer.venue
    venue_name = venue.publicName if venue.publicName else venue.name
    offer_name = offer.name
    price = "Gratuit" if booking.stock.price == 0 else f"{booking.stock.price} €"
    quantity = booking.quantity
    user_email = individual_booking.user.email
    user_firstname = individual_booking.user.firstName
    user_lastname = individual_booking.user.lastName
    user_phoneNumber = individual_booking.user.phoneNumber or ""
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
    if offer.subcategoryId == subcategories.LIVRE_PAPIER.id:
        expiration_delay = BOOKS_BOOKINGS_AUTO_EXPIRY_DELAY.days

    offer_link = build_pc_pro_offer_link(offer)

    if booking.stock.price == 0 or booking.activationCode or is_booking_autovalidated:
        must_use_token_for_payment = 0
    else:
        must_use_token_for_payment = 1

    mailjet_json = {
        "MJ-TemplateID": 3095147,
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
            "can_expire": can_expire,
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
