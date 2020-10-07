from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.repository.reimbursement_queries import find_all_offerer_payments
from pcapi.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_deposit, \
    create_payment, create_payment_status
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer


class FindAllOffererPaymentsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_payment_info_with_error_status(self, app):
        # Given
        user = create_user(last_name='User', first_name='Plus')
        deposit = create_deposit(user)
        offerer = create_offerer(address='7 rue du livre')
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=10)
        now = datetime.utcnow()
        booking = create_booking(user=user, stock=stock, is_used=True, date_used=now,
                                 token='ABCDEF', venue=venue)

        payment = create_payment(booking, offerer,
                                 transaction_label='pass Culture Pro - remboursement 1ère quinzaine 07-2019',
                                 status=TransactionStatus.ERROR,
                                 amount=50,
                                 detail='Iban non fourni')
        repository.save(deposit, payment)

        # When
        payments = find_all_offerer_payments(offerer.id)

        # Then
        assert len(payments) == 1
        assert payments[0] == (
            'User',
            'Plus',
            'ABCDEF',
            now,
            'Test Book',
            '7 rue du livre',
            'La petite librairie',
            '12345678912345',
            '123 rue de Paris',
            Decimal('50.00'),
            None,
            'pass Culture Pro - remboursement 1ère quinzaine 07-2019',
            TransactionStatus.ERROR,
            'Iban non fourni')

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_payment_info_with_sent_status(self, app):
        # Given
        user = create_user(last_name='User', first_name='Plus')
        deposit = create_deposit(user)
        offerer = create_offerer(address='7 rue du livre')
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=10)
        now = datetime.utcnow()
        booking = create_booking(user=user, stock=stock, is_used=True, date_used=now,
                                 token='ABCDEF', venue=venue)

        payment = create_payment(booking, offerer,
                                 transaction_label='pass Culture Pro - remboursement 1ère quinzaine 07-2019',
                                 status=TransactionStatus.ERROR,
                                 amount=50,
                                 detail='Iban non fourni',
                                 status_date=now - timedelta(days=2))
        payment_status1 = create_payment_status(payment, detail='All good',
                                                status=TransactionStatus.RETRY,
                                                date=now - timedelta(days=1))
        payment_status2 = create_payment_status(payment, detail='All good',
                                                status=TransactionStatus.SENT)
        repository.save(deposit, payment, payment_status1, payment_status2)

        # When
        payments = find_all_offerer_payments(offerer.id)

        # Then
        assert len(payments) == 1
        assert payments[0] == (
            'User',
            'Plus',
            'ABCDEF',
            now,
            'Test Book',
            '7 rue du livre',
            'La petite librairie',
            '12345678912345',
            '123 rue de Paris',
            Decimal('50.00'),
            None,
            'pass Culture Pro - remboursement 1ère quinzaine 07-2019',
            TransactionStatus.SENT,
            'All good')

    @pytest.mark.usefixtures("db_session")
    def test_should_return_last_matching_status_based_on_date_for_each_payment(self, app):
        # Given
        user = create_user(last_name='User', first_name='Plus')
        deposit = create_deposit(user)
        offerer = create_offerer(address='7 rue du livre')
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue, price=10)
        now = datetime.utcnow()
        booking1 = create_booking(user=user, stock=stock, is_used=True, date_used=now,
                                  token='ABCDEF', venue=venue)
        booking2 = create_booking(user=user, stock=stock, is_used=True, date_used=now,
                                  token='ABCDFE', venue=venue)

        payment1 = create_payment(booking1, offerer,
                                  transaction_label='pass Culture Pro - remboursement 1ère quinzaine 07-2019',
                                  status=TransactionStatus.PENDING,
                                  amount=50,
                                  status_date=now - timedelta(days=2))
        payment2 = create_payment(booking2, offerer,
                                  transaction_label='pass Culture Pro - remboursement 2ème quinzaine 07-2019',
                                  status=TransactionStatus.PENDING,
                                  amount=75,
                                  status_date=now - timedelta(days=4))

        repository.save(deposit, payment1, payment2)

        last_status_for_payment1 = create_payment_status(payment1, detail='All good',
                                                         status=TransactionStatus.SENT,
                                                         date=now)
        last_status_for_payment2 = create_payment_status(payment2, detail=None,
                                                         status=TransactionStatus.SENT,
                                                         date=now)
        repository.save(last_status_for_payment1, last_status_for_payment2)

        first_status_for_payment1 = create_payment_status(payment1, detail='Retry',
                                                          status=TransactionStatus.RETRY,
                                                          date=now - timedelta(days=1))
        first_status_for_payment2 = create_payment_status(payment2, detail='Iban non fournis',
                                                          status=TransactionStatus.ERROR,
                                                          date=now - timedelta(days=3))
        repository.save(first_status_for_payment1, first_status_for_payment2)

        # When
        payments = find_all_offerer_payments(offerer.id)

        # Then
        assert len(payments) == 2
        assert payments[0] == (
            'User',
            'Plus',
            'ABCDFE',
            now,
            'Test Book',
            '7 rue du livre',
            'La petite librairie',
            '12345678912345',
            '123 rue de Paris',
            Decimal('75.00'),
            None,
            'pass Culture Pro - remboursement 2ème quinzaine 07-2019',
            TransactionStatus.SENT,
            None)
        assert payments[1] == (
            'User', 'Plus',
            'ABCDEF',
            now,
            'Test Book',
            '7 rue du livre',
            'La petite librairie',
            '12345678912345',
            '123 rue de Paris',
            Decimal('50.00'),
            None,
            'pass Culture Pro - remboursement 1ère quinzaine 07-2019',
            TransactionStatus.SENT,
            'All good')
