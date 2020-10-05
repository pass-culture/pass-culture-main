from datetime import datetime
from unittest.mock import patch

from dateutil.tz import tz
from pytest import fixture
from pytest_mock import mocker

from repository import repository
import pytest
from tests.conftest import TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue, \
    create_stock, create_booking
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.date import format_into_timezoned_date
from utils.human_ids import humanize


class GetAllBookingsTest:
    @patch('routes.bookings.get_all_bookings_by_pro_user')
    @pytest.mark.usefixtures("db_session")
    def test_should_call_the_usecase_with_user_id_and_page(self,
                                                           get_all_bookings_by_pro_user: mocker,
                                                           app: fixture):
        # Given
        user = create_user(is_admin=True, can_book_free_offers=False)
        repository.save(user)
        page_number = 3

        # When
        TestClient(app.test_client()) \
            .with_auth(user.email) \
            .get(f'/bookings/pro?page={page_number}')

        # Then
        get_all_bookings_by_pro_user.assert_called_once_with(user_id=user.id, page=page_number)

    @patch('routes.bookings.get_all_bookings_by_pro_user')
    @pytest.mark.usefixtures("db_session")
    def test_should_call_the_usecase_with_1_when_no_page_provided(self,
                                                                  get_all_bookings_by_pro_user: mocker,
                                                                  app: fixture):
        # Given
        user = create_user(is_admin=True, can_book_free_offers=False)
        repository.save(user)

        # When
        TestClient(app.test_client()) \
            .with_auth(user.email) \
            .get(f'/bookings/pro')

        # Then
        get_all_bookings_by_pro_user.assert_called_once_with(user_id=user.id, page=1)


class GetTest:
    class Returns200Test:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_linked_to_a_valid_offerer(self, app: fixture):
            # Given
            beneficiary = create_user(email='beneficiary@example.com', first_name="Hermione", last_name="Granger")
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, idx=15)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock(offer=offer, price=0)
            date_created = datetime(2020, 4, 3, 12, 0, 0)
            date_used = datetime(2020, 5, 3, 12, 0, 0)
            booking = create_booking(user=beneficiary, stock=stock, token="ABCD", date_created=date_created,
                                     is_used=True, date_used=date_used)
            repository.save(user_offerer, booking)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get('/bookings/pro')

            # Then
            expected_bookings_recap = [
                {
                    'stock': {
                        'type': 'thing',
                        'offer_name': 'Test Book',
                        'offer_identifier': humanize(offer.id),
                    },
                    'beneficiary': {
                        'email': 'beneficiary@example.com',
                        'firstname': 'Hermione',
                        'lastname': 'Granger',
                    },
                    'booking_date': format_into_timezoned_date(
                        date_created.astimezone(tz.gettz('Europe/Paris'))
                    ),
                    'booking_amount': 0.0,
                    'booking_token': 'ABCD',
                    'booking_status': 'validated',
                    'booking_is_duo': False,
                    'booking_status_history': [
                        {
                            'status': 'booked',
                            'date': format_into_timezoned_date(
                                date_created.astimezone(tz.gettz('Europe/Paris'))
                            ),
                        },
                        {
                            'status': 'validated',
                            'date': format_into_timezoned_date(
                                date_used.astimezone(tz.gettz('Europe/Paris'))
                            ),
                        },
                    ],
                    'offerer': {
                        'name': offerer.name
                    },
                    'venue': {
                        'identifier': 'B4',
                        'is_virtual': venue.isVirtual,
                        'name': venue.name
                    }
                }
            ]
            assert response.status_code == 200
            assert response.json['bookings_recap'] == expected_bookings_recap
            assert response.json['page'] == 1
            assert response.json['pages'] == 1
            assert response.json['total'] == 1

    class Returns400Test:
        @pytest.mark.usefixtures("db_session")
        def when_page_number_is_not_a_number(self, app: fixture):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            repository.save(user)
            page_number = 'not a number'

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get(f'/bookings/pro?page={page_number}')

            # Then
            assert response.status_code == 400
            assert response.json == {
                'global': [f"L'argument 'page' {page_number} n'est pas valide"]
            }

    class Returns401Test:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_admin(self, app: fixture):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            repository.save(user)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get('/bookings/pro')

            # Then
            assert response.status_code == 401
            assert response.json == {
                'global': ["Le statut d'administrateur ne permet pas d'accéder au suivi des réservations"]
            }
