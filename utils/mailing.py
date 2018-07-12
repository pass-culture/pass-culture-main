""" mailing """
from datetime import datetime
from flask import current_app as app
from mailjet_rest import Client
import os
from pprint import pformat
import requests

from utils.config import API_URL, ENV, IS_DEV, IS_STAGING
from utils.date import format_datetime, utc_datetime_to_dept_timezone

MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')

Offer = app.model.Offer


if MAILJET_API_KEY is None or MAILJET_API_KEY=='':
    raise ValueError("Missing environment variable MAILJET_API_KEY")

if MAILJET_API_SECRET is None or MAILJET_API_SECRET=='':
    raise ValueError("Missing environment variable MAILJET_API_SECRET")
client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET),
              version='v3')
app.mailjet_client = client
app.mailjet = client.send.create


def send_booking_recap_emails(offer, booking=None, offerer=None, is_cancellation=False):
    if booking is None and len(offer.bookings)==0:
        print("Not sending recap for  "+offer+" as it has no bookings")

    email = make_booking_recap_email(offer, booking, offerer, is_cancellation)

    if offer.venue:
        venue = offer.venue
    else:
        venue = offer.eventOccurence.venue

    recipients = [venue.bookingEmail, 'passculture@beta.gouv.fr']


    if IS_DEV or IS_STAGING:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV)\
                              + ", ".join(recipients)\
                              + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'
    else:
        email['To'] = ", ".join(recipients)
    print('EMAIL', email['To'])

    mailjet_result = app.mailjet(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: "+pformat(vars(mailjet_result)))

    if booking is None:
        offer.bookingRecapSent = datetime.utcnow()
        app.model.PcObject.check_and_save(offer)


def send_booking_confirmation_email_to_user(offer, booking, is_cancellation=False):

    email = make_user_booking_recap_email(offer, booking, is_cancellation)

    recipients = [booking.user.email]

    if IS_DEV or IS_STAGING:
        email['Html-part'] = ('<p>This is a test (ENV=%s). In production, email would have been sent to : ' % ENV)\
                              + ", ".join(recipients)\
                              + '</p>' + email['Html-part']
        email['To'] = 'passculture-dev@beta.gouv.fr'
    else:
        email['To'] = ", ".join(recipients)
    print('EMAIL', email['To'])

    mailjet_result = app.mailjet(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: "+pformat(vars(mailjet_result)))


def _get_offerer_description(offerer):
    return ', proposé par {} (Adresse : {}, {} {}).'.format(offerer.name,
                                                                   offerer.address,
                                                                   offerer.postalCode,
                                                                   offerer.city)


def make_booking_recap_email(offer, booking=None, offerer=None, is_cancellation=False):
    email_html = '<html><body>'
    email_html += '<p>Cher partenaire Pass Culture,</p>'

    offer_description = _get_offer_description(offer)
    offerer_description = _get_offerer_description(offerer)

    email_subject = '[Reservations] '
    if booking is not None:
        user = booking.user
        email_html += '<p>%s (%s)' % (user.publicName, user.email)
        if is_cancellation:
            email_subject += 'Annulation pour ' + offer_description
            email_html += ' vient d\'annuler sa réservation'
        else:
            email_subject += 'Nouvelle reservation pour ' + offer_description
            email_html += ' vient de faire une nouvelle réservation'
        email_html += '</p>'
    else:
        email_subject += 'Récapitulatif pour ' + offer_description

    if offer.bookingLimitDatetime is not None:
        if offer.bookingLimitDatetime < datetime.utcnow():
            email_html += '<p>Voici le récapitulatif final des réservations (total '
        else:
            email_html += '<p>Voici le récapitulatif des réservations à ce jour (total '
        email_html += '%s) pour %s' % (len(offer.bookings), offer_description)

        if offerer is not None:
            email_html += offerer_description

        email_html += '</p>'

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


def _get_offer_description(offer):
    if offer.eventOccurence:
        date_in_utc = offer.eventOccurence.beginningDatetime
        date_in_tz = utc_datetime_to_dept_timezone(date_in_utc,
                                                   offer.eventOccurence.venue.departementCode)
        description = '{} le {}'.format(offer.eventOccurence.event.name,
                                         format_datetime(date_in_tz))
    elif offer.thing:
        description = '{} (Ref: {})'.format(offer.thing.name,
                                             offer.thing.idAtProviders)

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
        if isinstance(obj, app.model.UserOfferer):
            email_html += "<h3>Nouveau Rattachement : </h3>"
            email_html += "<h4>Utilisateur: </h4>"
            email_html += "<pre>"+pformat(vars(obj.user))+"</pre>"
            email_html += "<h4>Structure: </h4>"
            email_html += "<pre>"+pformat(vars(obj.offerer))+"</pre>"
        elif isinstance(obj, app.model.Offerer):
            email_html += "<h3>Nouvelle Structure : </h3>"
            email_html += "<pre>"+pformat(vars(obj))+"</pre>"
        else:
            raise ValueError("Unexpected object type in"
                             + " maybe_send_pro_validation_email : "
                             + obj.__class__.__name__)
        if isinstance(obj, app.model.Offerer):
            email_html += "<h4>Infos API entreprise : </h4>"
            api_entreprise = requests.get("https://sirene.entreprise.api.gouv.fr/v1/siren/"+obj.siren, verify=False)  # FIXME: add root cerficate on docker image ?
            if api_entreprise.status_code == 200:
                print(api_entreprise.text)
                email_html += "<pre>"+pformat(api_entreprise.json())+"</pre>"
            else:
                raise ValueError('Error getting API entreprise DATA for SIREN : '
                                 + obj.siren)

    if len(classes_to_validate) == 0:
        return

    email_html += "Pour valider, "
    email_html += "<a href='" + API_URL +"/validate?"\
                  + "modelNames=" + ",".join(classes_to_validate)\
                  + "&token=" + token + "'>cliquez ici</a>"

    email = {
             'FromName': 'Pass Culture',
             'FromEmail': 'passculture@beta.gouv.fr',
             'Subject': "Inscription PRO à valider",
             'Html-part': email_html,
             'To': 'passculture-dev@beta.gouv.fr' if IS_DEV or IS_STAGING
                    else 'passculture@beta.gouv.fr'
           }
    mailjet_result = app.mailjet(data=email)
    if mailjet_result.status_code != 200:
        raise Exception(": "+pformat(vars(mailjet_result)))

def send_dev_email(subject, html_text):
    email = {
             'FromName': 'Pass Culture Dev',
             'FromEmail': 'passculture-dev@beta.gouv.fr',
             'Subject': subject,
             'Html-part': html_text,
             'To': 'passculture-dev@beta.gouv.fr'
           }
    mailjet_result = app.mailjet(data=email)
    if mailjet_result.status_code != 200:
        raise Exception("Email send failed: "+pformat(vars(mailjet_result)))


def make_user_booking_recap_email(offer, booking, offerer=None, is_cancellation=False):

    user = booking.user
    offer_description = _get_offer_description(offer)
    email_html = '<html><body><p>Cher {},</p>'.format(user.publicName)
    if is_cancellation:
        email_subject = 'Annulation de votre réservation pour {}'.format(offer_description)
        email_html += '<p>Votre annulation pour {} a bien été prise en compte.'.format(offer_description)
    else:
        email_subject = 'Confirmation de votre réservation pour {}'.format(offer_description)
        email_html += '<p>Nous vous confirmons votre réservation pour {}.'.format(
            offer_description
        )
    email_html += '</p><p>Cordialement,</p><p>L\'équipe pass culture</p></body></html>'

    return {
             'FromName': 'Pass Culture',
             'FromEmail': 'passculture@beta.gouv.fr',
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

    #('Pass Culture - Liste de diffusion', 1795144)
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

app.get_contact = get_contact
app.subscribe_newsletter = subscribe_newsletter
