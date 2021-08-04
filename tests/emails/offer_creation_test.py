from bs4 import BeautifulSoup
import pytest

from pcapi import settings
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import make_offer_creation_notification_email
from pcapi.utils.mailing import make_offer_rejection_notification_email


@pytest.mark.usefixtures("db_session")
class MakeOfferCreationNotificationEmailTest:
    def test_with_physical_offer(self):
        author = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(
            author=author,
            product__name="Le vent se lève",
            venue__city="Montreuil",
            venue__postalCode="93100",
            venue__managingOfferer__name="Cinéma de Montreuil",
        )
        offerer = offer.venue.managingOfferer

        # When
        email = make_offer_creation_notification_email(offer)

        # Then
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre - 93] Le vent se lève"

        parsed_email = BeautifulSoup(email["Html-part"], "html.parser")

        offer_html = str(parsed_email.find("p", {"id": "offer"}))
        assert 'Une nouvelle offre : "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find("p", {"id": "offerer"}))
        assert "Vient d'être créée par : Cinéma de Montreuil" in offerer_html

        webapp_offer_link = str(parsed_email.find("p", {"id": "webapp_offer_link"}))
        assert (
            f"Lien vers l'offre dans la Webapp :"
            f" {settings.WEBAPP_URL}/offre/details/{humanize(offer.id)}" in webapp_offer_link
        )

        pro_offer_link = str(parsed_email.find("p", {"id": "pro_offer_link"}))
        assert (
            f"Lien vers l'offre dans le portail PRO :"
            f" http://localhost:3001/offres/{humanize(offer.id)}/edition" in pro_offer_link
        )

        offer_is_duo = str(parsed_email.find("p", {"id": "offer_is_duo"}))
        assert "Offre duo : False" in offer_is_duo

        venue_details = str(parsed_email.find("p", {"id": "venue_details"}))
        assert (
            f"Lien vers le lieu : http://localhost:3001/structures/{humanize(offerer.id)}/lieux/{humanize(offer.venue.id)}"
            in venue_details
        )
        assert "Adresse du lieu : Montreuil 93100" in venue_details

        pro_user_information = str(parsed_email.find("p", {"id": "pro_user_information"}))
        assert f"Nom : {author.lastName}" in pro_user_information
        assert f"Prénom : {author.firstName}" in pro_user_information

    def test_with_virtual_offer(self):
        # Given
        author = users_factories.ProFactory()
        offer = offers_factories.EventOfferFactory(
            author=author,
            product=offers_factories.DigitalProductFactory(name="Les lièvres pas malins"),
            venue=offers_factories.VirtualVenueFactory(),
        )

        # When
        email = make_offer_creation_notification_email(offer)

        # Then
        assert email["Subject"] == "[Création d’offre - numérique] Les lièvres pas malins"


@pytest.mark.usefixtures("db_session")
class MakeOfferRejectionNotificationEmailTest:
    def test_with_physical_offer(self):
        author = users_factories.ProFactory(firstName=None)
        offer = offers_factories.ThingOfferFactory(
            author=author,
            product__name="Le vent se lève",
            venue__city="Montreuil",
            venue__postalCode="93100",
            venue__managingOfferer__name="Cinéma de Montreuil",
        )
        offerer = offer.venue.managingOfferer

        # When
        email = make_offer_rejection_notification_email(offer)

        # Then
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre : refus - 93] Le vent se lève"

        parsed_email = BeautifulSoup(email["Html-part"], "html.parser")

        offer_html = str(parsed_email.find("p", {"id": "offer"}))
        assert 'Une nouvelle offre : "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find("p", {"id": "offerer"}))
        assert "Vient d'être créée par : Cinéma de Montreuil" in offerer_html

        pro_offer_link = str(parsed_email.find("p", {"id": "pro_offer_link"}))
        assert (
            f"Lien vers l'offre dans le portail PRO :"
            f" http://localhost:3001/offres/{humanize(offer.id)}/edition" in pro_offer_link
        )

        offer_is_duo = str(parsed_email.find("p", {"id": "offer_is_duo"}))
        assert "Offre duo : False" in offer_is_duo

        venue_details = str(parsed_email.find("p", {"id": "venue_details"}))
        assert (
            f"Lien vers le lieu : http://localhost:3001/structures/{humanize(offerer.id)}/lieux/{humanize(offer.venue.id)}"
            in venue_details
        )
        assert "Adresse du lieu : Montreuil 93100" in venue_details

        pro_user_information = str(parsed_email.find("p", {"id": "pro_user_information"}))
        assert f"Nom : {author.lastName}" in pro_user_information
        assert f"Prénom : {author.firstName}" in pro_user_information

    def test_with_virtual_offer(self):
        # Given
        author = users_factories.ProFactory()
        offer = offers_factories.EventOfferFactory(
            author=author,
            product=offers_factories.DigitalProductFactory(name="Les lièvres pas malins"),
            venue=offers_factories.VirtualVenueFactory(),
        )

        # When
        email = make_offer_rejection_notification_email(offer)

        # Then
        assert email["Subject"] == "[Création d’offre : refus - numérique] Les lièvres pas malins"
