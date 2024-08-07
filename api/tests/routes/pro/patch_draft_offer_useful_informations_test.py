from datetime import datetime

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import WithdrawalTypeEnum
import pcapi.core.users.factories as users_factories
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_patch_draft_offer_useful_informations(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            description="description",
            url="http://example.com/offer",
        )

        # When
        data = {
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/draft/{offer.id}/useful-informations", json=data
        )

        # Then
        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "Name"
        assert updated_offer.subcategoryId == subcategories.ABO_PLATEFORME_VIDEO.id
        assert updated_offer.externalTicketOfficeUrl == "http://example.net"
        assert updated_offer.audioDisabilityCompliant is True
        assert updated_offer.mentalDisabilityCompliant is False
        assert updated_offer.motorDisabilityCompliant is True
        assert updated_offer.visualDisabilityCompliant is False
        assert not updated_offer.product


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_trying_to_patch_forbidden_attributes(self, client):
        # Given
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CARTE_MUSEE.id,
            name="New name",
            url="http://example.com/offer",
            description="description",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "dateCreated": format_into_utc_date(datetime(2019, 1, 1)),
            "dateModifiedAtLastProvider": format_into_utc_date(datetime(2019, 1, 1)),
            "id": 1,
            "idAtProviders": 1,
            "lastProviderId": 1,
            "thumbCount": 2,
            "subcategoryId": subcategories.LIVRE_PAPIER,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"offers/draft/{offer.id}/useful-informations", json=data
        )

        # Then
        assert response.status_code == 400
        assert response.json["lastProviderId"] == ["Vous ne pouvez pas changer cette information"]
        forbidden_keys = {
            "dateCreated",
            "dateModifiedAtLastProvider",
            "id",
            "idAtProviders",
            "lastProviderId",
            "thumbCount",
            "subcategoryId",
        }
        for key in forbidden_keys:
            assert key in response.json

    def test_patch_non_approved_offer_fails(self, client):
        offer = offers_factories.OfferFactory(
            validation=OfferValidationStatus.PENDING,
            name="New name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            url="http://example.com/offer",
            description="description",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/draft/{offer.id}/useful-informations", json=data
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_reuse_unchanged_withdrawal(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=60 * 15,
            bookingContact="booking@conta.ct",
            name="New name",
            url="http://example.com/offer",
            description="description",
            extraData={"musicType": 520, "musicSubType": 524},
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "withdrawalType": "no_ticket",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"offers/draft/{offer.id}/useful-informations", json=data
        )

        assert response.status_code == 400
        msg = "Il ne peut pas y avoir de délai de retrait lorsqu'il s'agit d'un évènement sans ticket"
        assert response.json["offer"] == [msg]

    def test_booking_contact_is_checked_when_changed(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=WithdrawalTypeEnum.BY_EMAIL,
            withdrawalDelay=60 * 15,
            bookingContact="booking@conta.ct",
            name="New name",
            url="http://example.com/offer",
            description="description",
            extraData={"musicType": 520, "musicSubType": 524},
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"bookingContact": None}
        response = client.with_session_auth("user@example.com").patch(
            f"offers/draft/{offer.id}/useful-informations", json=data
        )

        assert response.status_code == 400
        msg = "Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"
        assert response.json["offer"] == [msg]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(
            name="Old name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            venue=venue,
            description="description",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"externalTicketOfficeUrl": "http://example.net"}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/draft/{offer.id}/useful-informations", json=data
        )

        # Then
        assert response.status_code == 403
        msg = "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        assert response.json["global"] == [msg]


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, client):
        email = "user@example.com"
        users_factories.UserFactory(email=email)
        response = client.with_session_auth(email).patch("/offers/draft/12345/useful-informations", json={})
        assert response.status_code == 404
