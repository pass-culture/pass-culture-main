from datetime import datetime
from unittest.mock import patch

from dateutil.tz import tz
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.date import format_into_timezoned_date
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@patch("pcapi.core.bookings.repository.find_by_pro_user_id")
class GetAllBookingsTest:
    @pytest.mark.usefixtures("db_session")
    def test_call_repository_with_user_and_page(self, find_by_pro_user_id, app):
        user = users_factories.UserFactory()
        TestClient(app.test_client()).with_auth(user.email).get(f"/bookings/pro?page=3")
        find_by_pro_user_id.assert_called_once_with(user_id=user.id, page=3)

    @pytest.mark.usefixtures("db_session")
    def test_call_repository_with_page_1(self, find_by_pro_user_id, app):
        user = users_factories.UserFactory()
        TestClient(app.test_client()).with_auth(user.email).get(f"/bookings/pro")
        find_by_pro_user_id.assert_called_once_with(user_id=user.id, page=1)


@pytest.mark.usefixtures("db_session")
class GetTest:
    class Returns200Test:
        def when_user_is_linked_to_a_valid_offerer(self, app):
            booking = bookings_factories.BookingFactory(
                dateCreated=datetime(2020, 4, 3, 12, 0, 0),
                isUsed=True,
                dateUsed=datetime(2020, 5, 3, 12, 0, 0),
                token="ABCDEF",
                user__email="beneficiary@example.com",
                user__firstName="Hermione",
                user__lastName="Granger",
            )
            pro_user = users_factories.UserFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            client = TestClient(app.test_client()).with_auth(pro_user.email)
            response = client.get("/bookings/pro")

            expected_bookings_recap = [
                {
                    "stock": {
                        "type": "thing",
                        "offer_name": booking.stock.offer.name,
                        "offer_identifier": humanize(booking.stock.offer.id),
                    },
                    "beneficiary": {
                        "email": "beneficiary@example.com",
                        "firstname": "Hermione",
                        "lastname": "Granger",
                    },
                    "booking_date": format_into_timezoned_date(
                        booking.dateCreated.astimezone(tz.gettz("Europe/Paris")),
                    ),
                    "booking_amount": 10.0,
                    "booking_token": "ABCDEF",
                    "booking_status": "validated",
                    "booking_is_duo": False,
                    "booking_status_history": [
                        {
                            "status": "booked",
                            "date": format_into_timezoned_date(
                                booking.dateCreated.astimezone(tz.gettz("Europe/Paris")),
                            ),
                        },
                        {
                            "status": "validated",
                            "date": format_into_timezoned_date(
                                booking.dateUsed.astimezone(tz.gettz("Europe/Paris")),
                            ),
                        },
                    ],
                    "offerer": {
                        "name": offerer.name,
                    },
                    "venue": {
                        "identifier": humanize(booking.stock.offer.venue.id),
                        "is_virtual": booking.stock.offer.venue.isVirtual,
                        "name": booking.stock.offer.venue.name,
                    },
                }
            ]
            assert response.status_code == 200
            assert response.json["bookings_recap"] == expected_bookings_recap
            assert response.json["page"] == 1
            assert response.json["pages"] == 1
            assert response.json["total"] == 1

    class Returns400Test:
        def when_page_number_is_not_a_number(self, app):
            user = users_factories.UserFactory()

            client = TestClient(app.test_client()).with_auth(user.email)
            response = client.get(f"/bookings/pro?page=not-a-number")

            assert response.status_code == 400
            assert response.json["global"] == ["L'argument 'page' not-a-number n'est pas valide"]

    class Returns401Test:
        def when_user_is_admin(self, app):
            user = users_factories.UserFactory(isAdmin=True, canBookFreeOffers=False)

            client = TestClient(app.test_client()).with_auth(user.email)
            response = client.get("/bookings/pro")

            assert response.status_code == 401
            assert response.json == {
                "global": ["Le statut d'administrateur ne permet pas d'accéder au suivi des réservations"]
            }
