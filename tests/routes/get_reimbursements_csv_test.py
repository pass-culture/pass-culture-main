from models import PcObject
from scripts.payment.batch_steps import generate_new_payments
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, create_deposit, \
    create_user_offerer, create_bank_information
from tests.model_creators.specific_creators import create_stock_with_thing_offer


class Get:
    class Returns200:
        @clean_database
        def when_user_has_an_offerer_attached(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            deposit = create_deposit(user, amount=500, source='public')
            offerer1 = create_offerer()
            offerer2 = create_offerer(siren='123456788')
            user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
            user_offerer2 = create_user_offerer(user, offerer2, validation_token=None)
            venue1 = create_venue(offerer1)
            venue2 = create_venue(offerer1, siret='12345678912346')
            venue3 = create_venue(offerer2, siret='12345678912347')
            bank_information1 = create_bank_information(id_at_providers='79387501900056', venue=venue1)
            bank_information2 = create_bank_information(id_at_providers='79387501900057', venue=venue2)
            stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
            stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
            stock3 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, price=12)
            stock4 = create_stock_with_thing_offer(offerer=offerer2, venue=venue3, price=13)
            booking1 = create_booking(user=user, stock=stock1, is_used=True, token='ABCDEF', venue=venue1)
            booking2 = create_booking(user=user, stock=stock1, token='ABCDEG', venue=venue1)
            booking3 = create_booking(user=user, stock=stock2, is_used=True, token='ABCDEH', venue=venue2)
            booking4 = create_booking(user=user, stock=stock3, is_used=True, token='ABCDEI', venue=venue3)
            booking5 = create_booking(user=user, stock=stock4, is_used=True, token='ABCDEJ', venue=venue3)
            booking6 = create_booking(user=user, stock=stock4, is_used=True, token='ABCDEK', venue=venue3)
            PcObject.save(deposit, booking1, booking2, booking3,
                          booking4, booking5, booking6, user_offerer1,
                          user_offerer2, bank_information1, bank_information2)
            generate_new_payments()

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/reimbursements/csv')
            response_lines = response.data.decode('utf-8').split('\n')

            # Then
            assert response.status_code == 200
            assert response.headers['Content-type'] == 'text/csv; charset=utf-8;'
            assert response.headers['Content-Disposition'] == 'attachment; filename=remboursements_pass_culture.csv'
            assert len(response_lines) == 7

        @clean_database
        def when_user_has_no_offerer_attached(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            PcObject.save(user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                '/reimbursements/csv')
            response_lines = response.data.decode('utf-8').split('\n')

            # Then
            assert response.status_code == 200
            assert len(response_lines) == 2
