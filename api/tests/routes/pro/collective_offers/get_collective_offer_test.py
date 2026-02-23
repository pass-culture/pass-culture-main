from datetime import timedelta

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.testing import assert_num_queries
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # session + user
    # offerer
    # user_offerer
    # collective_offer
    # google_places_info
    num_queries = 5

    def test_basics(self, client):
        template = educational_factories.CollectiveOfferTemplateFactory()
        stock = educational_factories.CollectiveStockFactory()
        teacher = educational_factories.EducationalRedactorFactory()
        national_program = educational_factories.NationalProgramFactory()
        provider = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory(bannerUrl="http://localhost/image.png")
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock,
            teacher=teacher,
            template=template,
            nationalProgram=national_program,
            provider=provider,
            venue=venue,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        expected_num_queries = self.num_queries
        expected_num_queries -= 1  # google_places_info
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json == {
            "allowedActions": ["CAN_DUPLICATE", "CAN_ARCHIVE"],
            "audioDisabilityCompliant": False,
            "booking": None,
            "bookingEmails": offer.bookingEmails,
            "collectiveStock": {
                "bookingLimitDatetime": format_into_utc_date(stock.bookingLimitDatetime),
                "educationalPriceDetail": stock.priceDetail,
                "endDatetime": format_into_utc_date(stock.endDatetime),
                "id": stock.id,
                "numberOfTickets": stock.numberOfTickets,
                "price": float(stock.price),
                "startDatetime": format_into_utc_date(stock.startDatetime),
            },
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
            "dateCreated": format_into_utc_date(offer.dateCreated),
            "dates": {
                "end": format_into_utc_date(stock.startDatetime),
                "start": format_into_utc_date(stock.endDatetime),
            },
            "description": offer.description,
            "displayedStatus": educational_models.CollectiveOfferDisplayedStatus.PUBLISHED.value,
            "domains": [],
            "durationMinutes": None,
            "formats": [f.value for f in offer.formats],
            "history": {
                "future": [
                    "PREBOOKED",
                    "BOOKED",
                    "ENDED",
                    "REIMBURSED",
                ],
                "past": [{"datetime": format_into_utc_date(offer.lastValidationDate), "status": "PUBLISHED"}],
            },
            "id": offer.id,
            "imageCredit": None,
            "imageUrl": None,
            "institution": None,
            "interventionArea": offer.interventionArea,
            "isPublicApi": True,
            "isTemplate": False,
            "location": {
                "location": None,
                "locationComment": None,
                "locationType": "TO_BE_DEFINED",
            },
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "name": offer.name,
            "nationalProgram": {
                "id": national_program.id,
                "name": national_program.name,
            },
            "provider": {
                "name": provider.name,
            },
            "students": ["Lycée - Seconde"],
            "teacher": {
                "civility": teacher.civility,
                "email": teacher.email,
                "firstName": teacher.firstName,
                "lastName": teacher.lastName,
            },
            "templateId": template.id,
            "venue": {
                "departementCode": "75",
                "id": venue.id,
                "imgUrl": "http://localhost/image.png",
                "managingOfferer": {
                    "id": venue.managingOfferer.id,
                    "name": venue.managingOfferer.name,
                    "siren": venue.managingOfferer.siren,
                },
                "name": venue.name,
                "publicName": venue.publicName,
            },
            "visualDisabilityCompliant": False,
        }

    def test_location_address_venue(self, client):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddress.id,
            interventionArea=None,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"]["isVenueLocation"] is True
        assert response_location["location"]["banId"] == venue.offererAddress.address.banId
        assert response_json["interventionArea"] == []

    def test_location_school(self, client):
        offer = educational_factories.CollectiveOfferFactory(
            locationType=educational_models.CollectiveLocationType.SCHOOL,
            locationComment=None,
            offererAddressId=None,
            interventionArea=["33", "75", "93"],
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "SCHOOL"
        assert response_location["locationComment"] is None
        assert response_location["location"] is None
        assert response_json["interventionArea"] == ["33", "75", "93"]

    def test_location_address(self, client):
        venue = offerers_factories.VenueFactory()
        oa = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)
        offer = educational_factories.CollectiveOfferFactory(
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddress=oa,
            interventionArea=None,
            venue=venue,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is False
        assert response_location["location"]["banId"] == oa.address.banId
        assert response_json["interventionArea"] == []

    def test_location_to_be_defined(self, client):
        offer = educational_factories.CollectiveOfferFactory(
            locationType=educational_models.CollectiveLocationType.TO_BE_DEFINED,
            locationComment="In space",
            offererAddressId=None,
            interventionArea=["33", "75", "93"],
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        client = client.with_session_auth(email="user@example.com")

        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        response_location = response_json["location"]
        assert response_location["locationType"] == "TO_BE_DEFINED"
        assert response_location["locationComment"] == "In space"
        assert response_location["location"] is None
        assert response_json["interventionArea"] == ["33", "75", "93"]

    def test_performance(self, client):
        stock = educational_factories.CollectiveStockFactory()
        educational_factories.CancelledCollectiveBookingFactory.create_batch(5, collectiveStock=stock)
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries):
            with testing.assert_no_duplicated_queries():
                client.get(f"/collective/offers/{offer_id}")

    def test_booking_field(self, client):
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=educational_models.CollectiveBookingStatus.CANCELLED
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=educational_models.CollectiveBookingStatus.REIMBURSED
        )

        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["booking"] == {
            "id": booking.id,
            "status": educational_models.CollectiveBookingStatus.REIMBURSED.value,
            "dateCreated": format_into_utc_date(booking.dateCreated),
            "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
            "cancellationReason": None,
            "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
            "educationalRedactor": {
                "civility": booking.educationalRedactor.civility,
                "email": booking.educationalRedactor.email,
                "firstName": booking.educationalRedactor.firstName,
                "lastName": booking.educationalRedactor.lastName,
            },
        }

    def test_booking_field_cancelled(self, client):
        offer = educational_factories.CancelledWithBookingCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        [booking] = offer.collectiveStock.collectiveBookings

        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["booking"] == {
            "id": booking.id,
            "status": educational_models.CollectiveBookingStatus.CANCELLED.value,
            "dateCreated": format_into_utc_date(booking.dateCreated),
            "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
            "cancellationReason": educational_models.CollectiveBookingCancellationReasons.OFFERER.value,
            "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
            "educationalRedactor": {
                "civility": booking.educationalRedactor.civility,
                "email": booking.educationalRedactor.email,
                "firstName": booking.educationalRedactor.firstName,
                "lastName": booking.educationalRedactor.lastName,
            },
        }

    def test_dates_on_offer(self, client):
        beginningDate = date_utils.get_naive_utc_now() + timedelta(days=100)
        endDate = date_utils.get_naive_utc_now() + timedelta(days=125)
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=beginningDate,
            endDatetime=endDate,
        )
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock,
            isActive=True,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["dates"] == {
            "start": beginningDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "end": endDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email=pro_user.email)
        offer_id = offer.id
        expected_num_queries = 5
        # session + user
        # offerer
        # user_offerer
        # rollback
        # rollback
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 403
