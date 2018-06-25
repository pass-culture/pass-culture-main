""" mailing """
from datetime import datetime
from dateutil import tz
from flask import current_app as app
from mailjet_rest import Client
import os
from pprint import pformat
import requests

from utils.date import format_datetime
from utils.config import ENV, IS_DEV, IS_STAGING

MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')

Offer = app.model.Offer


def init_mailjet():
    if MAILJET_API_KEY is None or MAILJET_API_KEY=='':
        raise ValueError("Missing environment variable MAILJET_API_KEY")

    if MAILJET_API_SECRET is None or MAILJET_API_SECRET=='':
        raise ValueError("Missing environment variable MAILJET_API_SECRET")

    return Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET),
                  version='v3')


def send_booking_recap_emails(offer, booking=None, is_cancellation=False):
    if booking is None and len(offer.bookings)==0:
        print("Not sending recap for  "+offer+" as it has no bookings")
    mailjet = init_mailjet()

    email = make_booking_recap_email(offer, booking, is_cancellation)

    recipients = [offer.offerer.bookingEmail, 'passculture@beta.gouv.fr']


    if IS_DEV or IS_STAGING:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV)\
                              + ", ".join(recipients)\
                              + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'
    else:
        email['To'] = ", ".join(recipients)
    print('EMAIL', email['To'])

    mailjet_result = mailjet.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: "+pformat(vars(mailjet_result)))

    if booking is None:
        offer.bookingRecapSent = datetime.utcnow()
        app.model.PcObject.check_and_save(offer)


def make_booking_recap_email(offer, booking=None, is_cancellation=False):
    email_html = '<html><body>'
    email_html += '<p>Cher partenaire Pass Culture,</p>'

    if offer.eventOccurence:
        date = offer.eventOccurence.beginningDatetime
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('UTC-3' if offer.eventOccurence.venue.departementCode == '97'
                                   else 'Europe/Paris')
        utc = date.replace(tzinfo=from_zone)
        in_tz = utc.astimezone(to_zone)
        description = '%s le %s' % (offer.eventOccurence.event.name,
                                    format_datetime(in_tz))
    elif offer.thing:
        description = '%s (Ref: %s)' % (offer.thing.name, offer.thing.idAtProviders)

    email_subject = '[Reservations] '
    if booking is not None:
        user = booking.user
        email_html += '<p>%s (%s)' % (user.publicName, user.email)
        if is_cancellation:
            email_subject += 'Annulation pour ' + description
            email_html += ' vient d\'annuler sa réservation'
        else:
            email_subject += 'Nouvelle reservation pour ' + description
            email_html += ' vient de faire une nouvelle réservation'
        email_html += '</p>'
    else:
        email_subject += 'Récapitulatif pour ' + description

    if offer.bookingLimitDatetime is not None:
        if offer.bookingLimitDatetime < datetime.utcnow():
            email_html += '<p>Voici le récapitulatif final des réservations (total '
        else:
            email_html += '<p>Voici le récapitulatif des réservations à ce jour (total '
        email_html += '%s) pour %s</p>' % (len(offer.bookings), description)

        if len(offer.bookings) > 0:
            email_html += '<table>'
            email_html += '<tr><th>Nom ou pseudo</th>'\
                            + '<th>Email</th>'\
                            + '<th>Code réservation</th>'\
                          '</tr>'
            for a_booking in offer.bookings:
                email_html += '<tr>'\
                              + '<td>%s</td>' % a_booking.user.publicName\
                              + '<td>%s</td>' % a_booking.user.email\
                              + '<td>%s</td>' % a_booking.token\
                            + '</tr>'
            email_html += '</table>'
        else:
            email_html += '<p>Aucune réservation</p>'

    email_html += '</body></html>'

    return {
             'FromName': 'Pass Culture',
             'FromEmail': 'passculture@beta.gouv.fr',
             'Subject': email_subject,
             'Html-part': email_html,
           }


def send_pro_validation_email(user, offerer):
    to = 'passculture-dev@beta.gouv.fr' if IS_DEV or IS_STAGING\
         else 'passculture@beta.gouv.fr'
    mailjet = init_mailjet()
    email_html = '<html><body>'
    email_html += "<p>Inscription ou rattachement PRO à valider</p>"
    if user.isValidated:
        email_html += "<h3>Personne (existante): </h3>"
    else:
        email_html += "<h3>Personne (nouvelle, à valider + valider le rattachement à l'organisation): </h3>"
    email_html += pformat(vars(user))
    if offerer.isValidated:
        email_html += "<h3>Organisation (existante): </h3>"
    else:
        email_html += "<h3>Organisation (nouvelle, à valider + valider le rattachement à la personne): </h3>"
    email_html += pformat(vars(offerer))

    if offerer.siren:
        email_html += "<h3>Infos API entreprise : </h3>"
        api_entreprise = requests.get("https://sirene.entreprise.api.gouv.fr/v1/SIREN/"+offerer.siren)
        if api_entreprise.status_code == 200:
            email_html += pformat(vars(api_entreprise.json()))
        else:
            raise ValueError('Error getting API entreprise DATA for SIREN : '
                             + offerer.siren)

    email_html += "Pour valider, "
    token = offerer.validationToken if user.isValidated\
            else user.validationToken
    email_html += "<a href='/validate?token=" + token + "'>cliquez ici</a>"

    email = {
             'FromName': 'Pass Culture',
             'FromEmail': 'passculture@beta.gouv.fr',
             'Subject': "Inscription PRO à valider",
             'Html-part': email_html,
             'To': [to]
           }
    mailjet_result = mailjet.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: "+pformat(vars(mailjet_result)))
