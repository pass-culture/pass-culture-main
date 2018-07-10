from utils.test_utils import create_offer_for_booking_email_test, \
    create_user_for_booking_email_test, create_booking_for_booking_email_test

from utils.config import ENV, IS_DEV, IS_STAGING


def test_01_make_user_booking_recap_email_should_have_standard_subject(app):
    # Given
    from utils.mailing import make_user_booking_recap_email

    offer = create_offer_for_booking_email_test(app)

    user = create_user_for_booking_email_test(app)

    booking = create_booking_for_booking_email_test(app, user)

    # When
    recap_email = make_user_booking_recap_email(offer, booking, is_cancellation=False)
    # Then
    assert recap_email['Subject'] == \
           'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'




def test_02_make_user_booking_recap_email_should_have_standard_body(app):
    # Given
    from utils.mailing import make_user_booking_recap_email

    offer = create_offer_for_booking_email_test(app)

    user = create_user_for_booking_email_test(app)

    booking = create_booking_for_booking_email_test(app, user)

    # When
    recap_email = make_user_booking_recap_email(offer, booking, is_cancellation=False)
    # Then
    assert recap_email['Html-part'] == '<html><body>' + \
           '<p>Cher Test,</p>' + \
           '<p>Nous vous confirmons votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00.</p>' + \
           '<p>Cordialement,</p>' + \
           '<p>L\'équipe pass culture</p>' + \
           '</body></html>'

def test_03_make_user_booking_recap_email_should_have_standard_subject_cancellation(app):
    # Given
    from utils.mailing import make_user_booking_recap_email

    offer = create_offer_for_booking_email_test(app)

    user = create_user_for_booking_email_test(app)

    booking = create_booking_for_booking_email_test(app, user)

    # When
    recap_email = make_user_booking_recap_email(offer, booking, is_cancellation=True)
    # Then
    assert recap_email['Subject'] == \
           'Annulation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'


def test_04_make_user_booking_recap_email_should_have_standard_body_cancellation(app):
    # Given
    from utils.mailing import make_user_booking_recap_email

    offer = create_offer_for_booking_email_test(app)

    user = create_user_for_booking_email_test(app)

    booking = create_booking_for_booking_email_test(app, user)

    # When
    recap_email = make_user_booking_recap_email(offer, booking, is_cancellation=True)
    # Then
    assert recap_email['Html-part'] == '<html><body>' + \
           '<p>Cher Test,</p>' + \
           '<p>Votre annulation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00 a bien été prise en compte.</p>' + \
           '<p>Cordialement,</p>' + \
           '<p>L\'équipe pass culture</p>' + \
           '</body></html>'


def test_05_send_booking_confirmation_email_to_user_should_call_mailjet_send_create(app, mocker):
    # Given
    from utils.mailing import send_booking_confirmation_email_to_user

    offer = create_offer_for_booking_email_test(app)
    user = create_user_for_booking_email_test(app)
    booking = create_booking_for_booking_email_test(app, user)

    mocked_mailjet = mocker.patch.object(app, 'mailjet', autospec=True)
    type(mocked_mailjet.return_value).status_code = 200

    mail_html = '<html><body>' + \
           '<p>Cher Test,</p>' + \
           '<p>Nous vous confirmons votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00.</p>' + \
           '<p>Cordialement,</p>' + \
           '<p>L\'équipe pass culture</p>' + \
           '</body></html>'

    if IS_DEV or IS_STAGING:
        beginning_email = '<p>This is a test (ENV={}). In production, email would have been sent to : '.format(ENV) \
                + 'test@email.com, passculture@beta.gouv.fr</p>'
        recipients = 'passculture-dev@beta.gouv.fr'
        mail_html = beginning_email + mail_html
    else:
        recipients = 'test@email.com, passculture@beta.gouv.fr'


    expected_email = {
    "FromName": 'Pass Culture',
    'FromEmail': 'passculture@beta.gouv.fr',
    'To': recipients,
    'Subject': 'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00',
    'Html-part': mail_html
    }

    # When
    send_booking_confirmation_email_to_user(offer, booking)

    # Then
    mocked_mailjet.assert_called_once_with(data=expected_email)
