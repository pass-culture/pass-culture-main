from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core import testing
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_basics(self, client):
        # Given
        template = educational_factories.CollectiveOfferTemplateFactory()
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(
            collectiveStock=stock, teacher=educational_factories.EducationalRedactorFactory(), templateId=template.id
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
        assert response_json["imageCredit"] == None
        assert response_json["imageUrl"] == None
        assert "dateCreated" in response_json
        assert "institution" in response.json
        assert response.json["isVisibilityEditable"] == True
        assert response_json["nonHumanizedId"] == offer.id
        assert response_json["lastBookingStatus"] is None
        assert response_json["lastBookingId"] is None
        assert response_json["isPublicApi"] == False
        assert response_json["teacher"] == {
            "email": offer.teacher.email,
            "firstName": offer.teacher.firstName,
            "lastName": offer.teacher.lastName,
            "civility": offer.teacher.civility,
        }
        assert response_json["templateId"] == humanize(template.id)

    def test_sold_out(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        educational_factories.UsedCollectiveBookingFactory(collectiveStock=stock)
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email="user@example.com")
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

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
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

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
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

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
        humanized_offer_id = humanize(offer.id)

        with testing.assert_no_duplicated_queries():
            client.get(f"/collective/offers/{humanized_offer_id}")

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
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json["lastBookingId"] == booking.id
        assert response_json["lastBookingStatus"] == booking.status.value

    def test_inactive_offer(self, client):
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.utcnow() + timedelta(days=125),
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
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        assert response.json["status"] == "INACTIVE"
        assert response.json["isActive"] == False


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # When
        client = client.with_session_auth(email=pro_user.email)
        response = client.get(f"/collective/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 403
