from unittest.mock import patch

from bs4 import BeautifulSoup
import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.generic_creators import create_venue_type
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import ThingType
from pcapi.models import VenueType
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import make_offer_creation_notification_email

from tests.utils.mailing_test import _remove_whitespaces


class MakeOfferCreationNotificationEmailTest:
    @pytest.mark.usefixtures("db_session")
    def test_when_physical_offer_returns_subject_with_departement_information_and_dictionary_with_given_content(
        self, app
    ):
        # Given
        venue_type = create_venue_type(label="Custom Label")
        repository.save(venue_type)

        author = create_user(email="user@example.com", first_name="John", last_name="Doe", phone_number="0102030405")
        offerer = create_offerer(name="Cinéma de Montreuil")
        physical_venue = create_venue(offerer, venue_type_id=venue_type.id)
        physical_offer = create_offer_with_thing_product(
            venue=physical_venue, thing_type=ThingType.AUDIOVISUEL, thing_name="Le vent se lève", idx=1
        )
        repository.save(author, physical_offer)

        # When

        email = make_offer_creation_notification_email(physical_offer, author)

        # Then
        assert email["FromEmail"] == "support@example.com"
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre - 93] Le vent se lève"

        email_html = _remove_whitespaces(email["Html-part"])
        parsed_email = BeautifulSoup(email_html, "html.parser")

        offer_html = str(parsed_email.find("p", {"id": "offer"}))
        assert 'Une nouvelle offre : "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find("p", {"id": "offerer"}))
        assert "Vient d'être créée par : Cinéma de Montreuil" in offerer_html

        webapp_offer_link = str(parsed_email.find("p", {"id": "webapp_offer_link"}))
        assert (
            f"Lien vers l'offre dans la Webapp :"
            f" http://localhost:3000/offre/details/{humanize(physical_offer.id)}" in webapp_offer_link
        )

        pro_offer_link = str(parsed_email.find("p", {"id": "pro_offer_link"}))
        assert (
            f"Lien vers l'offre dans le portail PRO :"
            f" http://localhost:3001/offres/{humanize(physical_offer.id)}" in pro_offer_link
        )

        offer_is_duo = str(parsed_email.find("p", {"id": "offer_is_duo"}))
        assert "Offre duo : False" in offer_is_duo

        venue_details = str(parsed_email.find("p", {"id": "venue_details"}))
        assert f"Lien vers le lieu : http://localhost:3001/lieux/{humanize(physical_offer.venue.id)}" in venue_details
        assert "Catégorie du lieu : Custom Label" in venue_details
        assert "Adresse du lieu : Montreuil 93100" in venue_details

        pro_user_information = str(parsed_email.find("p", {"id": "pro_user_information"}))
        assert "Nom : Doe" in pro_user_information
        assert "Prénom : John" in pro_user_information
        assert "Téléphone : 0102030405" in pro_user_information
        assert "Email : user@example.com" in pro_user_information

    @pytest.mark.usefixtures("db_session")
    def test_when_virtual_offer_returns_subject_with_virtual_information_and_dictionary_with_given_content(self, app):
        # Given
        author = create_user()
        offerer = create_offerer(name="Cinéma de Montreuil")
        virtual_venue = create_venue(offerer, siret=None, is_virtual=True)
        virtual_offer = create_offer_with_thing_product(
            venue=virtual_venue,
            thing_type=ThingType.JEUX_VIDEO,
            is_digital=True,
            thing_name="Les lapins crétins",
            idx=2,
        )
        repository.save(author, virtual_offer)

        # When
        email = make_offer_creation_notification_email(virtual_offer, author)

        # Then
        assert email["FromEmail"] == "support@example.com"
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre - numérique] Les lapins crétins"
