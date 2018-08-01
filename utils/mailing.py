""" mailing """

from models.offerer import Offerer
from models.pc_object import PcObject
from models.user_offerer import UserOfferer

import os
from datetime import datetime
from pprint import pformat

import requests
from flask import current_app as app

from utils.config import API_URL, ENV, IS_DEV, IS_STAGING
from utils.date import format_datetime, utc_datetime_to_dept_timezone

MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')

if MAILJET_API_KEY is None or MAILJET_API_KEY == '':
    raise ValueError("Missing environment variable MAILJET_API_KEY")

if MAILJET_API_SECRET is None or MAILJET_API_SECRET == '':
    raise ValueError("Missing environment variable MAILJET_API_SECRET")


def send_booking_recap_emails(stock, booking=None, is_cancellation=False):
    if booking is None and len(stock.bookings)==0:
        print("Not sending recap for  "+stock+" as it has no bookings")

    email = make_booking_recap_email(stock, booking, is_cancellation)

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

    if booking is None:
        stock.bookingRecapSent = datetime.utcnow()
        PcObject.check_and_save(stock)


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


def _get_venue_description(venue):
    return ', proposé par {} (Adresse : {}, {} {}).'.format(venue.name,
                                                            venue.address,
                                                            venue.postalCode,
                                                            venue.city)


def make_booking_recap_email(stock, booking=None, is_cancellation=False):
    if booking == None:
        venue = stock.resolvedOffer.venue
    else:
        venue = booking.stock.resolvedOffer.venue
    email_html = '<html><body>'
    email_html += '<p>Cher partenaire Pass Culture,</p>'

    stock_description = _get_stock_description(stock)
    venue_description = _get_venue_description(venue)

    email_subject = '[Reservations] '
    if booking is not None:
        user = booking.user
        email_html += '<p>%s (%s)' % (user.publicName, user.email)
        if is_cancellation:
            email_subject += 'Annulation pour ' + stock_description
            email_html += ' vient d\'annuler sa réservation'
        else:
            email_subject += 'Nouvelle reservation pour ' + stock_description
            email_html += ' vient de faire une nouvelle réservation.</p>'
    else:
        email_subject += 'Récapitulatif pour ' + stock_description

    if stock.bookingLimitDatetime is not None:
        if stock.bookingLimitDatetime < datetime.utcnow():
            email_html += '<p>Voici le récapitulatif final des réservations (total '
        else:
            email_html += '<p>Voici le récapitulatif des réservations à ce jour (total '
        email_html += '%s) pour %s' % (len(stock.bookings), stock_description)

        if venue is not None:
            email_html += venue_description

        if len(stock.bookings) > 0:
            email_html += '</p><table>'
            email_html += '<tr><th>Nom ou pseudo</th>' \
                          + '<th>Email</th>' \
                          + '<th>Code réservation</th>' \
                            '</tr>'
            for a_booking in stock.bookings:
                email_html += '<tr>' \
                              + '<td>%s</td>' % a_booking.user.publicName \
                              + '<td>%s</td>' % a_booking.user.email \
                              + '<td>%s</td>' % a_booking.token \
                              + '</tr>'
            email_html += '</table>'
        else:
            email_html += '<p>Aucune réservation</p>'

    email_html += '</body></html>'

    return {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture-dev@beta.gouv.fr' if IS_DEV or IS_STAGING else 'passculture@beta.gouv.fr',
        'Subject': email_subject,
        'Html-part': email_html,
    }


def _get_stock_description(stock):
    if stock.eventOccurrence:
        date_in_tz = _get_event_datetime(stock)
        description = '{} le {}'.format(stock.eventOccurrence.offer.event.name,
                                        format_datetime(date_in_tz))
    elif stock.resolvedOffer.thing:
        description = str(stock.resolvedOffer.thing.name)

    return description


def maybe_send_offerer_validation_email(user, *objects_to_validate):
    email_html = '<html><body>'
    email_html += "<p>Inscription ou rattachement PRO à valider</p>"

    classes_to_validate = []
    for obj in objects_to_validate:
        if obj.isValidated:
            continue
        token = obj.validationToken  # objects validated together are supposed to have the same token
        classes_to_validate.append(obj.__class__.__name__)
        if isinstance(obj, UserOfferer):
            email_html += "<h3>Nouveau Rattachement : </h3>"
            email_html += "<h4>Utilisateur: </h4>"
            email_html += "<pre>" + pformat(vars(obj.user)) + "</pre>"
            email_html += "<h4>Structure: </h4>"
            email_html += "<pre>" + pformat(vars(obj.offerer)) + "</pre>"
        elif isinstance(obj, Offerer):
            email_html += "<h3>Nouvelle Structure : </h3>"
            email_html += "<pre>" + pformat(vars(obj)) + "</pre>"
        else:
            raise ValueError("Unexpected object type in"
                             + " maybe_send_pro_validation_email : "
                             + obj.__class__.__name__)
        if isinstance(obj, Offerer):
            email_html += "<h4>Infos API entreprise : </h4>"
            api_entreprise = requests.get("https://sirene.entreprise.api.gouv.fr/v1/siren/" + obj.siren,
                                          verify=False)  # FIXME: add root cerficate on docker image ?
            if api_entreprise.status_code == 200:
                print(api_entreprise.text)
                email_html += "<pre>" + pformat(api_entreprise.json()) + "</pre>"
            else:
                raise ValueError('Error getting API entreprise DATA for SIREN : '
                                 + obj.siren)

    if len(classes_to_validate) == 0:
        return

    email_html += "Pour valider, "
    email_html += "<a href='" + API_URL + "/validate?" \
                  + "modelNames=" + ",".join(classes_to_validate) \
                  + "&token=" + token + "'>cliquez ici</a>"

    email = {
        'FromName': 'Pass Culture',
        'FromEmail': 'passculture-dev@beta.gouv.fr' if IS_DEV or IS_STAGING else 'passculture@beta.gouv.fr',
        'Subject': "Inscription PRO à valider",
        'Html-part': email_html,
        'To': 'passculture-dev@beta.gouv.fr' if IS_DEV or IS_STAGING else 'passculture@beta.gouv.fr'
    }
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


def _get_event_datetime(stock):
    date_in_utc = stock.eventOccurrence.beginningDatetime
    date_in_tz = utc_datetime_to_dept_timezone(date_in_utc,
                                               stock.eventOccurrence.offer.venue.departementCode)
    return date_in_tz


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
    email_html = '<html><body><p>Cher {},</p>'.format(user.publicName)
    if stock.eventOccurrence == None:
        confirmation_nature = 'commande'
    else:
        confirmation_nature = 'réservation'
    email_subject = 'Confirmation de votre {} pour {}'.format(confirmation_nature,
                                                              stock_description)
    email_html += '<p>Nous vous confirmons votre {} pour {}'.format(confirmation_nature,
                                                                    stock_description)
    if stock.eventOccurrence == None:
        email_html += ' (Ref: {}),'.format(stock.resolvedOffer.thing.idAtProviders)
        email_html += ' proposé par {}.'.format(venue.name)
    else:
        email_html += _get_venue_description(venue)
    email_html += '</p><p>Votre code de réservation est le {}.</p>'.format(booking.token)
    email_html += '<p>Cordialement,</p><p>L\'équipe pass culture</p></body></html>'
    return email_html, email_subject


def _generate_cancellation_email_html_and_subject(user, stock):
    venue = stock.resolvedOffer.venue
    email_html = '<html><body><p>Cher {},</p>'.format(user.publicName)
    if stock.eventOccurrence == None:
        confirmation_nature = 'commande'
        stock_name = stock.resolvedOffer.thing.name
        thing_reference = ' (Ref: {})'.format(stock.resolvedOffer.thing.idAtProviders)

    else:
        confirmation_nature = 'réservation'
        stock_name = stock.eventOccurrence.offer.event.name

    email_html += '<p>Votre {} pour {}'.format(confirmation_nature,
                                                stock_name)

    if stock.eventOccurrence == None:
        email_html += thing_reference

    email_html += ','
    email_subject = 'Annulation de votre {} pour {}'.format(confirmation_nature,
                                                            stock_name)
    email_html += ' proposé par {}'.format(venue.name)
    if stock.eventOccurrence != None:
        date_in_tz = _get_event_datetime(stock)
        datetime_information = ' le {}'.format(format_datetime(date_in_tz))
        email_html += '{},'.format(datetime_information)
        email_subject += datetime_information
    email_html += ' a bien été annulée.'
    email_html += '</p><p>Cordialement,</p><p>L\'équipe pass culture</p></body></html>'
    return email_html, email_subject


def _get_event_datetime(stock):
    date_in_utc = stock.eventOccurrence.beginningDatetime
    date_in_tz = utc_datetime_to_dept_timezone(date_in_utc,
                                               stock.eventOccurrence.offer.venue.departementCode)
    return date_in_tz
