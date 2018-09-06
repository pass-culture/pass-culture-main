""" mailing """
import os
from datetime import datetime
from pprint import pformat

from flask import current_app as app, render_template

from connectors import api_entreprises
from models.pc_object import PcObject
from repository.features import feature_send_mail_to_users_enabled
from utils.config import API_URL, ENV
from utils.date import format_datetime, utc_datetime_to_dept_timezone

MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')

if MAILJET_API_KEY is None or MAILJET_API_KEY == '':
    raise ValueError("Missing environment variable MAILJET_API_KEY")

if MAILJET_API_SECRET is None or MAILJET_API_SECRET == '':
    raise ValueError("Missing environment variable MAILJET_API_SECRET")


class MailServiceException(Exception):
    pass


def send_final_booking_recap_email(stock):
    if len(stock.bookings) == 0:
        print("Not sending recap for  " + str(stock) + " as it has no bookings")
    email = make_final_recap_email_for_stock_with_event(stock)

    recipients = ['passculture@beta.gouv.fr']
    if stock.resolvedOffer.bookingEmail:
        recipients.append(stock.resolvedOffer.bookingEmail)

    if feature_send_mail_to_users_enabled():
        email['To'] = ", ".join(recipients)
    else:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                             + ", ".join(recipients) \
                             + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'

    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mailjet_result)))

    stock.bookingRecapSent = datetime.utcnow()
    PcObject.check_and_save(stock)


def send_booking_recap_emails(stock, booking):
    email = make_offerer_booking_recap_email_after_user_action(booking)

    recipients = ['passculture@beta.gouv.fr']
    if stock.resolvedOffer.bookingEmail:
        recipients.append(stock.resolvedOffer.bookingEmail)

    if feature_send_mail_to_users_enabled():
        email['To'] = ", ".join(recipients)
    else:

        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                             + ", ".join(recipients) \
                             + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'

    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mailjet_result)))


def send_booking_confirmation_email_to_user(booking, is_cancellation=False):
    email = make_user_booking_recap_email(booking, is_cancellation)
    recipients = [booking.user.email]

    if feature_send_mail_to_users_enabled():
        email['To'] = ", ".join(recipients)
    else:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV) \
                             + ", ".join(recipients) \
                             + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'

    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mailjet_result)))


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


def make_offerer_booking_recap_email_after_user_action(booking, is_cancellation=False):
    venue = booking.stock.resolvedOffer.venue
    user = booking.user
    stock_bookings = [b for b in booking.stock.bookings if not b.isCancelled]
    stock_name = booking.stock.resolvedOffer.eventOrThing.name

    if booking.stock.eventOccurrence is None:
        email_subject = '[Reservations] Nouvelle reservation pour {}'.format(stock_name)
        formatted_datetime = None
    else:
        date_in_tz = _get_event_datetime(booking.stock)
        formatted_datetime = format_datetime(date_in_tz)
        email_subject = '[Reservations] Nouvelle reservation pour {} le {}'.format(stock_name,
                                                                                   formatted_datetime)

    if is_cancellation:
        template_name = 'offerer_cancellation_by_user_email.html'
    else:
        template_name = 'offerer_booking_recap_email.html'
    email_html = render_template(template_name,
                                 number_of_bookings=len(stock_bookings),
                                 stock_name=stock_name,
                                 stock_date_time=formatted_datetime,
                                 venue_name=venue.name,
                                 venue_address=venue.address,
                                 venue_postal_code=venue.postalCode,
                                 venue_city=venue.city,
                                 stock_bookings=stock_bookings,
                                 user_name=user.publicName,
                                 user_email=user.email)

    print(email_html)

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

    email_html = render_template('validation_email.html',
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


def maybe_send_offerer_validation_email(offerer, user_offerer):
    if offerer.isValidated and user_offerer.isValidated:
        return
    email = write_object_validation_email(offerer, user_offerer)
    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mailjet_result)))


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
        raise MailServiceException("Email send failed: " + pformat(vars(mailjet_result)))


def make_offerer_driven_cancellation_email_for_user(booking):
    is_event = booking.stock.resolvedOffer.event
    if is_event:
        email_html, email_subject = _generate_offerer_driven_cancellation_email_for_user_event(booking)
    else:
        email_html, email_subject = _generate_offerer_driven_cancellation_email_for_user_thing(booking)

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def _generate_offerer_driven_cancellation_email_for_user_thing(booking):
    offer_name = booking.stock.resolvedOffer.eventOrThing.name
    offerer_name = booking.stock.resolvedOffer.venue.managingOfferer.name
    booking_value = booking.amount * booking.quantity
    user_public_name = booking.user.publicName
    email_html = render_template('user_cancellation_by_offerer_email_thing.html',
                                 user_public_name=user_public_name,
                                 offer_name=offer_name,
                                 offerer_name=offerer_name,
                                 booking_value=booking_value
                                 )
    email_subject = 'Votre commande pour {}, proposé par {} a été annulée par l\'offreur'.format(offer_name,
                                                                                                 offerer_name)
    return email_html, email_subject


def _generate_offerer_driven_cancellation_email_for_user_event(booking):
    offer_name = booking.stock.resolvedOffer.eventOrThing.name
    offerer_name = booking.stock.resolvedOffer.venue.managingOfferer.name
    booking_value = booking.amount * booking.quantity
    user_public_name = booking.user.publicName
    date_in_tz = _get_event_datetime(booking.stock)
    formatted_datetime = format_datetime(date_in_tz)
    email_html = render_template('user_cancellation_by_offerer_email_event.html',
                                 user_public_name=user_public_name,
                                 offer_name=offer_name,
                                 event_date=formatted_datetime,
                                 offerer_name=offerer_name,
                                 booking_value=booking_value
                                 )
    email_subject = 'Votre réservation pour {}, proposé par {} a été annulée par l\'offreur'.format(offer_name,
                                                                                                    offerer_name)
    return email_html, email_subject


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


def make_reset_password_email(user):
    email_html = render_template(
        'user_reset_password_email.html',
        user_public_name=user.publicName,
        token=user.resetPasswordToken,
        api_url=API_URL
    )

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture@beta.gouv.fr' if feature_send_mail_to_users_enabled() else 'passculture-dev@beta.gouv.fr',
        'Subject': 'Réinitialisation de votre mot de passe',
        'Html-part': email_html,
        'To': user.email
    }


def send_reset_password_email(user):
    email = make_reset_password_email(user)
    mailjet_result = app.mailjet_client.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise MailServiceException("Email send failed: " + pformat(vars(mailjet_result)))


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


def _generate_user_driven_cancellation_email_for_user(user, stock):
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
