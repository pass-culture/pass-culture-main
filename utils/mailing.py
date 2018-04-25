from datetime import datetime
from flask import current_app as app
from mailjet_rest import Client
from pprint import pformat
from utils.config import ENV, IS_DEV, IS_STAGING
import os

MAILJET_API_KEY = os.environ['MAILJET_API_KEY']
MAILJET_API_SECRET = os.environ['MAILJET_API_SECRET']

Offer = app.model.Offer


def send_booking_recap_emails(offer, booking=None, is_cancellation=False):
    if MAILJET_API_KEY is None or MAILJET_API_KEY=='':
        raise ValueError("Missing environment variable MAILJET_API_KEY")

    if MAILJET_API_SECRET is None or MAILJET_API_SECRET=='':
        raise ValueError("Missing environment variable MAILJET_API_SECRET")

    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET),
                     version='v3')

    email = make_booking_recap_email(offer, booking, is_cancellation)

    recipients = [offer.offerer.bookingEmail, 'pass@culture.gouv.fr']

    if IS_DEV or IS_STAGING:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : '
                              + ", ".join(recipients)
                              + '</p>' + email['Html-part']) % ENV
        email['To'] = 'passculture-dev@beta.gouv.fr'
    else:
        email['To'] = recipients

    from pprint import pprint
    pprint(email)

    mailjet_result = mailjet.send.create(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: "+pformat(vars(mailjet_result)))

    if booking is None:
        offer.bookingRecapSent = datetime.now()
        app.model.PcObject.check_and_save(offer)


def make_booking_recap_email(offer, booking=None, is_cancellation=False):
    email_html = '<html><body>'
    email_html += '<p>Cher partenaire Pass Culture,</p>'

    email_subject = '[Reservations] '
    if booking is not None:
        user = booking.user
        email_html += '<p>%s (%s)' % (user.publicName, user.email)
        if is_cancellation:
            email_subject += 'Annulation de reservation pour '
            email_html += ' vient d\'annuler sa réservation'
        else:
            email_subject += 'Nouvelle reservation pour '
            email_html += ' vient de faire une nouvelle réservation'
        if offer.eventOccurence:
            email_subject += '%s le %s' % (offer.eventOccurence.event.name,
                                           offer.eventOccurence.beginningDatetime.strftime('%c'))
        elif offer.thing:
            email_subject += '%s (Ref: %s)' % (offer.thing.name, offer.thing.idAtProviders)
        email_html += '</p>'
    else:
        email_subject += 'Récapitulatif de réservation pour '

    if offer.bookingLimitDatetime is not None:
        if offer.bookingLimitDatetime < datetime.now():
            email_html += '<h2>Récapitulatif final des réservations (total '
        else:
            email_html += '<h2>Récapitulatif des réservations à ce jour (total '
        email_html += '%s)</h2>' % len(offer.bookings)

        email_html += '<table>'
        email_html += '<tr><th>Nom ou pseudo</th><th>Email</th></tr>'
        for a_booking in offer.bookings:
            email_html += '<tr>'\
                          + '<td>%s</td>' % a_booking.user.publicName\
                          + '<td>%s</td>' % a_booking.user.email\
                        + '</tr>'
        email_html += '</table>'
    email_html += '</body></html>'

    return {
             'FromName': 'Pass Culture',
             'FromEmail': 'passculture@beta.gouv.fr',
             'Subject': email_subject,
             'Html-part': email_html,
           }

