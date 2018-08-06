""" mailing """

from connectors import api_entreprises

from models.offerer import Offerer
from models.pc_object import PcObject
from models.user_offerer import UserOfferer

import os
from datetime import datetime
from pprint import pformat

import requests
from flask import current_app as app, render_template

from utils.config import API_URL, ENV, IS_DEV, IS_STAGING
from utils.date import format_datetime, utc_datetime_to_dept_timezone

MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')

if MAILJET_API_KEY is None or MAILJET_API_KEY == '':
    raise ValueError("Missing environment variable MAILJET_API_KEY")

if MAILJET_API_SECRET is None or MAILJET_API_SECRET == '':
    raise ValueError("Missing environment variable MAILJET_API_SECRET")

def send_final_booking_recap_email(stock):
    if len(stock.bookings) == 0:
        print("Not sending recap for  " + stock + " as it has no bookings")
    email = make_final_recap_email_for_stock_with_event(stock)
    venue = stock.resolvedOffer.venue
    recipients = [venue.bookingEmail, 'passculture@beta.gouv.fr']

    if IS_DEV or IS_STAGING:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                             + ", ".join(recipients) \
                             + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'
    else:
        email['To'] = ", ".join(recipients)
    print('EMAIL', email['To'])

    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: " + pformat(vars(mailjet_result)))

    stock.bookingRecapSent = datetime.utcnow()
    PcObject.check_and_save(stock)


def send_booking_recap_emails(stock, booking):
    email = make_booking_recap_email(stock, booking)
    venue = stock.resolvedOffer.venue
    recipients = [venue.bookingEmail, 'passculture@beta.gouv.fr']

    if IS_DEV or IS_STAGING:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                             + ", ".join(recipients) \
                             + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'
    else:
        email['To'] = ", ".join(recipients)
    print('EMAIL', email['To'])

    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: " + pformat(vars(mailjet_result)))


def send_booking_confirmation_email_to_user(booking, is_cancellation=False):
    email = make_user_booking_recap_email(booking, is_cancellation)
    recipients = [booking.user.email]

    if IS_DEV or IS_STAGING:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                             + ", ".join(recipients) \
                             + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'
    else:
        email['To'] = ", ".join(recipients)
    print('EMAIL', email['To'])

    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: " + pformat(vars(mailjet_result)))


def make_final_recap_email_for_stock_with_event(stock):
    venue = stock.resolvedOffer.venue
    date_in_tz = _get_event_datetime(stock)
    formatted_datetime = format_datetime(date_in_tz)
    email_subject = '[Reservations] Récapitulatif pour {} le {}'.format(stock.eventOccurrence.offer.event.name,
                                                                        formatted_datetime)
    email_html = render_template('offerer_final_recap_email.html',
                                 number_of_bookings=len(stock.bookings),
                                 stock_name=stock.eventOccurrence.offer.event.name,
                                 stock_date_time=formatted_datetime,
                                 venue_name=venue.name,
                                 venue_address=venue.address,
                                 venue_postal_code=venue.postalCode,
                                 venue_city=venue.city,
                                 stock_bookings=stock.bookings)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def make_booking_recap_email(stock, booking):
    venue = booking.stock.resolvedOffer.venue
    user = booking.user

    if stock.eventOccurrence is None:
        stock_name = stock.offer.thing.name
        email_subject = '[Reservations] Nouvelle reservation pour {}'.format(stock_name)
        formatted_datetime=None
    else:
        date_in_tz = _get_event_datetime(stock)
        formatted_datetime = format_datetime(date_in_tz)
        stock_name = stock.eventOccurrence.offer.event.name
        email_subject = '[Reservations] Nouvelle reservation pour {} le {}'.format(stock_name,
                                                                                   formatted_datetime)

    email_html = render_template('offerer_booking_recap_email.html',
                                 number_of_bookings=len(stock.bookings),
                                 stock_name=stock_name,
                                 stock_date_time=formatted_datetime,
                                 venue_name=venue.name,
                                 venue_address=venue.address,
                                 venue_postal_code=venue.postalCode,
                                 venue_city=venue.city,
                                 stock_bookings=stock.bookings,
                                 user_name=user.publicName,
                                 user_email=user.email)

    print(email_html)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def write_object_validation_email(*objects_to_validate, get_by_siren=api_entreprises.get_by_siren):
    user_offerers = []
    offerers = []
    users_vars_user_offerer = []
    offerers_vars_user_offerer = []
    offerers_vars_offerer = []
    offerers_api = []
    classes_to_validate = []
    for obj in objects_to_validate:
        classes_to_validate.append(obj.__class__.__name__)
        if isinstance(obj, UserOfferer):
            vars_obj_user = vars(obj.user)
            vars_obj_user.pop('clearTextPassword', None)
            user_offerers.append(obj)
            user_vars = pformat(vars_obj_user)
            offerer_vars_user_offerer = pformat(vars(obj.offerer))
            users_vars_user_offerer.append(user_vars)
            offerers_vars_user_offerer.append(offerer_vars_user_offerer)
        elif isinstance(obj, Offerer):
            offerer_vars_offerer = pformat(vars(obj))
            offerers_vars_offerer.append(offerer_vars_offerer)
            api_entreprise_response = get_by_siren(obj)
            if api_entreprise_response.status_code != 200:
                raise ValueError('Error getting API entreprise DATA for SIREN : '
                                 + obj.siren)
            offerers_api.append(api_entreprise_response.json())
            offerers.append(obj)
        else:
            raise ValueError("Unexpected object type in"
                             + " maybe_send_pro_validation_email : "
                             + obj.__class__.__name__)

    token = obj.validationToken


    email_html = render_template('validation_email.html',
                                 users_offerers_vars=zip(users_vars_user_offerer, offerers_vars_user_offerer),
                                 offerer_information=zip(offerers_vars_offerer, offerers_api),
                                 api_url=API_URL,
                                 joined_classes_to_validate=",".join(classes_to_validate),
                                 token=token)


    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr',
        'Subject': "Inscription PRO à valider",
        'Html-part': email_html,
        'To': 'passculture-dev@beta.gouv.fr' if IS_DEV or IS_STAGING
        else 'passculture@beta.gouv.fr'
    }


def maybe_send_offerer_validation_email(*objects_to_validate):
    unvalidated_objects = [o for o in objects_to_validate if not o.isValidated]
    if len(unvalidated_objects) == 0:
        return
    email = write_object_validation_email(*unvalidated_objects)
    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception(": " + pformat(vars(mailjet_result)))


def send_dev_email(subject, html_text):
    email = {
        'FromName': 'Pass Culture Dev',
        'FromEmail': 'passculture-dev@beta.gouv.fr',
        'Subject': subject,
        'Html-part': html_text,
        'To': 'passculture-dev@beta.gouv.fr'
    }
    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: " + pformat(vars(mailjet_result)))


def make_user_booking_recap_email(booking, is_cancellation=False):
    stock = booking.stock
    user = booking.user
    if is_cancellation:
        email_html, email_subject = _generate_cancellation_email_html_and_subject(user,
                                                                                  stock)
    else:
        email_html, email_subject = _generate_reservation_email_html_subject(booking)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture-dev@beta.gouv.fr' if IS_DEV or IS_STAGING else 'passculture@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def get_contact(user):
    return app.mailjet_client.contact.get(user.email).json()['Data'][0]


def subscribe_newsletter(user):
    if IS_DEV or IS_STAGING:
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


def _generate_reservation_email_html_subject(booking):
    stock = booking.stock
    user = booking.user
    venue = stock.resolvedOffer.venue
    stock_description = _get_stock_description(stock)
    if stock.eventOccurrence == None:
        email_subject = 'Confirmation de votre commande pour {}'.format(stock_description)
        email_html = render_template('user_confirmation_email_thing.html',
                                     user_public_name=user.publicName,
                                     booking_token=booking.token,
                                     thing_name=stock.resolvedOffer.thing.name,
                                     thing_reference=stock.resolvedOffer.thing.idAtProviders,
                                     venue_name=venue.name)
    else:
        date_in_tz = _get_event_datetime(stock)
        formatted_date_time = format_datetime(date_in_tz)
        email_subject = 'Confirmation de votre réservation pour {}'.format(stock_description)
        email_html = render_template('user_confirmation_email_event.html',
                                     user_public_name=user.publicName,
                                     booking_token=booking.token,
                                     event_occurrence_name=stock.eventOccurrence.offer.event.name,
                                     formatted_date_time=formatted_date_time,
                                     venue_name=venue.name,
                                     venue_address=venue.address,
                                     venue_postalCode=venue.postalCode,
                                     venue_city=venue.city
                                     )

    return email_html, email_subject


def _generate_cancellation_email_html_and_subject(user, stock):
    venue = stock.resolvedOffer.venue
    if stock.eventOccurrence == None:
        email_subject = 'Annulation de votre commande pour {}'.format(stock.resolvedOffer.thing.name)
        email_html = render_template('user_cancellation_email_thing.html',
                                     user_public_name=user.publicName,
                                     thing_name=stock.resolvedOffer.thing.name,
                                     thing_reference=stock.resolvedOffer.thing.idAtProviders,
                                     venue_name=venue.name)
    else:
        date_in_tz = _get_event_datetime(stock)
        formatted_date_time = format_datetime(date_in_tz)
        email_html = render_template('user_cancellation_email_event.html',
                                     user_public_name=user.publicName,
                                     event_occurrence_name=stock.eventOccurrence.offer.event.name,
                                     venue_name=venue.name,
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
