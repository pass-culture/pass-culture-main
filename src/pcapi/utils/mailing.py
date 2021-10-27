import base64
from datetime import datetime
import io
from pprint import pformat
import zipfile

from flask import render_template

from pcapi import settings
from pcapi.connectors import api_entreprises
from pcapi.core.bookings.repository import find_ongoing_bookings_by_stock
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.utils import offer_webapp_link
from pcapi.core.users.models import User
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import UserOfferer
from pcapi.utils.date import format_datetime
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.human_ids import humanize
from pcapi.utils.urls import get_webapp_url


class MailServiceException(Exception):
    pass


def build_pc_pro_offer_link(offer: Offer) -> str:
    return f"{settings.PRO_URL}/offres/{humanize(offer.id)}/edition"


def build_pc_pro_offerer_link(offerer: Offerer) -> str:
    return f"{settings.PRO_URL}/accueil?structure={humanize(offerer.id)}"


def build_pc_pro_create_password_link(token_value: str) -> str:
    return f"{settings.PRO_URL}/creation-de-mot-de-passe/{token_value}"


def build_pc_pro_reset_password_link(token_value: str) -> str:
    return f"{settings.PRO_URL}/mot-de-passe-perdu?token={token_value}"


def build_pc_webapp_reset_password_link(token_value: str) -> str:
    return f"{get_webapp_url()}/mot-de-passe-perdu?token={token_value}"


def extract_users_information_from_bookings(bookings: list[Booking]) -> list[dict]:
    users_keys = ("firstName", "lastName", "email", "contremarque")
    users_properties = [[booking.firstName, booking.lastName, booking.email, booking.token] for booking in bookings]

    return [dict(zip(users_keys, user_property)) for user_property in users_properties]


def format_booking_date_for_email(booking: Booking) -> str:
    if booking.stock.offer.isEvent:
        date_in_tz = get_event_datetime(booking.stock)
        offer_date = date_in_tz.strftime("%d-%b-%Y")
        return offer_date
    return ""


def format_booking_hours_for_email(booking: Booking) -> str:
    if booking.stock.offer.isEvent:
        date_in_tz = get_event_datetime(booking.stock)
        event_hour = date_in_tz.hour
        event_minute = date_in_tz.minute
        return f"{event_hour}h" if event_minute == 0 else f"{event_hour}h{event_minute}"
    return ""


def make_validation_email_object(
    offerer: Offerer, user_offerer: UserOfferer, get_by_siren=api_entreprises.get_by_offerer
) -> dict:
    vars_obj_user = vars(user_offerer.user)
    vars_obj_user.pop("clearTextPassword", None)
    api_entreprise = get_by_siren(offerer)

    offerer_departement_code = PostalCode(offerer.postalCode).get_departement_code()

    email_html = render_template(
        "mails/internal_validation_email.html",
        user_offerer=user_offerer,
        user_vars=pformat(vars_obj_user),
        offerer=offerer,
        offerer_vars_user_offerer=pformat(vars(user_offerer.offerer)),
        offerer_vars=pformat(vars(offerer)),
        offerer_pro_link=build_pc_pro_offerer_link(offerer),
        offerer_summary=pformat(_summarize_offerer_vars(offerer, api_entreprise)),
        user_summary=pformat(_summarize_user_vars(user_offerer)),
        api_entreprise=pformat(api_entreprise),
        api_url=settings.API_URL,
    )

    return {
        "FromName": "pass Culture",
        "Subject": "%s - inscription / rattachement PRO à valider : %s" % (offerer_departement_code, offerer.name),
        "Html-part": email_html,
    }


def make_offerer_driven_cancellation_email_for_offerer(booking: Booking) -> dict:
    stock_name = booking.stock.offer.name
    venue = booking.venue
    user_name = booking.publicName
    user_email = booking.email
    email_subject = "Confirmation de votre annulation de réservation pour {}, proposé par {}".format(
        stock_name, venue.name
    )
    ongoing_stock_bookings = find_ongoing_bookings_by_stock(booking.stock.id)
    stock_date_time = None
    booking_is_on_event = booking.stock.beginningDatetime is not None
    if booking_is_on_event:
        date_in_tz = get_event_datetime(booking.stock)
        stock_date_time = format_datetime(date_in_tz)
    email_html = render_template(
        "mails/offerer_recap_email_after_offerer_cancellation.html",
        booking_is_on_event=booking_is_on_event,
        user_name=user_name,
        user_email=user_email,
        stock_date_time=stock_date_time,
        number_of_bookings=len(ongoing_stock_bookings),
        stock_bookings=ongoing_stock_bookings,
        stock_name=stock_name,
        venue=venue,
    )
    return {
        "FromName": "pass Culture",
        "Subject": email_subject,
        "Html-part": email_html,
    }


def make_payment_message_email(xml: str, venues_csv, checksum: bytes) -> dict:
    now = datetime.utcnow()
    encoded_xml = base64.b64encode(xml.encode("utf-8")).decode()
    xml_name = "message_banque_de_france_{}.xml".format(now.strftime("%Y%m%d"))
    encoded_csv = base64.b64encode(venues_csv.encode("utf-8")).decode()
    csv_name = "lieux_{}.csv".format(now.strftime("%Y%m%d"))

    attachments = [
        {
            "ContentType": "text/xml",
            "Filename": xml_name,
            "Content": encoded_xml,
        },
        {
            "ContentType": "text/csv",
            "Filename": csv_name,
            "Content": encoded_csv,
        },
    ]

    return {
        "FromName": "pass Culture Pro",
        "Subject": "Virements XML pass Culture Pro - {}".format(datetime.strftime(now, "%Y-%m-%d")),
        "Attachments": attachments,
        "Html-part": render_template(
            "mails/payments_xml_email.html", xml_name=xml_name, csv_name=csv_name, xml_hash=checksum.hex()
        ),
    }


def _get_zipfile_content(content: str, filename: str):
    """Return the content of a ZIP fie that would include a single file
    with the requested content and filename.
    """
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr(filename, content)
    stream.seek(0)
    return stream.read()


def make_payment_details_email(csv: str) -> dict:
    now = datetime.utcnow()
    csv_filename = f"details_des_paiements_{datetime.strftime(now, '%Y%m%d')}.csv"
    zipfile_content = _get_zipfile_content(csv, csv_filename)
    return {
        "FromName": "pass Culture Pro",
        "Subject": "Détails des paiements pass Culture Pro - {}".format(datetime.strftime(now, "%Y-%m-%d")),
        "Attachments": [
            {
                "ContentType": "application/zip",
                "Filename": f"{csv_filename}.zip",
                "Content": base64.b64encode(zipfile_content).decode(),
            },
        ],
        "Html-part": "",
    }


def make_payments_report_email(not_processable_csv: str, n_payments_by_status: dict) -> dict:
    now = datetime.utcnow()
    not_processable_csv_b64encode = base64.b64encode(not_processable_csv.encode("utf-8")).decode()
    formatted_date = datetime.strftime(now, "%Y-%m-%d")

    n_total_payments = sum(count for count in n_payments_by_status.values())

    return {
        "Subject": "Récapitulatif des paiements pass Culture Pro - {}".format(formatted_date),
        "FromName": "pass Culture Pro",
        "Attachments": [
            {
                "ContentType": "text/csv",
                "Filename": "paiements_non_traitables_{}.csv".format(formatted_date),
                "Content": not_processable_csv_b64encode,
            },
        ],
        "Html-part": render_template(
            "mails/payments_report_email.html",
            date_sent=formatted_date,
            total_number=n_total_payments,
            n_payments_by_status=n_payments_by_status,
        ),
    }


def make_wallet_balances_email(csv: str) -> dict:
    now = datetime.utcnow()
    csv_filename = "soldes_des_utilisateurs_{}.csv".format(now.strftime("%Y%m%d"))
    zipfile_content = _get_zipfile_content(csv, csv_filename)
    return {
        "FromName": "pass Culture Pro",
        "Subject": "Soldes des utilisateurs pass Culture - {}".format(datetime.strftime(now, "%Y-%m-%d")),
        "Attachments": [
            {
                "ContentType": "application/zip",
                "Filename": f"{csv_filename}.zip",
                "Content": base64.b64encode(zipfile_content).decode(),
            }
        ],
        "Html-part": "",
    }


def make_offer_creation_notification_email(offer: Offer) -> dict:
    author = offer.author or offer.venue.managingOfferer.UserOfferers[0].user
    venue = offer.venue
    pro_link_to_offer = f"{settings.PRO_URL}/offres/{humanize(offer.id)}/edition"
    pro_venue_link = f"{settings.PRO_URL}/structures/{humanize(venue.managingOffererId)}/lieux/{humanize(venue.id)}"
    webapp_link_to_offer = offer_webapp_link(offer)
    html = render_template(
        "mails/offer_creation_notification_email.html",
        offer=offer,
        venue=venue,
        author=author,
        pro_link_to_offer=pro_link_to_offer,
        webapp_link_to_offer=webapp_link_to_offer,
        pro_venue_link=pro_venue_link,
    )
    location_information = offer.venue.departementCode or "numérique"
    return {
        "Html-part": html,
        "FromName": "pass Culture",
        "Subject": f"[Création d’offre - {location_information}] {offer.name}",
    }


def make_offer_rejection_notification_email(offer: Offer) -> dict:
    author = offer.author or offer.venue.managingOfferer.UserOfferers[0].user
    pro_link_to_offer = f"{settings.PRO_URL}/offres/{humanize(offer.id)}/edition"
    venue = offer.venue
    pro_venue_link = f"{settings.PRO_URL}/structures/{humanize(venue.managingOffererId)}/lieux/{humanize(venue.id)}"
    html = render_template(
        "mails/offer_creation_refusal_notification_email.html",
        offer=offer,
        venue=venue,
        author=author,
        pro_link_to_offer=pro_link_to_offer,
        pro_venue_link=pro_venue_link,
    )
    location_information = offer.venue.departementCode or "numérique"
    return {
        "Html-part": html,
        "FromName": "pass Culture",
        "Subject": f"[Création d’offre : refus - {location_information}] {offer.name}",
    }


def get_event_datetime(stock: Stock) -> datetime:
    if stock.offer.venue.departementCode is not None:
        date_in_utc = stock.beginningDatetime
        date_in_tz = utc_datetime_to_department_timezone(date_in_utc, stock.offer.venue.departementCode)
    else:
        date_in_tz = stock.beginningDatetime

    return date_in_tz


def make_pro_user_validation_email(user: User) -> dict:
    return {
        "FromName": "pass Culture pro",
        "Subject": "[pass Culture pro] Validation de votre adresse email pour le pass Culture",
        "MJ-TemplateID": 1660341,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "nom_structure": user.publicName,
            "lien_validation_mail": f"{settings.PRO_URL}/inscription/validation/{user.validationToken}",
        },
    }


def make_admin_user_validation_email(user: User, token: str) -> dict:
    return {
        "FromName": "pass Culture admin",
        "Subject": "[pass Culture admin] Validation de votre adresse email pour le pass Culture",
        "MJ-TemplateID": 1660341,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "lien_validation_mail": f"{settings.PRO_URL}/creation-de-mot-de-passe/{token}",
        },
    }


def _add_template_debugging(message_data: dict) -> None:
    message_data["TemplateErrorReporting"] = {
        "Email": settings.DEV_EMAIL_ADDRESS,
        "Name": "Mailjet Template Errors",
    }


def _summarize_offerer_vars(offerer: Offerer, api_entreprise: dict) -> dict:
    return {
        "name": offerer.name,
        "siren": offerer.siren,
        "address": offerer.address,
        "city": offerer.city,
        "postalCode": offerer.postalCode,
        "siret": api_entreprise["unite_legale"]["etablissement_siege"]["siret"],
        "legal_main_activity": api_entreprise["unite_legale"]["activite_principale"],
    }


def _summarize_user_vars(user_offerer: UserOfferer) -> dict:
    return {
        "firstName": user_offerer.user.firstName,
        "lastName": user_offerer.user.lastName,
        "email": user_offerer.user.email,
        "phoneNumber": user_offerer.user.phoneNumber,
        "activity": user_offerer.user.activity,
    }
