from datetime import date
from datetime import datetime
from datetime import timedelta

import pytest
from flask import url_for

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.testing import assert_num_queries


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # session
    # user
    # offerer
    # user_offerer
    # collective_offer
    # google_places_info
    num_queries = 6

    def test_filtering(self, client):
        offer = educational_factories.PendingCollectiveBookingFactory().collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")

        dst = url_for("Private API.get_collective_offers", status=CollectiveOfferDisplayedStatus.PREBOOKED.value)

        with assert_num_queries(4):  #  session + user + collective_offer + collective_offer_template
            response = client.get(dst)
            assert response.status_code == 200

        assert len(response.json) == 1
        assert response.json[0]["id"] == offer.id

    def test_basics(self, client):
        template = educational_factories.CollectiveOfferTemplateFactory()
        stock = educational_factories.CollectiveStockFactory()
        national_program = educational_factories.NationalProgramFactory()
        provider = providers_factories.ProviderFactory()
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock,
            teacher=educational_factories.EducationalRedactorFactory(),
            templateId=template.id,
            nationalProgramId=national_program.id,
            providerId=provider.id,
            venue___bannerUrl="http://localhost/image.png",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        expected_num_queries = self.num_queries
        expected_num_queries -= 1  # google_places_info
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert response_json["venue"]["imgUrl"] == "http://localhost/image.png"
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
        assert response_json["venue"]["departementCode"] == offer.venue.offererAddress.address.departmentCode
        assert response_json["venue"]["managingOfferer"] == {
            "id": offer.venue.managingOffererId,
            "name": offer.venue.managingOfferer.name,
            "siren": offer.venue.managingOfferer.siren,
            "allowedOnAdage": offer.venue.managingOfferer.allowedOnAdage,
        }
        assert response_json["imageCredit"] is None
        assert response_json["imageUrl"] is None
        assert "dateCreated" in response_json
        assert "institution" in response.json
        assert response.json["isVisibilityEditable"] is True
        assert response_json["id"] == offer.id
        assert response_json["lastBookingStatus"] is None
        assert response_json["lastBookingId"] is None
        assert response_json["teacher"] == {
            "email": offer.teacher.email,
            "firstName": offer.teacher.firstName,
            "lastName": offer.teacher.lastName,
            "civility": offer.teacher.civility,
        }
        assert response_json["templateId"] == template.id
        assert response_json["nationalProgram"] == {"id": national_program.id, "name": national_program.name}
        assert response_json["formats"] == [fmt.value for fmt in offer.formats]
        assert response_json["provider"]["name"] == provider.name
        assert response_json["displayedStatus"] == "PUBLISHED"
        assert response_json["isTemplate"] is False
        assert response_json["isActive"] is True

        assert response_json["location"] is None

    def test_location_address_venue(self, client):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddressId,
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
        assert response_location["address"]["id_oa"] == venue.offererAddressId
        assert response_location["address"]["isLinkedToVenue"] is True
        assert response_location["address"]["banId"] == venue.offererAddress.address.banId
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
        assert response_location["address"] is None
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
        assert response_location["address"] is not None
        assert response_location["address"]["id_oa"] == oa.id
        assert response_location["address"]["isLinkedToVenue"] is False
        assert response_location["address"]["banId"] == oa.address.banId
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
        assert response_location["address"] is None
        assert response_json["interventionArea"] == ["33", "75", "93"]

    def test_sold_out(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        educational_factories.UsedCollectiveBookingFactory(collectiveStock=stock)
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert response_json["collectiveStock"]["isBooked"] is True
        assert response_json["isCancellable"] is False
        assert response_json["isVisibilityEditable"] is False

    def test_cancellable(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert response_json["collectiveStock"]["isBooked"] is True
        assert response_json["isCancellable"] is True
        assert response_json["isVisibilityEditable"] is False

    def test_cancellable_with_not_cancellable_booking(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)
        educational_factories.UsedCollectiveBookingFactory(collectiveStock=stock)
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert response_json["collectiveStock"]["isBooked"] is True
        assert response_json["isCancellable"] is True
        assert response_json["isVisibilityEditable"] is False

    def test_performance(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        educational_factories.CancelledCollectiveBookingFactory.create_batch(5, collectiveStock=stock)
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries):
            with testing.assert_no_duplicated_queries():
                client.get(f"/collective/offers/{offer_id}")

    def test_last_booking_fields(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=educational_models.CollectiveBookingStatus.CANCELLED
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock, status=educational_models.CollectiveBookingStatus.REIMBURSED
        )

        # When
        client = client.with_session_auth(email="user@example.com")
        offer_id = offer.id
        with assert_num_queries(self.num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert response_json["lastBookingId"] == booking.id
        assert response_json["lastBookingStatus"] == booking.status.value

    def test_dates_on_offer(self, client):
        beginningDate = datetime.utcnow() + timedelta(days=100)
        endDate = datetime.utcnow() + timedelta(days=125)
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
        # session
        # user
        # offerer
        # user_offerer
        # rollback
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/{offer_id}")
            assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class GetCollectiveOfferRequestTest:
    def test_get_offer_request(self, client):
        pro_user = users_factories.ProFactory()

        redactor = educational_factories.EducationalRedactorFactory()
        request = educational_factories.CollectiveOfferRequestFactory(
            educationalRedactor=redactor,
            requestedDate=date.today() + timedelta(days=7),
            totalStudents=40,
            totalTeachers=2,
            comment="Some offer request with all information filled",
            phoneNumber="0102030405",
            dateCreated=date.today(),
        )

        offerers_factories.UserOffererFactory(
            user=pro_user, offerer=request.collectiveOfferTemplate.venue.managingOfferer
        )

        dst = url_for(
            "Private API.get_collective_offer_request",
            offer_id=request.collectiveOfferTemplateId,
            request_id=request.id,
        )
        client = client.with_session_auth(email=pro_user.email)

        # fetch session (1 query)
        # fetch user (1 query)
        # fetch collective offer request and related data (1 query)
        # check whether user has access to offerer (1 query)
        with testing.assert_num_queries(4):
            response = client.get(dst)

        assert response.status_code == 200
        assert response.json == {
            "redactor": {
                "firstName": redactor.firstName,
                "lastName": redactor.lastName,
                "email": redactor.email,
            },
            "requestedDate": request.requestedDate.isoformat(),
            "totalStudents": request.totalStudents,
            "totalTeachers": request.totalTeachers,
            "comment": request.comment,
            "phoneNumber": request.phoneNumber,
            "dateCreated": request.dateCreated.isoformat(),
            "institution": {
                "institutionId": request.educationalInstitution.institutionId,
                "institutionType": request.educationalInstitution.institutionType,
                "name": request.educationalInstitution.name,
                "city": request.educationalInstitution.city,
                "postalCode": request.educationalInstitution.postalCode,
            },
        }

    def test_user_does_not_have_access_to_the_offer(self, client):
        pro_user = users_factories.ProFactory()
        another_pro_user = users_factories.ProFactory()

        redactor = educational_factories.EducationalRedactorFactory()
        request = educational_factories.CollectiveOfferRequestFactory(educationalRedactor=redactor)
        offerers_factories.UserOffererFactory(
            user=another_pro_user, offerer=request.collectiveOfferTemplate.venue.managingOfferer
        )

        dst = url_for(
            "Private API.get_collective_offer_request",
            offer_id=request.collectiveOfferTemplateId,
            request_id=request.id,
        )

        client = client.with_session_auth(email=pro_user.email)
        expected_num_queries = 5
        # session
        # user
        # collective_offer_request
        # user_offerer
        # rollback
        with assert_num_queries(expected_num_queries):
            response = client.get(dst)
            assert response.status_code == 403

    def test_offer_request_does_not_exist(self, client):
        pro_user = users_factories.ProFactory()
        request = educational_factories.CollectiveOfferRequestFactory()
        offerers_factories.UserOffererFactory(
            user=pro_user, offerer=request.collectiveOfferTemplate.venue.managingOfferer
        )

        dst = url_for(
            "Private API.get_collective_offer_request",
            offer_id=request.collectiveOfferTemplateId,
            request_id=request.id + 1,
        )

        client = client.with_session_auth(email=pro_user.email)
        with assert_num_queries(4):  #  session + user + collective_offer_request + rollback
            response = client.get(dst)
            assert response.status_code == 404
