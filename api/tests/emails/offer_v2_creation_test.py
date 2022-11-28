from bs4 import BeautifulSoup
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import VenueTypeCode
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
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
    @override_features(OFFER_FORM_V3=False)
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
        parsed_email = BeautifulSoup(email.html_content, "html.parser")
        pro_offer_link = str(parsed_email.find("p", {"id": "pro_offer_link"}))
        pro_offer_type = "individuel" if isEducationalOffer is False else "collectif"
        assert (
            f"Lien vers l'offre dans le portail PRO :"
            f" http://localhost:3001/offre/{humanize(offer.id)}/{pro_offer_type}/edition" in pro_offer_link
        )


@pytest.mark.usefixtures("db_session")
class MakeOfferRejectionNotificationEmailTest:
    @pytest.mark.parametrize(
        "isEducationalOffer",
        [True, False],
    )
    @override_features(OFFER_FORM_V3=False)
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
        parsed_email = BeautifulSoup(email.html_content, "html.parser")
        pro_offer_link = str(parsed_email.find("p", {"id": "pro_offer_link"}))
        pro_offer_type = "individuel" if not isEducationalOffer else "collectif"
        assert (
            f"Lien vers l'offre dans le portail PRO :"
            f" http://localhost:3001/offre/{humanize(offer.id)}/{pro_offer_type}/edition" in pro_offer_link
        )
