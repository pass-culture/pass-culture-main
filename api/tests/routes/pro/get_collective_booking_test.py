from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @freeze_time("2022-05-01 15:00:00")
    def test_get_collective_booking(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory(
            id=dehumanize("EXCEL"),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"collective/bookings/{humanize(booking.id)}")

        assert response.status_code == 200
        assert response.json == {
            "id": booking.id,
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": None},
            "beginningDatetime": "2022-05-02T15:00:00",
            "students": ["Lycée - Seconde"],
            "bankInformationStatus": "MISSING",
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
            "venueId": humanize(booking.venueId),
            "offererId": humanize(booking.venue.managingOffererId),
        }

    @freeze_time("2022-05-01 15:00:00")
    def test_get_collective_booking_with_banking_informations(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=booking.collectiveStock.collectiveOffer.venue,
            reimbursementPoint__dmsToken="7490b4f8d5e3",
            reimbursementPoint__bankInformation=finance_factories.BankInformationFactory(
                status="DRAFT", applicationId=24881014
            ),
        )

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"collective/bookings/{humanize(booking.id)}")

        assert response.status_code == 200
        assert response.json == {
            "id": booking.id,
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": None},
            "beginningDatetime": "2022-05-02T15:00:00",
            "students": ["Lycée - Seconde"],
            "bankInformationStatus": "DRAFT",
            "venueDMSApplicationId": 24881014,
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
            "venueId": humanize(booking.venueId),
            "offererId": humanize(booking.venue.managingOffererId),
        }


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    @freeze_time("2022-05-01 15:00:00")
    def test_when_booking_not_found(self, client):
        user = users_factories.ProFactory()

        client = client.with_session_auth(user.email)
        response = client.get("collective/bookings/0")

        assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    @freeze_time("2022-05-01 15:00:00")
    def test_when_no_rights(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"collective/bookings/{humanize(booking.id)}")

        assert response.status_code == 403
