from unittest.mock import patch

from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user


class Get:
    class GetAllBookings:
        @patch('routes.bookings.get_all_bookings_by_pro_user')
        @clean_database
        def test_should_call_the_usecase_method_get_all_bookings_by_pro_user(self,
                                                                             get_all_bookings_by_pro_user,
                                                                             app):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            repository.save(user)

            # When
            TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get('/bookings/pro')

            # Then
            get_all_bookings_by_pro_user.assert_called_once_with(user.id)

    class Returns200:
        @clean_database
        def when_pro_have_multiple_offerer(self, app):
            # Given

            # When

            # Then
            pass

    class Returns400:
        @clean_database
        def when_user_is_admin(self, app):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            repository.save(user)

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get('/bookings/pro')

            # Then
            assert response.status_code == 400
            assert response.json == {
                'global': ["Le statut d'administrateur ne permet"
                           " pas d'accéder au suivi des réservations"]
            }
