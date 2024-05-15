from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_user_can_access_collective_booking_in_new_bank_account_journey_context(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )
        booking_id = booking.id

        client = client.with_session_auth(user_offerer.user.email)
        queries = AUTHENTICATION_QUERIES
        queries += 1  # select booking
        queries += 1  # select exists user_offerer (access check)
        queries += 1  # select bank account
        with assert_num_queries(queries):
            response = client.get(f"collective/bookings/{booking_id}")

        assert response.status_code == 200
        assert response.json == {
            "id": booking.id,
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": None},
            "beginningDatetime": booking.collectiveStock.startDatetime.isoformat(),
            "students": ["Lycée - Seconde"],
            "bankAccountStatus": "MISSING",
            "venueDMSApplicationId": None,
            "price": float(booking.collectiveStock.price),
            "educationalInstitution": {
                "id": booking.educationalInstitution.id,
                "institutionType": booking.educationalInstitution.institutionType,
                "name": booking.educationalInstitution.name,
                "city": booking.educationalInstitution.city,
                "postalCode": booking.educationalInstitution.postalCode,
                "phoneNumber": booking.educationalInstitution.phoneNumber,
                "institutionId": booking.educationalInstitution.institutionId,
            },
            "educationalRedactor": {
                "id": booking.educationalRedactor.id,
                "civility": booking.educationalRedactor.civility,
                "email": booking.educationalRedactor.email,
                "firstName": booking.educationalRedactor.firstName,
                "lastName": booking.educationalRedactor.lastName,
            },
            "numberOfTickets": booking.collectiveStock.numberOfTickets,
            "venuePostalCode": booking.venue.postalCode,
            "isCancellable": booking.is_cancellable_from_offerer,
            "venueId": booking.venueId,
            "offererId": booking.venue.managingOffererId,
        }

    def test_user_can_access_collective_booking_with_correct_bank_account_status_new_bank_account_journey(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        bank_account = finance_factories.BankAccountFactory(
            offerer=user_offerer.offerer, status=finance_models.BankAccountApplicationStatus.ACCEPTED
        )
        offerers_factories.VenueBankAccountLinkFactory(
            bankAccount=bank_account, venue=venue, timespan=(datetime.utcnow() - timedelta(days=365), None)
        )
        booking = educational_factories.CollectiveBookingFactory(collectiveStock__collectiveOffer__venue=venue)
        booking_id = booking.id

        client = client.with_session_auth(user_offerer.user.email)
        queries = AUTHENTICATION_QUERIES
        queries += 1  # select booking
        queries += 1  # select exists user_offerer (access check)
        queries += 1  # select bank account
        with assert_num_queries(queries):
            response = client.get(f"collective/bookings/{booking_id}")

        assert response.status_code == 200
        assert response.json == {
            "id": booking.id,
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": None},
            "beginningDatetime": booking.collectiveStock.startDatetime.isoformat(),
            "students": ["Lycée - Seconde"],
            "bankAccountStatus": "ACCEPTED",
            "venueDMSApplicationId": bank_account.dsApplicationId,
            "price": float(booking.collectiveStock.price),
            "educationalInstitution": {
                "id": booking.educationalInstitution.id,
                "institutionType": booking.educationalInstitution.institutionType,
                "name": booking.educationalInstitution.name,
                "city": booking.educationalInstitution.city,
                "postalCode": booking.educationalInstitution.postalCode,
                "phoneNumber": booking.educationalInstitution.phoneNumber,
                "institutionId": booking.educationalInstitution.institutionId,
            },
            "educationalRedactor": {
                "id": booking.educationalRedactor.id,
                "civility": booking.educationalRedactor.civility,
                "email": booking.educationalRedactor.email,
                "firstName": booking.educationalRedactor.firstName,
                "lastName": booking.educationalRedactor.lastName,
            },
            "numberOfTickets": booking.collectiveStock.numberOfTickets,
            "venuePostalCode": booking.venue.postalCode,
            "isCancellable": booking.is_cancellable_from_offerer,
            "venueId": booking.venueId,
            "offererId": booking.venue.managingOffererId,
        }


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_when_booking_not_found(self, client):
        user = users_factories.ProFactory()

        client = client.with_session_auth(user.email)
        response = client.get("collective/bookings/0")

        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_no_rights(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"collective/bookings/{booking.id}")

        assert response.status_code == 403
