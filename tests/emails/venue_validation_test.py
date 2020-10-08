from unittest.mock import patch

from bs4 import BeautifulSoup

from pcapi.model_creators.generic_creators import create_offerer, create_venue
from tests.utils.mailing_test import _remove_whitespaces
from pcapi.utils.mailing import make_venue_validated_email


@patch('pcapi.utils.mailing.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
def test_make_venue_validated_email(app):
    # Given
    offerer = create_offerer(name='La Structure', siren='123456789')
    venue = create_venue(offerer, name='Le Lieu', comment='Ceci est mon commentaire')

    # When
    email = make_venue_validated_email(venue)

    # Then
    assert email['Subject'] == 'Validation du rattachement du lieu "Le Lieu" à votre structure "La Structure"'
    assert email["FromEmail"] == 'support@example.com'
    assert email["FromName"] == "pass Culture pro"
    email_html = _remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_validation = str(parsed_email.find('p', {'id': 'validation-details'}))
    html_greeting = str(parsed_email.find('p', {'id': 'mail-greeting'}))
    html_salutation = str(parsed_email.find('p', {'id': 'mail-salutation'}))
    assert 'Cher partenaire pass Culture,' in html_greeting
    assert 'Le rattachement du lieu "Le Lieu"' in html_validation
    assert 'à votre structure "La Structure"' in html_validation
    assert 'Cordialement,' in html_salutation
    assert 'L\'équipe pass Culture' in html_salutation
