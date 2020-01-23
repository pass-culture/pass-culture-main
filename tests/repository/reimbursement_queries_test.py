from repository import repository
from repository.reimbursement_queries import find_all_offerer_reimbursement_details
from scripts.payment.batch_steps import generate_new_payments
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, create_deposit, \
    create_user_offerer, create_bank_information
from tests.model_creators.specific_creators import create_stock_with_thing_offer, create_offer_with_thing_product


class FindReimbursementDetailsTest:
    @clean_database
    def test_find_all_offerer_reimbursement_details(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        deposit = create_deposit(user, amount=500, source='public')
        offerer1 = create_offerer(siren='123456789')
        user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
        venue1 = create_venue(offerer1)
        venue2 = create_venue(offerer1, siret='12345678912346')
        bank_information1 = create_bank_information(id_at_providers='79387501900056', venue=venue1)
        bank_information2 = create_bank_information(id_at_providers='79387501900057', venue=venue2)
        create_offer_with_thing_product(venue1, url='https://host/path/{token}?offerId={offerId}&email={email}')
        create_offer_with_thing_product(venue2)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
        stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
        booking1 = create_booking(user=user, stock=stock1, is_used=True, token='ABCDEF', venue=venue1)
        booking2 = create_booking(user=user, stock=stock1, token='ABCDEG', venue=venue1)
        booking3 = create_booking(user=user, stock=stock2, is_used=True, token='ABCDEH', venue=venue2)
        repository.save(deposit, booking1, booking2, booking3,
                      user_offerer1, bank_information1, bank_information2)
        generate_new_payments()

        # When
        reimbursement_details = find_all_offerer_reimbursement_details(offerer1.id)

        # Then
        assert len(reimbursement_details) == 2
