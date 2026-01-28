from datetime import datetime
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.utils import date
from pcapi.utils import date as date_utils
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.settings(USE_FAST_AND_INSECURE_PASSWORD_HASHING_ALGORITHM=True)
class Returns200Test:
    num_queries = 1  # select user_session + user
    num_queries += 1  # select booking, stock, offer, venue, address
    num_queries += 1  # check user has rights on offerer
    num_queries += 1  # check if a pricing processed or invoiced exists for this booking
    num_queries += 1  # select user

    def test_when_user_has_rights_and_regular_offer(self, client):
        past = date_utils.get_naive_utc_now() - timedelta(days=2)
        booking = bookings_factories.BookingFactory(
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, months=2),
            stock__beginningDatetime=past,
            stock__offer=offers_factories.EventOfferFactory(
                extraData={
                    "theater": {"allocine_movie_id": 165, "allocine_room_id": 987},
                },
                subcategoryId=subcategories.CARTE_CINE_MULTISEANCES.id,
                name="An offer you cannot refuse",
                venue__name="Le Petit Rintintin",
            ),
        )
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=booking.offerer)

        client = client.with_session_auth(pro.email)
        booking_token = booking.token
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/bookings/token/{booking_token}")
            assert response.status_code == 200

        assert response.headers["Content-type"] == "application/json"
        assert response.json == {
            "bookingId": humanize(booking.id),
            "dateOfBirth": booking.user.birth_date.isoformat(),
            "datetime": date.format_into_utc_date(booking.stock.beginningDatetime),
            "ean13": None,
            "email": "beneficiary@example.com",
            "isUsed": False,
            "offerId": booking.stock.offerId,
            "offerName": "An offer you cannot refuse",
            "offerType": "EVENEMENT",
            "phoneNumber": "+33101010101",
            "price": 10.1,
            "priceCategoryLabel": None,
            "publicOfferId": humanize(booking.stock.offerId),
            "quantity": 1,
            "userName": booking.user.full_name,
            "firstName": booking.user.firstName,
            "lastName": booking.user.lastName,
            "offerAddress": booking.stock.offer.offererAddress.address.street,
            "offerDepartmentCode": booking.stock.offer.offererAddress.address.departmentCode,
            "venueName": "Le Petit Rintintin",
        }

    def test_when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, client):
        booking = bookings_factories.BookingFactory(
            stock__beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=2),
        )
        booking_token = booking.token.lower()
        user_offerer = offerers_factories.UserOffererFactory(offerer=booking.offerer)
        pro_user = user_offerer.user

        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/bookings/token/{booking_token}")
            assert response.status_code == 200


class Returns401Test:
    def test_when_user_no_auth_nor_api_key(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/bookings/token/TOKEN")
            assert response.status_code == 401


class Returns403Test:
    def test_when_user_doesnt_have_rights_and_token_exists(self, client):
        booking = bookings_factories.BookingFactory()
        another_pro_user = users_factories.ProFactory()

        url = f"/bookings/token/{booking.token}"
        client = client.with_session_auth(another_pro_user.email)
        num_queries = 1  # select user_session + user
        num_queries += 1  # select booking
        num_queries += 1  # check user has rights on offerer
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        with testing.assert_num_queries(num_queries):
            response = client.get(url)
            assert response.status_code == 404

        assert response.json["global"] == [
            "La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder."
        ]

    def test_when_booking_not_confirmed(self, client):
        next_week = date_utils.get_naive_utc_now() + timedelta(weeks=1)
        booking = bookings_factories.BookingFactory(stock__beginningDatetime=next_week)
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=booking.offerer)

        url = f"/bookings/token/{booking.token}"
        num_queries = 1  # select user_session + user
        num_queries += 1  # select booking, stock, offer, venue, address
        num_queries += 1  # check user has rights on offerer
        num_queries += 1  # check if a pricing processed or invoiced exists for this booking
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        client = client.with_session_auth(pro.email)
        with testing.assert_num_queries(num_queries):
            response = client.get(url)
            assert response.status_code == 403

        cancellation_limit_date = datetime.strftime(
            date.utc_datetime_to_department_timezone(
                booking.cancellationLimitDate, booking.venue.offererAddress.address.departmentCode
            ),
            "%d/%m/%Y à %H:%M",
        )
        assert (
            response.json["booking"][0]
            == f"Vous pourrez valider cette contremarque à partir du {cancellation_limit_date}, une fois le délai d’annulation passé."
        )

    def test_when_booking_is_refunded(self, client):
        booking = bookings_factories.ReimbursedBookingFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=booking.offerer)

        url = f"/bookings/token/{booking.token}"
        num_queries = 1  # select user_session + user
        num_queries += 1  # Select booking
        num_queries += 1  # check user has rights on offerer
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        client = client.with_session_auth(pro.email)
        with testing.assert_num_queries(num_queries):
            response = client.get(url)
            assert response.status_code == 403

        assert response.json["payment"] == ["Cette réservation a été remboursée"]

    def test_when_offerer_is_closed(self, client):
        offerer = offerers_factories.ClosedOffererFactory()
        booking = bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer)
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=booking.offerer)

        url = f"/bookings/token/{booking.token}"
        num_queries = 1  # Select user session + user
        num_queries += 1  # Select booking
        num_queries += 1  # check user has rights on offerer
        num_queries += 1  # check if a pricing processed or invoiced exists for this booking
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        client = client.with_session_auth(pro.email)
        with testing.assert_num_queries(num_queries):
            response = client.get(url)
            assert response.status_code == 403

        assert response.json["booking"] == ["Vous ne pouvez plus valider de contremarque sur une structure fermée"]
        assert booking.status == bookings_models.BookingStatus.CONFIRMED


class Returns404Test:
    def test_missing_token(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/bookings/token/")
            assert response.status_code == 404

    def test_basic_auth_but_unknown_token(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)
        num_queries = 1  # Select user session + user
        num_queries += 1  # select booking
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        with testing.assert_num_queries(num_queries):
            response = client.get("/bookings/token/UNKNOWN")
            assert response.status_code == 404

        assert response.json["global"] == [
            "La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder."
        ]


class Returns410Test:
    def test_when_booking_is_already_validated(self, client):
        booking = bookings_factories.UsedBookingFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=booking.offerer)

        client = client.with_session_auth(pro.email)
        num_queries = 1  # Select user session + user
        num_queries += 1  # Select booking
        num_queries += 1  # check user has rights on offerer
        num_queries += 1  # check if a pricing processed or invoiced exists for this booking
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        token = booking.token
        with testing.assert_num_queries(num_queries):
            response = client.get(f"/bookings/token/{token}")
            assert response.status_code == 410

        assert response.json["booking"] == ["Cette réservation a déjà été validée"]

    def test_when_booking_is_cancelled(self, client):
        booking = bookings_factories.CancelledBookingFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=booking.offerer)

        url = f"/bookings/token/{booking.token}"
        num_queries = 1  # Select user session + user
        num_queries += 1  # Select booking
        num_queries += 1  # check user has rights on offerer
        num_queries += 1  # check if a pricing processed or invoiced exists for this booking
        num_queries += 1  # rollback atomic
        num_queries += 1  # rollback atomic
        client = client.with_session_auth(pro.email)
        with testing.assert_num_queries(num_queries):
            response = client.get(url)
            assert response.status_code == 410

        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
