from datetime import datetime

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import StudentLevels
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking
from pcapi.routes.serialization import serialize
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @freeze_time("2019-01-01T12:00:00Z")
    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_educational_offer(self, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
            subcategoryId="CINE_PLEIN_AIR",
        )
        booking = bookings_factories.EducationalBookingFactory(
            stock__offer=offer, stock__beginningDatetime=datetime(2020, 1, 1)
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "extraData": {"contactEmail": "toto@example.com"},
            "subcategoryId": "CONCERT",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200
        product = offer.product
        venue = offer.venue
        offerer = venue.managingOfferer
        stock = offer.stocks[0]

        assert response.json == {
            "activeMediation": None,
            "ageMax": None,
            "ageMin": None,
            "audioDisabilityCompliant": False,
            "bookingEmail": None,
            "conditions": None,
            "dateCreated": format_into_utc_date(offer.dateCreated),
            "dateModifiedAtLastProvider": format_into_utc_date(offer.dateModifiedAtLastProvider),
            "dateRange": [
                format_into_utc_date(stock.beginningDatetime),
                format_into_utc_date(stock.beginningDatetime),
            ],
            "description": offer.description,
            "durationMinutes": None,
            "externalTicketOfficeUrl": None,
            "extraData": {"contactEmail": "toto@example.com", "contactPhone": "0600000000"},
            "fieldsUpdated": [],
            "hasBookingLimitDatetimesPassed": False,
            "id": humanize(offer.id),
            "isActive": True,
            "isBookable": True,
            "isDigital": False,
            "isDuo": False,
            "isEditable": True,
            "isEducational": True,
            "isEvent": True,
            "isNational": False,
            "isThing": False,
            "lastProvider": None,
            "lastProviderId": None,
            "mediaUrls": [],
            "mediations": [],
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "name": "New name",
            "nonHumanizedId": offer.id,
            "product": {
                "ageMax": None,
                "ageMin": None,
                "conditions": None,
                "dateModifiedAtLastProvider": format_into_utc_date(product.dateModifiedAtLastProvider),
                "description": product.description,
                "durationMinutes": None,
                "extraData": None,
                "fieldsUpdated": [],
                "id": humanize(product.id),
                "idAtProviders": None,
                "isGcuCompatible": True,
                "isNational": False,
                "lastProviderId": None,
                "mediaUrls": [],
                "name": product.name,
                "owningOffererId": None,
                "thumbCount": 0,
                "url": None,
            },
            "productId": humanize(product.id),
            "status": "ACTIVE",
            "stocks": [
                {
                    "beginningDatetime": "2020-01-01T00:00:00Z",
                    "bookingLimitDatetime": format_into_utc_date(stock.bookingLimitDatetime),
                    "bookingsQuantity": 1,
                    "cancellationLimitDate": "2019-01-03T12:00:00Z",
                    "dateCreated": format_into_utc_date(stock.dateCreated),
                    "dateModified": format_into_utc_date(stock.dateModified),
                    "dateModifiedAtLastProvider": format_into_utc_date(stock.dateModifiedAtLastProvider),
                    "fieldsUpdated": [],
                    "hasActivationCode": False,
                    "id": humanize(stock.id),
                    "idAtProviders": None,
                    "isBookable": True,
                    "isEventDeletable": True,
                    "isEventExpired": False,
                    "isSoftDeleted": False,
                    "lastProviderId": None,
                    "offerId": humanize(offer.id),
                    "price": stock.price,
                    "quantity": stock.quantity,
                    "remainingQuantity": stock.quantity - 1,
                }
            ],
            "subcategoryId": "CONCERT",
            "thumbUrl": None,
            "url": None,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "audioDisabilityCompliant": False,
                "bookingEmail": offer.venue.bookingEmail,
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
                    "fieldsUpdated": [],
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
            "withdrawalDetails": None,
        }
        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.extraData == {"contactEmail": "toto@example.com", "contactPhone": "0600000000"}
        assert updated_offer.subcategoryId == "CONCERT"

        expected_payload = EducationalBookingEdition(
            **serialize_educational_booking(booking.educationalBooking).dict(),
            updatedFields=sorted(["name", "contactEmail", "mentalDisabilityCompliant", "subcategoryId"]),
        )

        adage_request = adage_api_testing.adage_requests[0]
        adage_request["sent_data"].updatedFields = sorted(adage_request["sent_data"].updatedFields)

        assert adage_request["sent_data"] == expected_payload
        assert adage_request["url"] == "https://adage_base_url/v1/prereservation-edit"

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_educational_offer_do_not_notify_educational_redactor_when_no_active_booking(
        self,
        client,
    ):
        # Given
        offer = offers_factories.EducationalEventOfferFactory()
        bookings_factories.RefusedEducationalBookingFactory(stock__offer=offer)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200
        assert len(adage_api_testing.adage_requests) == 0

    @freeze_time("2019-01-01T12:00:00Z")
    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer(self, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000", "isShowcase": False},
            isEducational=True,
            subcategoryId="CINE_PLEIN_AIR",
        )
        collective_offer = CollectiveOfferFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            offerId=offer.id,
        )
        CollectiveBookingFactory(
            collectiveStock__collectiveOffer=collective_offer, collectiveStock__beginningDatetime=datetime(2020, 1, 1)
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "extraData": {"contactEmail": "toto@example.com"},
            "subcategoryId": "CONCERT",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200

        updated_offer = CollectiveOffer.query.get(collective_offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.subcategoryId == "CONCERT"

    @freeze_time("2019-01-01T12:00:00Z")
    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer_template(self, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={
                "contactEmail": "johndoe@yopmail.com",
                "contactPhone": "0600000000",
                "isShowcase": True,
                "students": ["Collège - 3e"],
            },
            isEducational=True,
            subcategoryId="CINE_PLEIN_AIR",
        )
        collective_offer_template = CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            offerId=offer.id,
            students=[StudentLevels.COLLEGE3],
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "extraData": {"contactEmail": "toto@example.com", "students": ["Collège - 4e"]},
            "subcategoryId": "CONCERT",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200

        updated_offer = CollectiveOfferTemplate.query.get(collective_offer_template.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.subcategoryId == "CONCERT"
        assert updated_offer.students == [StudentLevels.COLLEGE4]


class Returns400Test:
    def when_trying_to_patch_forbidden_attributes(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(isEducational=True)
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

    def test_patch_non_approved_offer_fails(self, app, client):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING, isEducational=True)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_patch_offer_with_empty_name(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": " "}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_null_name(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": None}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_non_educational_subcategory(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"subcategoryId": "LIVRE_PAPIER"}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_wrong_extra_data(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(
            mentalDisabilityCompliant=False,
            extraData={"contactEmail": "johndoe@yopmail.com", "contactPhone": "0600000000"},
            isEducational=True,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"extraData": {"wrongKey": 1}}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400


class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(name="Old name", isEducational=True)
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert Offer.query.get(offer.id).name == "Old name"


class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, app, client):
        # given
        users_factories.UserFactory(email="user@example.com")

        # when
        response = client.with_session_auth("user@example.com").patch("/offers/educational/ADFGA", json={})

        # then
        assert response.status_code == 404

    def test_returns_404_if_no_educational_offer_exist(self, app, client):
        # Given
        offer = offers_factories.OfferFactory(isEducational=False)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "extraData": {"contactEmail": "toto@example.com"},
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/offers/educational/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 404
        assert response.json == {
            "offerId": "no educational offer has been found with this id",
        }
