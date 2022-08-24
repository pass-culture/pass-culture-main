from bs4 import BeautifulSoup
import pytest

from pcapi import settings
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import VenueTypeCode
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import make_offer_creation_notification_email
from pcapi.utils.mailing import make_offer_rejection_notification_email


@pytest.mark.usefixtures("db_session")
class MakeOfferCreationNotificationEmailTest:
    @pytest.mark.parametrize(
        "isEducationalOffer",
        [True, False],
    )
    def test_with_physical_offer(self, isEducationalOffer):
        author = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(
            city="Montreuil",
            postalCode="93100",
            managingOfferer__name="Cinéma de Montreuil",
            venueTypeCode=VenueTypeCode.MOVIE,
        )
        if not isEducationalOffer:
            offer = offers_factories.ThingOfferFactory(
                author=author,
                product__name="Le vent se lève",
                venue=venue,
            )
        else:
            offer = educational_factories.CollectiveOfferFactory(name="Le vent se lève", venue=venue)
        offerer = offer.venue.managingOfferer
        offerers_factories.UserOffererFactory(user=author, offerer=offerer)

        # When
        email = make_offer_creation_notification_email(offer)

        # Then
        assert email.sender.value.name == "pass Culture"

        parsed_email = BeautifulSoup(email.html_content, "html.parser")

        offer_html = str(parsed_email.find("p", {"id": "offer"}))
        assert 'Une nouvelle offre : "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find("p", {"id": "offerer"}))
        assert "Vient d'être créée par : Cinéma de Montreuil" in offerer_html

        webapp_offer_link = str(parsed_email.find("p", {"id": "webapp_offer_link"}))
        assert f"Lien vers l'offre dans la Webapp :" f" {settings.WEBAPP_V2_URL}/offre/{offer.id}" in webapp_offer_link

        pro_offer_link = str(parsed_email.find("p", {"id": "pro_offer_link"}))
        pro_offer_type = "individuel" if isEducationalOffer is False else "collectif"
        assert (
            f"Lien vers l'offre dans le portail PRO :"
            f" http://localhost:3001/offre/{humanize(offer.id)}/{pro_offer_type}/edition" in pro_offer_link
        )
        offer_is_duo = str(parsed_email.find("p", {"id": "offer_is_duo"}))
        assert "Offre duo : False" in offer_is_duo

        offer_is_eac = str(parsed_email.find("p", {"id": "offer_is_educational"}))
        if isEducationalOffer is True:
            assert "Offre EAC : True" in offer_is_eac
            assert email.subject == "[Création d’offre EAC - 93] Le vent se lève"
        else:
            assert email.subject == "[Création d’offre - 93] Le vent se lève"
            assert "Offre EAC : False" in offer_is_eac

        venue_details = str(parsed_email.find("p", {"id": "venue_details"}))
        assert "Catégorie du lieu : Cinéma - Salle de projections" in venue_details
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
            venue=offerers_factories.VirtualVenueFactory(),
        )

        # When
        email = make_offer_creation_notification_email(offer)

        # Then
        assert email.subject == "[Création d’offre - numérique] Les lièvres pas malins"


@pytest.mark.usefixtures("db_session")
class MakeOfferRejectionNotificationEmailTest:
    @pytest.mark.parametrize(
        "isEducationalOffer",
        [True, False],
    )
    def test_with_physical_offer(self, isEducationalOffer):
        author = users_factories.ProFactory(firstName=None)
        venue = offerers_factories.VenueFactory(
            city="Montreuil",
            postalCode="93100",
            managingOfferer__name="Cinéma de Montreuil",
            venueTypeCode=VenueTypeCode.MOVIE,
        )
        if not isEducationalOffer:
            offer = offers_factories.ThingOfferFactory(
                author=author,
                product__name="Le vent se lève",
                venue=venue,
            )
        else:
            offer = educational_factories.CollectiveOfferFactory(name="Le vent se lève", venue=venue)
        offerer = offer.venue.managingOfferer
        offerers_factories.UserOffererFactory(user=author, offerer=offerer)

        # When
        email = make_offer_rejection_notification_email(offer)

        # Then
        assert email.sender.value.name == "pass Culture"

        parsed_email = BeautifulSoup(email.html_content, "html.parser")

        offer_html = str(parsed_email.find("p", {"id": "offer"}))
        assert 'Une nouvelle offre : "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find("p", {"id": "offerer"}))
        assert "Vient d'être créée par : Cinéma de Montreuil" in offerer_html

        pro_offer_link = str(parsed_email.find("p", {"id": "pro_offer_link"}))
        pro_offer_type = "individuel" if not isEducationalOffer else "collectif"
        assert (
            f"Lien vers l'offre dans le portail PRO :"
            f" http://localhost:3001/offre/{humanize(offer.id)}/{pro_offer_type}/edition" in pro_offer_link
        )

        offer_is_duo = str(parsed_email.find("p", {"id": "offer_is_duo"}))
        assert "Offre duo : False" in offer_is_duo

        offer_is_eac = str(parsed_email.find("p", {"id": "offer_is_educational"}))
        if isEducationalOffer:
            assert "Offre EAC : True" in offer_is_eac
            assert email.subject == "[Création d’offre EAC : refus - 93] Le vent se lève"
        else:
            assert email.subject == "[Création d’offre : refus - 93] Le vent se lève"
            assert "Offre EAC : False" in offer_is_eac

        venue_details = str(parsed_email.find("p", {"id": "venue_details"}))
        assert "Catégorie du lieu : Cinéma - Salle de projections" in venue_details
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
            venue=offerers_factories.VirtualVenueFactory(),
        )

        # When
        email = make_offer_rejection_notification_email(offer)

        # Then
        assert email.subject == "[Création d’offre : refus - numérique] Les lièvres pas malins"
