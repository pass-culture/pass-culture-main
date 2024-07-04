from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.date import isoformat
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_when_user_has_rights_and_regular_offer(self, client):
        # Given
        past = datetime.utcnow() - timedelta(days=2)
        booking = bookings_factories.BookingFactory(
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2),
            stock__beginningDatetime=past,
            stock__offer=offers_factories.EventOfferFactory(
                extraData={
                    "theater": {
                        "allocine_movie_id": 165,
                        "allocine_room_id": 987,
                    },
                },
                subcategoryId=subcategories.CARTE_CINE_MULTISEANCES.id,
                name="An offer you cannot refuse",
                venue__name="Le Petit Rintintin",
            ),
        )
        user_offerer = offerers_factories.UserOffererFactory(offerer=booking.offerer)
        pro_user = user_offerer.user

        # When
        client = client.with_basic_auth(pro_user.email)
        response = client.get(f"/v2/bookings/token/{booking.token}")

        # Then
        assert response.headers["Content-type"] == "application/json"
        assert response.status_code == 200
        assert response.json == {
            "bookingId": humanize(booking.id),
            "dateOfBirth": isoformat(booking.user.birth_date),
            "datetime": format_into_utc_date(booking.stock.beginningDatetime),
            "ean13": None,
            "email": "beneficiary@example.com",
            "formula": "ABO",
            "isUsed": False,
            "offerId": booking.stock.offerId,
            "offerName": "An offer you cannot refuse",
            "offerType": "EVENEMENT",
            "phoneNumber": "+33101010101",
            "price": 10.1,
            "priceCategoryLabel": None,
            "publicOfferId": humanize(booking.stock.offerId),
            "quantity": 1,
            "theater": {
                "allocine_movie_id": 165,
                "allocine_room_id": 987,
            },
            "userName": "Jeanne Doux",
            "firstName": "Jeanne",
            "lastName": "Doux",
            "venueAddress": "1 boulevard Poissonnière",
            "venueDepartmentCode": "75",
            "venueName": "Le Petit Rintintin",
        }

    def test_when_api_key_is_provided_and_rights_and_regular_offer(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        offerers_factories.ApiKeyFactory(offerer=booking.offerer, prefix="test_prefix")

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.get(url, headers={"Authorization": "Bearer test_prefix_clearSecret"})

        # Then
        assert response.status_code == 200

    def test_when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, client):
        # Given
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() - timedelta(days=2),
        )
        user_offerer = offerers_factories.UserOffererFactory(offerer=booking.offerer)
        pro_user = user_offerer.user

        # When
        client = client.with_basic_auth(pro_user.email)
        response = client.get(f"/v2/bookings/token/{booking.token.lower()}")

        # Then
        assert response.status_code == 200


class NonStandardGetTest:
    def test_non_standard_get_on_token_endpoint(self, client):
        # This is a test following the incident caused by a check on the JSON sent by API user (PR #12928 introduced the bug, PR #13062 fixed it)
        # Some legacy users are sending us an invalid JSON in a GET request to /v2/bookings/token/<token>
        # We must not raise an error in those cases otherwise it breaks their integrations.
        booking = bookings_factories.BookingFactory()
        offerers_factories.ApiKeyFactory(offerer=booking.offerer, prefix="test_prefix")

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.get_with_invalid_json_body(
            url,
            headers={"Authorization": "Bearer test_prefix_clearSecret"},
            raw_json="ABC",  # both sad an irritating
        )

        # Then
        assert response.status_code == 200


class Returns401Test:
    def test_when_user_no_auth_nor_api_key(self, client):
        response = client.get("/v2/bookings/token/TOKEN")
        assert response.status_code == 401

    def test_when_wrong_api_key(self, client):
        url = "/v2/bookings/token/FAKETOKEN"
        response = client.get(url, headers={"Authorization": "Bearer WrongApiKey1234567"})
        assert response.status_code == 401


class Returns403Test:
    def test_when_user_doesnt_have_rights_and_token_exists(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        another_pro_user = offerers_factories.UserOffererFactory().user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(another_pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]

    def test_when_given_api_key_not_related_to_booking_offerer(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        offerers_factories.ApiKeyFactory()  # another offerer's API key

        # When
        auth = "Bearer development_prefix_clearSecret"
        url = f"/v2/bookings/token/{booking.token}"
        response = client.get(url, headers={"Authorization": auth})

        # Then
        assert response.status_code == 403
        assert response.json["user"] == [
            "Vous n’avez pas les droits suffisants pour valider cette contremarque car cette réservation n'a pas été faite sur une de vos offres, ou que votre rattachement à la structure est encore en cours de validation"
        ]

    def test_when_booking_not_confirmed(self, client):
        # Given
        next_week = datetime.utcnow() + timedelta(weeks=1)
        booking = bookings_factories.BookingFactory(stock__beginningDatetime=next_week)
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        cancellation_limit_date = datetime.strftime(
            utc_datetime_to_department_timezone(booking.cancellationLimitDate, booking.venue.departementCode),
            "%d/%m/%Y à %H:%M",
        )
        assert (
            response.json["booking"][0]
            == f"Vous pourrez valider cette contremarque à partir du {cancellation_limit_date}, une fois le délai d’annulation passé."
        )

    def test_when_booking_is_refunded(self, client):
        # Given
        booking = bookings_factories.ReimbursedBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 403
        assert response.json["payment"] == ["Cette réservation a été remboursée"]


class Returns404Test:
    def test_missing_token(self, client):
        response = client.get("/v2/bookings/token/")
        assert response.status_code == 404

    def test_basic_auth_but_unknown_token(self, client):
        user = offerers_factories.UserOffererFactory().user
        client = client.with_basic_auth(user.email)
        response = client.get("/v2/bookings/token/UNKNOWN")

        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    def test_authenticated_with_api_key_but_token_not_found(self, client):
        offerers_factories.ApiKeyFactory(prefix="test_prefix")
        response = client.get("/v2/bookings/token/12345", headers={"Authorization": "Bearer test_prefix_clearSecret"})

        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    def test_when_booking_is_already_validated(self, client):
        booking = bookings_factories.UsedBookingFactory()
        user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        client = client.with_basic_auth(user.email)
        response = client.get(f"/v2/bookings/token/{booking.token}")

        assert response.status_code == 410
        assert response.json["booking"] == ["Cette réservation a déjà été validée"]

    def test_when_booking_is_cancelled(self, client):
        # Given
        booking = bookings_factories.CancelledBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).get(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
