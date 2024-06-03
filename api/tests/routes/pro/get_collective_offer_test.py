from datetime import date
from datetime import datetime
from datetime import timedelta

from flask import url_for
import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_filtering(self, client):
        offer = educational_factories.PendingCollectiveBookingFactory().collectiveStock.collectiveOffer
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")

        dst = url_for("Private API.get_collective_offers", status=CollectiveOfferDisplayedStatus.PREBOOKED.value)
        response = client.get(dst)

        assert response.status_code == 200

        assert len(response.json) == 1
        assert response.json[0]["id"] == offer.id

    def test_basics(self, client):
        # Given
        template = educational_factories.CollectiveOfferTemplateFactory()
        stock = educational_factories.CollectiveStockFactory()
        national_program = educational_factories.NationalProgramFactory()
        provider = providers_factories.ProviderFactory()
        offer = educational_factories.CollectiveOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            collectiveStock=stock,
            teacher=educational_factories.EducationalRedactorFactory(),
            templateId=template.id,
            nationalProgramId=national_program.id,
            providerId=provider.id,
            venue___bannerUrl="http://localhost/image.png",
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        response = client.get(f"/collective/offers/{offer.id}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert response_json["venue"]["imgUrl"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
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
        assert response_json["formats"] == [fmt.value for fmt in subcategories.SEANCE_CINE.formats]
        assert response_json["provider"]["name"] == provider.name
        assert not response_json["isTemplate"]

    def test_sold_out(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        educational_factories.UsedCollectiveBookingFactory(collectiveStock=stock)
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        response = client.get(f"/collective/offers/{offer.id}")

        # Then
        response_json = response.json
        assert response.status_code == 200
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
        response = client.get(f"/collective/offers/{offer.id}")

        # Then
        response_json = response.json
        assert response.status_code == 200
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
        response = client.get(f"/collective/offers/{offer.id}")

        # Then
        response_json = response.json
        assert response.status_code == 200
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

        with testing.assert_no_duplicated_queries():
            client.get(f"/collective/offers/{offer.id}")

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
        response = client.get(f"/collective/offers/{offer.id}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json["lastBookingId"] == booking.id
        assert response_json["lastBookingStatus"] == booking.status.value

    def test_inactive_offer(self, client):
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=datetime.utcnow() + timedelta(days=125),
            endDatetime=datetime.utcnow() + timedelta(days=125),
            bookingLimitDatetime=datetime.utcnow() - timedelta(days=125),
        )
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock,
            teacher=educational_factories.EducationalRedactorFactory(),
            isActive=True,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        response = client.get(f"/collective/offers/{offer.id}")

        # Then
        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert response.json["isActive"] is False

    def test_offer_venue_has_an_empty_string_venue_id(self, client):
        # TODO(jeremieb): remove this test once there is no empty
        # string stored as a venueId
        offer = educational_factories.CollectiveOfferFactory(
            offerVenue={"venueId": "", "addressType": "offererVenue", "otherAddress": "some address"}
        )

        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        client = client.with_session_auth(email="user@example.com")
        response = client.get(f"/collective/offers/{offer.id}")

        assert response.status_code == 200
        assert response.json["offerVenue"] == {
            "venueId": None,
            "addressType": "offererVenue",
            "otherAddress": "some address",
        }

    def test_offer_with_empty_string_subcategory_instead_of_none(self, client):
        """Test that an offer with a legal but unexpected subcategory
        (empty string instead if none) can be serialized.
        """
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, subcategoryId="")
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        dst = url_for("Private API.get_collective_offer", offer_id=offer.id)
        response = client.with_session_auth(user.email).get(dst)

        assert response.status_code == 200
        assert response.json["subcategoryId"] is None


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email=pro_user.email)
        response = client.get(f"/collective/offers/{offer.id}")

        # Then
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
        response = client.with_session_auth(email=pro_user.email).get(dst)

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

        response = client.with_session_auth(email=pro_user.email).get(dst)

        assert response.status_code == 404
