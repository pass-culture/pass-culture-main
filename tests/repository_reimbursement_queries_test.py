from datetime import datetime
import pytest

from models import PcObject
from repository.reimbursement_queries import find_all_offerer_reimbursement_details
from scripts.payment.batch_steps import generate_new_payments
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_bank_information, create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_deposit, create_stock_with_event_offer, create_venue, create_offerer, \
    create_recommendation, create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer

@pytest.mark.standalone
class FindReimbursementDetailsTest:
    @clean_database
    def test_find_all_offerer_reimbursement_details(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        deposit = create_deposit(user, datetime.utcnow(), amount=500, source='public')
        offerer1 = create_offerer()
        user_offerer1 = create_user_offerer(user, offerer1, validation_token=None)
        venue1 = create_venue(offerer1)
        venue2 = create_venue(offerer1, siret='12345678912346')
        bank_information1 = create_bank_information(id_at_providers='79387501900056', venue=venue1)
        bank_information2 = create_bank_information(id_at_providers='79387501900057', venue=venue2)

        offer1 = create_offer_with_thing_product(venue1, url='https://host/path/{token}?offerId={offerId}&email={email}')
        offer2 = create_offer_with_thing_product(venue2)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
        stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
        booking1 = create_booking(user, stock1, venue=venue1, token='ABCDEF', is_used=True)
        booking2 = create_booking(user, stock1, venue=venue1, token='ABCDEG')
        booking3 = create_booking(user, stock2, venue=venue2, token='ABCDEH', is_used=True)
        PcObject.check_and_save(deposit, booking1, booking2, booking3,
                                user_offerer1, bank_information1, bank_information2)
        generate_new_payments()

        # When
        reimbursement_details = find_all_offerer_reimbursement_details(offerer1.id)


        # Then
        assert len(reimbursement_details) == 2
