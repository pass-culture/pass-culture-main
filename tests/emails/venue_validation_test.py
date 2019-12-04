from bs4 import BeautifulSoup

from tests.test_utils import create_offerer, create_venue
from tests.utils.mailing_test import _remove_whitespaces
from utils.mailing import make_venue_to_validate_email, make_venue_validated_email


def test_make_venue_to_validate_email(app):
    # Given
    offerer = create_offerer(name='La Structure', siren='123456789')
    venue = create_venue(offerer, name='Le Lieu', comment='Ceci est mon commentaire')
    venue.generate_validation_token()

    # When
    email = make_venue_to_validate_email(venue)

    # Then
    assert email["FromEmail"] == 'support@passculture.app'
    assert email["FromName"] == "pass Culture"
    assert email["Subject"] == "{} - rattachement de lieu pro à valider : {}".format(venue.departementCode, venue.name)
    email_html = _remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_validation = parsed_email.find('p', {'id': 'validation'}).text
    html_validation_link = parsed_email.find('a', {'id': 'validation-link'}).text
    assert 'La structure "La Structure" (SIREN : 123456789)' in html_validation
    assert 'a rattaché le lieu suivant sans renseigner de SIRET' in html_validation
    assert 'Nom : "Le Lieu"' in html_validation
    assert 'Commentaire de la structure : "Ceci est mon commentaire".' in html_validation
    assert 'localhost/validate/venue?token={}'.format(venue.validationToken) in html_validation
    assert 'localhost/validate/venue?token={}'.format(venue.validationToken) in html_validation_link


def test_make_venue_validated_email(app):
    # Given
    offerer = create_offerer(name='La Structure', siren='123456789')
    venue = create_venue(offerer, name='Le Lieu', comment='Ceci est mon commentaire')

    # When
    email = make_venue_validated_email(venue)

    # Then
    assert email['Subject'] == 'Validation du rattachement du lieu "Le Lieu" à votre structure "La Structure"'
    assert email["FromEmail"] == 'support@passculture.app'
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
