import base64
import os
from datetime import datetime
from pprint import pformat
from typing import Dict, List, Union

from flask import current_app as app, render_template

from connectors import api_entreprises
from domain.postal_code.postal_code import PostalCode
from models import BookingSQLEntity, Offer, Offerer, StockSQLEntity, UserSQLEntity, UserOfferer, Venue
from models.email import EmailStatus
from repository import booking_queries
from repository import email_queries
from repository.feature_queries import feature_send_mail_to_users_enabled
from utils import logger
from utils.config import API_URL, PRO_URL, ENV, IS_PROD
from utils.date import format_datetime, utc_datetime_to_department_timezone
from utils.human_ids import humanize

MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')
SUPPORT_EMAIL_ADDRESS = os.environ.get('SUPPORT_EMAIL_ADDRESS')
ADMINISTRATION_EMAIL_ADDRESS = os.environ.get('ADMINISTRATION_EMAIL_ADDRESS')
DEV_EMAIL_ADDRESS = os.environ.get('DEV_EMAIL_ADDRESS')

if MAILJET_API_KEY is None or MAILJET_API_KEY == '':
    raise ValueError("Missing environment variable MAILJET_API_KEY")

if MAILJET_API_SECRET is None or MAILJET_API_SECRET == '':
    raise ValueError("Missing environment variable MAILJET_API_SECRET")

if SUPPORT_EMAIL_ADDRESS is None or SUPPORT_EMAIL_ADDRESS == '':
    raise ValueError("Missing environment variable SUPPORT_EMAIL_ADDRESS")

if ADMINISTRATION_EMAIL_ADDRESS is None or ADMINISTRATION_EMAIL_ADDRESS == '':
    raise ValueError(
        "Missing environment variable ADMINISTRATION_EMAIL_ADDRESS")

if DEV_EMAIL_ADDRESS is None or DEV_EMAIL_ADDRESS == '':
    raise ValueError("Missing environment variable DEV_EMAIL_ADDRESS")


class MailServiceException(Exception):
    pass


def send_raw_email(data: Dict) -> bool:
    response = app.mailjet_client.send.create(data=data)
    successfully_sent_email = response.status_code == 200
    status = EmailStatus.SENT if successfully_sent_email else EmailStatus.ERROR
    email_queries.save(data, status)
    if not successfully_sent_email:
        logger.logger.warning(
            f'[EMAIL] Trying to send email # {data} failed with status code {response.status_code}')
    return successfully_sent_email


def build_pc_pro_offer_link(offer: Offer) -> str:
    return f'{PRO_URL}/offres/{humanize(offer.id)}?lieu={humanize(offer.venueId)}' \
           f'&structure={humanize(offer.venue.managingOffererId)}'


def extract_users_information_from_bookings(bookings: List[BookingSQLEntity]) -> List[dict]:
    users_keys = ('firstName', 'lastName', 'email', 'contremarque')
    users_properties = [[booking.user.firstName, booking.user.lastName, booking.user.email, booking.token] for booking
                        in bookings]

    return [dict(zip(users_keys, user_property)) for user_property in users_properties]


def create_email_recipients(recipients: List[str]) -> str:
    if feature_send_mail_to_users_enabled():
        return ', '.join(recipients)
    else:
        return DEV_EMAIL_ADDRESS


def format_environment_for_email() -> str:
    return '' if IS_PROD else f'-{ENV}'


def format_booking_date_for_email(booking: BookingSQLEntity) -> str:
    if booking.stock.offer.isEvent:
        date_in_tz = get_event_datetime(booking.stock)
        offer_date = date_in_tz.strftime("%d-%b-%Y")
        return offer_date
    return ''


def format_booking_hours_for_email(booking: BookingSQLEntity) -> str:
    if booking.stock.offer.isEvent:
        date_in_tz = get_event_datetime(booking.stock)
        event_hour = date_in_tz.hour
        event_minute = date_in_tz.minute
        return f'{event_hour}h' if event_minute == 0 else f'{event_hour}h{event_minute}'
    return ''


def make_validation_email_object(offerer: Offerer, user_offerer: UserOfferer,
                                 get_by_siren=api_entreprises.get_by_offerer) -> Dict:
    vars_obj_user = vars(user_offerer.user)
    vars_obj_user.pop('clearTextPassword', None)
    api_entreprise = get_by_siren(offerer)

    offerer_departement_code = PostalCode(offerer.postalCode).get_departement_code()

    email_html = render_template('mails/internal_validation_email.html',
                                 user_offerer=user_offerer,
                                 user_vars=pformat(vars_obj_user),
                                 offerer=offerer,
                                 offerer_vars_user_offerer=pformat(
                                     vars(user_offerer.offerer)),
                                 offerer_vars=pformat(vars(offerer)),
                                 api_entreprise=pformat(api_entreprise),
                                 api_url=API_URL)

    return {
        'FromName': 'pass Culture',
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'Subject': "%s - inscription / rattachement PRO à valider : %s" % (
            offerer_departement_code, offerer.name),
        'Html-part': email_html
    }


def make_offerer_driven_cancellation_email_for_offerer(booking: BookingSQLEntity) -> Dict:
    stock_name = booking.stock.offer.product.name
    venue = booking.stock.offer.venue
    user_name = booking.user.publicName
    user_email = booking.user.email
    email_subject = 'Confirmation de votre annulation de réservation pour {}, proposé par {}'.format(stock_name,
                                                                                                     venue.name)
    ongoing_stock_bookings = booking_queries.find_ongoing_bookings_by_stock(
        booking.stock.id)
    stock_date_time = None
    booking_is_on_event = booking.stock.beginningDatetime is not None
    if booking_is_on_event:
        date_in_tz = get_event_datetime(booking.stock)
        stock_date_time = format_datetime(date_in_tz)
    email_html = render_template('mails/offerer_recap_email_after_offerer_cancellation.html',
                                 booking_is_on_event=booking_is_on_event,
                                 user_name=user_name,
                                 user_email=user_email,
                                 stock_date_time=stock_date_time,
                                 number_of_bookings=len(
                                     ongoing_stock_bookings),
                                 stock_bookings=ongoing_stock_bookings,
                                 stock_name=stock_name,
                                 venue=venue,
                                 )
    return {
        'FromName': 'pass Culture',
        'FromEmail': SUPPORT_EMAIL_ADDRESS if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'Subject': email_subject,
        'Html-part': email_html,
    }


def make_user_validation_email(user: UserSQLEntity, app_origin_url: str, is_webapp: bool) -> Dict:
    if is_webapp:
        data = make_webapp_user_validation_email(user, app_origin_url)
    else:
        data = make_pro_user_validation_email(user, app_origin_url)
    return data


def get_contact(user: UserSQLEntity) -> Union[str, None]:
    mailjet_json_response = app.mailjet_client.contact.get(user.email).json()
    return mailjet_json_response['Data'][0] if 'Data' in mailjet_json_response else None


def subscribe_newsletter(user: UserSQLEntity):
    if not feature_send_mail_to_users_enabled():
        logger.logger.info("Subscription in DEV or STAGING mode is disabled")
        return

    try:
        contact = get_contact(user)
    except:
        contact_data = {
            'Email': user.email,
            'Name': user.publicName
        }
        contact_json = app.mailjet_client.contact.create(
            data=contact_data).json()
        contact = contact_json['Data'][0] if 'Data' in contact_json else None

    if contact is None:
        raise MailServiceException

    # ('Pass Culture - Liste de diffusion', 1795144)
    contact_lists_data = {
        "ContactsLists": [
            {
                "Action": "addnoforce",
                "ListID": 1795144
            }
        ]
    }

    return app.mailjet_client.contact_managecontactslists.create(
        id=contact['ID'],
        data=contact_lists_data
    ).json()


def make_payment_message_email(xml: str, checksum: bytes) -> Dict:
    now = datetime.utcnow()
    xml_b64encode = base64.b64encode(xml.encode('utf-8')).decode()
    file_name = "message_banque_de_france_{}.xml".format(
        datetime.strftime(now, "%Y%m%d"))

    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'FromName': "pass Culture Pro",
        'Subject': "Virements XML pass Culture Pro - {}".format(datetime.strftime(now, "%Y-%m-%d")),
        'Attachments': [{"ContentType": "text/xml",
                         "Filename": file_name,
                         "Content": xml_b64encode}],
        'Html-part': render_template('mails/payments_xml_email.html', file_name=file_name, file_hash=checksum.hex())
    }


def make_payment_details_email(csv: str) -> Dict:
    now = datetime.utcnow()
    csv_b64encode = base64.b64encode(csv.encode('utf-8')).decode()
    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'FromName': 'pass Culture Pro',
        'Subject': 'Détails des paiements pass Culture Pro - {}'.format(datetime.strftime(now, "%Y-%m-%d")),
        'Attachments': [{"ContentType": "text/csv",
                         "Filename": "details_des_paiements_{}.csv".format(datetime.strftime(now, "%Y%m%d")),
                         "Content": csv_b64encode}],
        'Html-part': ''
    }


def make_payments_report_email(not_processable_csv: str, error_csv: str, grouped_payments: Dict) -> Dict:
    now = datetime.utcnow()
    not_processable_csv_b64encode = base64.b64encode(
        not_processable_csv.encode('utf-8')).decode()
    error_csv_b64encode = base64.b64encode(error_csv.encode('utf-8')).decode()
    formatted_date = datetime.strftime(now, "%Y-%m-%d")

    def number_of_payments_for_one_status(key_value): return len(key_value[1])

    total_number_of_payments = sum(
        map(number_of_payments_for_one_status, grouped_payments.items()))

    return {
        'Subject': 'Récapitulatif des paiements pass Culture Pro - {}'.format(formatted_date),
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'FromName': 'pass Culture Pro',
        'Attachments': [
            {
                "ContentType": "text/csv",
                "Filename": "paiements_non_traitables_{}.csv".format(formatted_date),
                "Content": not_processable_csv_b64encode
            },
            {
                "ContentType": "text/csv",
                "Filename": "paiements_en_erreur_{}.csv".format(formatted_date),
                "Content": error_csv_b64encode
            }
        ],
        'Html-part': render_template(
            'mails/payments_report_email.html',
            date_sent=formatted_date,
            total_number=total_number_of_payments,
            grouped_payments=grouped_payments
        )
    }


def make_wallet_balances_email(csv: str) -> Dict:
    now = datetime.utcnow()
    csv_b64encode = base64.b64encode(csv.encode('utf-8')).decode()
    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'FromName': "pass Culture Pro",
        'Subject': "Soldes des utilisateurs pass Culture - {}".format(datetime.strftime(now, "%Y-%m-%d")),
        'Attachments': [{"ContentType": "text/csv",
                         "Filename": "soldes_des_utilisateurs_{}.csv".format(datetime.strftime(now, "%Y%m%d")),
                         "Content": csv_b64encode}],
        'Html-part': ""
    }


def make_activation_users_email(csv: str) -> Dict:
    now = datetime.utcnow()
    csv_b64encode = base64.b64encode(csv.encode('utf-8')).decode()
    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'FromName': "pass Culture Pro",
        'Subject': "Liste des utilisateurs créés pour l'activation du pass Culture - {}".format(
            datetime.strftime(now, "%Y-%m-%d")),
        'Attachments': [{"ContentType": "text/csv",
                         "Filename": "liste_des_utilisateurs_{}.csv".format(datetime.strftime(now, "%Y%m%d")),
                         "Content": csv_b64encode}],
        'Html-part': ""
    }


def make_venue_validated_email(venue: Venue) -> Dict:
    html = render_template(
        'mails/venue_validation_confirmation_email.html', venue=venue)
    return {
        'Subject': 'Validation du rattachement du lieu "{}" à votre structure "{}"'.format(venue.name,
                                                                                           venue.managingOfferer.name),
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'FromName': "pass Culture pro",
        'Html-part': html
    }


def compute_email_html_part_and_recipients(email_html_part, recipients: Union[List[str], str]) -> (str, str):
    if isinstance(recipients, list):
        recipients_string = ", ".join(recipients)
    else:
        recipients_string = recipients
    if feature_send_mail_to_users_enabled():
        email_to = recipients_string
    else:
        email_html_part = '<p>This is a test (ENV={environment}).' \
                          ' In production, email would have been sent to : {recipients}</p>{html_part}'.format(
            environment=ENV, recipients=recipients_string, html_part=email_html_part)
        email_to = DEV_EMAIL_ADDRESS
    return email_html_part, email_to


def parse_email_addresses(addresses: str) -> List[str]:
    if not addresses:
        addresses = []
    elif ',' in addresses:
        addresses = [a.strip() for a in addresses.split(',')]
    elif ';' in addresses:
        addresses = [a.strip() for a in addresses.split(';')]
    else:
        addresses = [addresses]

    return [a for a in addresses if a]


def make_offer_creation_notification_email(offer: Offer, author: UserSQLEntity, pro_origin_url: str) -> Dict:
    humanized_offer_id = humanize(offer.id)
    link_to_offer = f'{pro_origin_url}/offres/{humanized_offer_id}'
    html = render_template('mails/offer_creation_notification_email.html', offer=offer, author=author,
                           link_to_offer=link_to_offer)
    location_information = offer.venue.departementCode or 'numérique'
    return {
        'Html-part': html,
        'To': [ADMINISTRATION_EMAIL_ADDRESS],
        'FromEmail': SUPPORT_EMAIL_ADDRESS,
        'FromName': 'pass Culture',
        'Subject': f'[Création d’offre - {location_information}] {offer.product.name}'
    }


def get_event_datetime(stock: StockSQLEntity) -> datetime:
    if stock.offer.venue.departementCode is not None:
        date_in_utc = stock.beginningDatetime
        date_in_tz = utc_datetime_to_department_timezone(date_in_utc,
                                                         stock.offer.venue.departementCode)
    else:
        date_in_tz = stock.beginningDatetime

    return date_in_tz


def make_webapp_user_validation_email(user: UserSQLEntity, app_origin_url: str) -> Dict:
    template = 'mails/webapp_user_validation_email.html'
    email_html = render_template(
        template, user=user, api_url=API_URL, app_origin_url=app_origin_url)
    return {
        'Html-part': email_html,
        'To': user.email,
        'Subject': 'Validation de votre adresse email pour le pass Culture',
        'FromName': 'pass Culture',
        'FromEmail': SUPPORT_EMAIL_ADDRESS if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS
    }


def make_pro_user_validation_email(user: UserSQLEntity, app_origin_url: str) -> Dict:
    return {
        'FromEmail': SUPPORT_EMAIL_ADDRESS if feature_send_mail_to_users_enabled() else DEV_EMAIL_ADDRESS,
        'FromName': 'pass Culture pro',
        'Subject': '[pass Culture pro] Validation de votre adresse email pour le pass Culture',
        'MJ-TemplateID': 778688,
        'MJ-TemplateLanguage': True,
        'Recipients': [
            {
                "Email": user.email,
                "Name": user.publicName
            }
        ],
        'Vars': {
            'nom_structure': user.publicName,
            'lien_validation_mail': f'{app_origin_url}/inscription/validation/{user.validationToken}'
        },
    }
