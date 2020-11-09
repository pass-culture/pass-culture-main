from unittest.mock import patch

from bs4 import BeautifulSoup

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import ThingType
from pcapi.utils.mailing import make_offer_creation_notification_email

from tests.utils.mailing_test import _remove_whitespaces


class MakeOfferCreationNotificationEmailTest:
    @classmethod
    def setup_class(cls):
        offerer = create_offerer(name='Cinéma de Montreuil')
        virtual_venue = create_venue(offerer, is_virtual=True)
        pysical_venue = create_venue(offerer)
        cls.virtual_offer = create_offer_with_thing_product(virtual_venue, thing_type=ThingType.JEUX_VIDEO, thing_name='Les lapins crétins', idx=2)
        cls.physical_offer = create_offer_with_thing_product(pysical_venue, thing_type=ThingType.AUDIOVISUEL, thing_name='Le vent se lève', idx=1)

    def test_when_physical_offer_returns_subject_with_departement_information_and_dictionary_with_given_content(self, app):
        # When
        author = create_user(email='user@example.com')
        email = make_offer_creation_notification_email(self.physical_offer, author, 'test.url')

        # Then
        assert email['FromEmail'] == 'support@example.com'
        assert email['FromName'] == 'pass Culture'
        assert email['Subject'] == '[Création d’offre - 93] Le vent se lève'

        email_html = _remove_whitespaces(email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')

        offer_html = str(parsed_email.find('p', {'id': 'offer'}))
        assert 'Une nouvelle offre "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find('p', {'id': 'offerer'}))
        assert "Vient d'être créée par Cinéma de Montreuil" in offerer_html

        link_html = str(parsed_email.find('p', {'id': 'give_link'}))
        assert 'Lien pour y accéder : ' in link_html
        assert 'Cette offre a été créée par user@example.com.' in str(parsed_email.find('p', {'id': 'author'}))
        link = str(parsed_email.find('a', {'id': 'link'}))
        assert 'test.url/offres/AE' in link
        assert 'href="test.url/offres/AE"' in link

    def test_when_virtual_offer_returns_subject_with_virtual_information_and_dictionary_with_given_content(self, app):
        # When
        author = create_user()
        email = make_offer_creation_notification_email(self.virtual_offer, author, 'test.url')

        # Then
        assert email['FromEmail'] == 'support@example.com'
        assert email['FromName'] == 'pass Culture'
        assert email['Subject'] == '[Création d’offre - numérique] Les lapins crétins'
