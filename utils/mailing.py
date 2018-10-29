""" mailing """
import base64
import os
from datetime import datetime
from pprint import pformat

from flask import current_app as app, render_template

from connectors import api_entreprises
from models import RightsType
from repository.booking_queries import find_all_ongoing_bookings_by_stock
from repository.features import feature_send_mail_to_users_enabled
from repository.user_offerer_queries import find_user_offerer_email
from utils.config import API_URL
from utils.date import format_datetime, utc_datetime_to_dept_timezone

MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')

if MAILJET_API_KEY is None or MAILJET_API_KEY == '':
    raise ValueError("Missing environment variable MAILJET_API_KEY")

if MAILJET_API_SECRET is None or MAILJET_API_SECRET == '':
    raise ValueError("Missing environment variable MAILJET_API_SECRET")


class MailServiceException(Exception):
    pass


def check_if_email_sent(mail_result):
    if mail_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mail_result)))


def make_batch_cancellation_email(bookings, cancellation_case):
    booking = next(iter(bookings))
    offer_name = booking.stock.resolvedOffer.eventOrThing.name
    email_html = render_template('mails/offerer_batch_cancellation_email.html',
                                 offer_name=offer_name, bookings=bookings, cancellation_case=cancellation_case)
    email_subject = 'Annulation de réservations pour %s' % offer_name
    return {
        'FromName': 'pass Culture pro',
        'FromEmail': 'passculture@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def make_final_recap_email_for_stock_with_event(stock):
    booking_is_on_event = stock.eventOccurrence is not None
    venue = stock.resolvedOffer.venue
    date_in_tz = _get_event_datetime(stock)
    formatted_datetime = format_datetime(date_in_tz)
    email_subject = '[Réservations] Récapitulatif pour {} le {}'.format(stock.eventOccurrence.offer.event.name,
                                                                        formatted_datetime)
    stock_bookings = find_all_ongoing_bookings_by_stock(stock)
    email_html = render_template('mails/offerer_recap_email.html',
                                 is_final=True,
                                 booking_is_on_event=booking_is_on_event,
                                 number_of_bookings=len(stock_bookings),
                                 stock_name=stock.eventOccurrence.offer.event.name,
                                 stock_date_time=formatted_datetime,
                                 venue=venue,
                                 stock_bookings=stock_bookings)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def make_offerer_booking_recap_email_after_user_action(booking, is_cancellation=False):
    venue = booking.stock.resolvedOffer.venue
    user = booking.user
    stock_bookings = find_all_ongoing_bookings_by_stock(booking.stock)
    stock_name = booking.stock.resolvedOffer.eventOrThing.name
    booking_is_on_event = booking.stock.eventOccurrence is not None

    if booking_is_on_event:
        date_in_tz = _get_event_datetime(booking.stock)
        formatted_datetime = format_datetime(date_in_tz)
        email_subject = '[Réservations] Nouvelle réservation pour {} - {}'.format(stock_name,
                                                                                  formatted_datetime)
    else:
        email_subject = '[Réservations] Nouvelle réservation pour {}'.format(stock_name)
        formatted_datetime = None
    email_html = render_template('mails/offerer_recap_email_after_user_action.html',
                                 is_final=False,
                                 is_cancellation=is_cancellation,
                                 booking_is_on_event=booking_is_on_event,
                                 number_of_bookings=len(stock_bookings),
                                 stock_name=stock_name,
                                 stock_date_time=formatted_datetime,
                                 venue=venue,
                                 stock_bookings=stock_bookings,
                                 user_name=user.publicName,
                                 user_email=user.email)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def write_object_validation_email(offerer, user_offerer, get_by_siren=api_entreprises.get_by_siren):
    vars_obj_user = vars(user_offerer.user)
    vars_obj_user.pop('clearTextPassword', None)
    api_entreprise = get_by_siren(offerer).json()

    email_html = render_template('mails/internal_validation_email.html',
                                 user_offerer=user_offerer,
                                 user_vars=pformat(vars_obj_user),
                                 offerer=offerer,
                                 offerer_vars_user_offerer=pformat(vars(user_offerer.offerer)),
                                 offerer_vars=pformat(vars(offerer)),
                                 api_entreprise=pformat(api_entreprise),
                                 api_url=API_URL)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr',
        'Subject': "%s - inscription / rattachement PRO à valider : %s" % (
            user_offerer.user.departementCode, offerer.name),
        'Html-part': email_html,
        'To': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr'
    }


def make_offerer_driven_cancellation_email_for_user(booking):
    offer_name = booking.stock.resolvedOffer.eventOrThing.name
    offerer_name = booking.stock.resolvedOffer.venue.managingOfferer.name
    booking_value = booking.amount * booking.quantity
    booking_is_on_event = booking.stock.eventOccurrence is not None
    formatted_datetime = None
    commande_ou_reservation = 'réservation' if booking_is_on_event else 'commande'
    if booking_is_on_event:
        date_in_tz = _get_event_datetime(booking.stock)
        formatted_datetime = format_datetime(date_in_tz)

    email_html = render_template('mails/user_cancellation_by_offerer_email.html',
                                 booking_is_on_event=booking_is_on_event,
                                 user=booking.user,
                                 offer_name=offer_name,
                                 event_date=formatted_datetime,
                                 offerer_name=offerer_name,
                                 booking_value=booking_value
                                 )

    email_subject = 'Votre {} pour {}, proposé par {} a été annulée par l\'offreur'.format(commande_ou_reservation,
                                                                                           offer_name, offerer_name)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def make_offerer_driven_cancellation_email_for_offerer(booking):
    stock_name = booking.stock.resolvedOffer.eventOrThing.name
    venue = booking.stock.resolvedOffer.venue
    user_name = booking.user.publicName
    user_email = booking.user.email
    email_subject = 'Confirmation de votre annulation de réservation pour {}, proposé par {}'.format(stock_name,
                                                                                                     venue.name)
    ongoing_stock_bookings = find_all_ongoing_bookings_by_stock(booking.stock)
    stock_date_time = None
    booking_is_on_event = booking.stock.eventOccurrence is not None
    if booking_is_on_event:
        date_in_tz = _get_event_datetime(booking.stock)
        stock_date_time = format_datetime(date_in_tz)
    email_html = render_template('mails/offerer_recap_email_after_offerer_cancellation.html',
                                 is_final=False,
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
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def make_user_booking_recap_email(booking, is_cancellation=False):
    stock = booking.stock
    user = booking.user
    if is_cancellation:
        email_html, email_subject = _generate_user_driven_cancellation_email_for_user(user,
                                                                                      stock)
    else:
        email_html, email_subject = _generate_reservation_email_html_subject(booking)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def make_reset_password_email(user, app_origin_url):
    email_html = render_template(
        'mails/user_reset_password_email.html',
        user=user,
        app_origin_url=app_origin_url
    )

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr',
        'Subject': 'Réinitialisation de votre mot de passe',
        'Html-part': email_html,
        'To': user.email
    }


def make_validation_confirmation_email(user_offerer, offerer):
    user_offerer_email = None
    user_offerer_rights = None
    if user_offerer is not None:
        user_offerer_email = find_user_offerer_email(user_offerer.id)
        if user_offerer.rights == RightsType.admin:
            user_offerer_rights = 'administrateur'
        else:
            user_offerer_rights = 'éditeur'
    email_html = render_template(
        'mails/user_offerer_and_offerer_validation_confirmation_email.html',
        user_offerer_email=user_offerer_email,
        offerer=offerer,
        user_offerer_rights=user_offerer_rights
    )
    if user_offerer and offerer:
        subject = 'Validation de votre structure et de compte {} rattaché'.format(user_offerer_rights)
    elif user_offerer:
        subject = 'Validation de compte {} rattaché à votre structure'.format(user_offerer_rights)
    else:
        subject = 'Validation de votre structure'
    return {
        'FromName': 'pass Culture pro',
        'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr',
        'Subject': subject,
        'Html-part': email_html,
    }


def make_venue_validation_email(venue):
    html = render_template('mails/venue_validation_email.html', venue=venue, api_url=API_URL)
    return {
        'FromEmail': 'passculture@beta.gouv.fr',
        'FromName': 'pass Culture',
        'To': 'passculture@beta.gouv.fr',
        'Subject': '{} - rattachement de lieu pro à valider : {}'.format(venue.departementCode, venue.name),
        'Html-part': html
    }


def make_user_validation_email(user, is_webapp):
    if is_webapp:
        template = 'mails/webapp_user_validation_email.html'
        from_name = 'pass Culture'
    else:
        template = 'mails/pro_user_validation_email.html'
        from_name = 'pass Culture pro'
    email_html = render_template(template, user=user, api_url=API_URL)
    return {'Html-part': email_html,
            'To': user.email,
            'Subject': 'Validation de votre adresse email pour le pass Culture',
            'FromName': from_name,
            'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr'}


def get_contact(user):
    return app.mailjet_client.contact.get(user.email).json()['Data'][0]


def subscribe_newsletter(user):
    if not feature_send_mail_to_users_enabled():
        print("Subscription in DEV or STAGING mode is disabled")
        return

    try:
        contact = get_contact(user)
    except:
        contact_data = {
            'Email': user.email,
            'Name': user.publicName
        }
        contact_json = app.mailjet_client.contact.create(data=contact_data).json()
        contact = contact_json['Data'][0]

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


def make_payment_transaction_email(xml: str) -> dict:
    now = datetime.utcnow()
    xml_b64encode = base64.b64encode(xml.encode())
    return {
        'From': {"Email": "passculture@beta.gouv.fr",
                 "Name": "pass Culture Pro"},
        'To': [{"Email": "passculture-dev@beta.gouv.fr",
                "Name": "Compta pass Culture"}],
        'Subject': "Virements pass Culture Pro - {}".format(datetime.strftime(now, "%Y-%m-%d")),
        'Attachments': [{"ContentType": "text/xml",
                         "Filename": "transaction_banque_de_france_{}.xml".format(datetime.strftime(now, "%Y%m%d")),
                         "Base64Content": xml_b64encode}]}


def make_venue_validation_confirmation_email(venue):
    html = render_template('mails/venue_validation_confirmation_email.html', venue=venue)
    return {
        'Subject': 'Validation du rattachement du lieu "{}" à votre structure "{}"'.format(venue.name,
                                                                                           venue.managingOfferer.name),
        'FromEmail': "passculture@beta.gouv.fr",
        'FromName': "pass Culture pro",
        'Html-part': html
    }


def _generate_reservation_email_html_subject(booking):
    stock = booking.stock
    user = booking.user
    venue = stock.resolvedOffer.venue
    stock_description = _get_stock_description(stock)
    booking_is_on_event = stock.eventOccurrence == None
    if booking_is_on_event:
        email_subject = 'Confirmation de votre commande pour {}'.format(stock_description)
        email_html = render_template('mails/user_confirmation_email_thing.html',
                                     user=user,
                                     booking_token=booking.token,
                                     thing_name=stock.resolvedOffer.thing.name,
                                     thing_reference=stock.resolvedOffer.thing.idAtProviders,
                                     venue=venue)
    else:
        date_in_tz = _get_event_datetime(stock)
        formatted_date_time = format_datetime(date_in_tz)
        email_subject = 'Confirmation de votre réservation pour {}'.format(stock_description)
        email_html = render_template('mails/user_confirmation_email_event.html',
                                     user=user,
                                     booking_token=booking.token,
                                     event_occurrence_name=stock.eventOccurrence.offer.event.name,
                                     formatted_date_time=formatted_date_time,
                                     venue=venue
                                     )

    return email_html, email_subject


def _generate_user_driven_cancellation_email_for_user(user, stock):
    venue = stock.resolvedOffer.venue
    if stock.eventOccurrence == None:
        email_subject = 'Annulation de votre commande pour {}'.format(stock.resolvedOffer.thing.name)
        email_html = render_template('mails/user_cancellation_email_thing.html',
                                     user=user,
                                     thing_name=stock.resolvedOffer.thing.name,
                                     thing_reference=stock.resolvedOffer.thing.idAtProviders,
                                     venue=venue)
    else:
        date_in_tz = _get_event_datetime(stock)
        formatted_date_time = format_datetime(date_in_tz)
        email_html = render_template('mails/user_cancellation_email_event.html',
                                     user=user,
                                     event_occurrence_name=stock.eventOccurrence.offer.event.name,
                                     venue=venue,
                                     formatted_date_time=formatted_date_time)
        email_subject = 'Annulation de votre réservation pour {} le {}'.format(
            stock.eventOccurrence.offer.event.name,
            formatted_date_time
        )
    return email_html, email_subject


def _get_event_datetime(stock):
    date_in_utc = stock.eventOccurrence.beginningDatetime
    date_in_tz = utc_datetime_to_dept_timezone(date_in_utc,
                                               stock.eventOccurrence.offer.venue.departementCode)
    return date_in_tz


def _get_stock_description(stock):
    if stock.eventOccurrence:
        date_in_tz = _get_event_datetime(stock)
        description = '{} le {}'.format(stock.eventOccurrence.offer.event.name,
                                        format_datetime(date_in_tz))
    elif stock.resolvedOffer.thing:
        description = str(stock.resolvedOffer.thing.name)

    return description
