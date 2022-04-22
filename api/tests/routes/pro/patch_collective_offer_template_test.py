from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories
from pcapi.routes.serialization import serialize
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @freeze_time("2019-01-01T12:00:00Z")
    def test_patch_collective_offer_template(self, client):
        # Given
        collective_offer = educational_factories.CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=collective_offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "extraData": {"contactEmail": "toto@example.com"},
            "subcategoryId": "CONCERT",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(collective_offer.id)}", json=data
        )

        # Then
        # assert response.status_code == 200
        venue = collective_offer.venue
        offerer = venue.managingOfferer

        assert response.json == {
            "audioDisabilityCompliant": False,
            "bookingEmail": None,
            "contactEmail": "toto@example.com",
            "contactPhone": "0600000000",
            "dateCreated": format_into_utc_date(collective_offer.dateCreated),
            "description": collective_offer.description,
            "durationMinutes": None,
            "educationalPriceDetail": None,
            "extraData": {
                "contactEmail": "toto@example.com",
                "contactPhone": "0600000000",
                "isShowcase": True,
                "offerVenue": {
                    "addressType": "other",
                    "otherAddress": "1 rue des polissons, Paris 75017",
                    "venueId": "",
                },
                "students": ["Lycée - Seconde"],
            },
            "hasBookingLimitDatetimesPassed": False,
            "id": humanize(collective_offer.id),
            "isActive": True,
            "isBooked": False,
            "isEducational": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "name": "New name",
            "offerId": None,
            "offerVenue": {
                "addressType": "other",
                "otherAddress": "1 rue des polissons, Paris 75017",
                "venueId": "",
            },
            "students": ["Lycée - Seconde"],
            "nonHumanizedId": collective_offer.id,
            "status": "ACTIVE",
            "stocks": [],
            "subcategoryId": "CONCERT",
            "venue": {
                "address": "1 boulevard Poissonnière",
                "audioDisabilityCompliant": False,
                "bookingEmail": collective_offer.venue.bookingEmail,
                "city": "Paris",
                "comment": None,
                "dateCreated": format_into_utc_date(venue.dateCreated),
                "dateModifiedAtLastProvider": format_into_utc_date(venue.dateModifiedAtLastProvider),
                "departementCode": "75",
                "fieldsUpdated": [],
                "id": humanize(venue.id),
                "idAtProviders": None,
                "isValidated": True,
                "isVirtual": False,
                "lastProviderId": None,
                "latitude": 48.87004,
                "longitude": 2.3785,
                "managingOfferer": {
                    "address": "1 boulevard Poissonnière",
                    "city": "Paris",
                    "dateCreated": format_into_utc_date(offerer.dateCreated),
                    "dateModifiedAtLastProvider": format_into_utc_date(offerer.dateModifiedAtLastProvider),
                    "id": humanize(offerer.id),
                    "idAtProviders": None,
                    "isActive": True,
                    "isValidated": True,
                    "lastProviderId": None,
                    "name": offerer.name,
                    "postalCode": "75000",
                    "siren": offerer.siren,
                    "thumbCount": 0,
                },
                "managingOffererId": humanize(offerer.id),
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "name": venue.name,
                "postalCode": "75000",
                "publicName": venue.publicName,
                "siret": venue.siret,
                "thumbCount": 0,
                "venueLabelId": None,
                "visualDisabilityCompliant": False,
            },
            "venueId": humanize(venue.id),
            "visualDisabilityCompliant": False,
        }
        updated_offer: CollectiveOfferTemplate = CollectiveOfferTemplate.query.get(collective_offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.subcategoryId == "CONCERT"


class Returns400Test:
    def when_trying_to_patch_forbidden_attributes(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "dateCreated": serialize(datetime(2019, 1, 1)),
            "id": 1,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400
        assert response.json["dateCreated"] == ["Vous ne pouvez pas changer cette information"]
        forbidden_keys = {
            "dateCreated",
            "id",
        }
        for key in forbidden_keys:
            assert key in response.json

    def test_patch_non_approved_offer_fails(self, client):
        offer = educational_factories.CollectiveOfferTemplateFactory(validation=OfferValidationStatus.PENDING)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}", json=data
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_patch_collective_offer_template_with_empty_name(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": " "}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_collective_offer_template_with_null_name(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": None}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_collective_offer_template_with_non_educational_subcategory(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"subcategoryId": "LIVRE_PAPIER"}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_collective_offer_template_with_wrong_extra_data(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"extraData": {"wrongKey": 1}}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400


class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, client):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory(name="Old name")
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert CollectiveOfferTemplate.query.get(offer.id).name == "Old name"
