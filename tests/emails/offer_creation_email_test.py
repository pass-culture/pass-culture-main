from bs4 import BeautifulSoup

from models import ThingType
from tests.test_utils import create_offerer, create_venue, create_offer_with_thing_product, create_user
from tests.utils.mailing_test import _remove_whitespaces
from utils.mailing import make_offer_creation_notification_email


class MakeOfferCreationNotificationEmailTest:
    @classmethod
    def setup_class(self):
        self.offerer = create_offerer(siren='123456789', postal_code='93100', name='Cinéma de Montreuil')

        siret = self.offerer.siren + '12345'

        self.virtual_venue = create_venue(self.offerer, siret=None, is_virtual=True, postal_code=None,
                                          departement_code=None, address=None)
        self.venue93 = create_venue(self.offerer, siret=siret, is_virtual=False, departement_code='93',
                                    postal_code='93100')

        self.physical_offer93 = create_offer_with_thing_product(self.venue93, thing_type=ThingType.AUDIOVISUEL,
                                                                thing_name='Le vent se lève', idx=1)
        self.virtual_offer = create_offer_with_thing_product(self.virtual_venue, thing_type=ThingType.JEUX_VIDEO,
                                                             thing_name='Les lapins crétins', idx=2)

    def test_when_physical_offer_returns_subject_with_departement_information_and_dictionary_with_given_content(self,
                                                                                                                app):
        # When
        author = create_user(email='user@email.com')
        email = make_offer_creation_notification_email(self.physical_offer93, author, 'test.url')
        # Then
        assert email["FromEmail"] == 'support@passculture.app'
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre - 93] Le vent se lève"

        email_html = _remove_whitespaces(email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')

        offer_html = str(parsed_email.find('p', {'id': 'offer'}))
        assert 'Une nouvelle offre "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find('p', {'id': 'offerer'}))
        assert "Vient d'être créée par Cinéma de Montreuil" in offerer_html

        link_html = str(parsed_email.find('p', {'id': 'give_link'}))
        assert "Lien pour y accéder : " in link_html
        assert "Cette offre a été créée par user@email.com." in str(parsed_email.find('p', {'id': 'author'}))
        link = str(parsed_email.find('a', {'id': 'link'}))
        assert "test.url/offres/AE" in link
        assert 'href="test.url/offres/AE"' in link

    def test_when_virtual_offer_returns_subject_with_virtual_information_and_dictionary_with_given_content(self, app):
        # When
        author = create_user('author@email.com')
        email = make_offer_creation_notification_email(self.virtual_offer, author, 'test.url')
        # Then
        assert email["FromEmail"] == 'support@passculture.app'
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre - numérique] Les lapins crétins"
