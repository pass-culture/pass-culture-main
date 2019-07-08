from datetime import datetime
from decimal import Decimal
from pprint import pprint
from typing import List, Tuple
from unittest.mock import Mock, patch
import os

import pytest

from models import PcObject
from scripts.payment.batch import generate_and_send_payments
from scripts.payment.batch_steps import generate_new_payments, concatenate_payments_with_errors_and_retries, \
    send_transactions, send_payments_report, send_payments_details, send_wallet_balances
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, create_offer_with_thing_product, create_stock_from_offer, \
    create_booking, create_user, create_deposit, create_payment, create_bank_information
from utils.mailing import parse_email_addresses


class GenerateNewPaymentsTest:
    @patch('os.environ', return_value={
        'PASS_CULTURE_IBAN': '1234567',
        'PASS_CULTURE_BIC': '1234567',
        'PASS_CULTURE_REMITTANCE_CODE': '1234567',
    })
    @patch('scripts.payment.batch.concatenate_payments_with_errors_and_retries', return_value=[])
    @patch('scripts.payment.batch.generate_new_payments', return_value=([], []))
    @patch('scripts.payment.batch.get_payments_by_message_id')
    @clean_database
    def test_should_retrieve_all_steps_when_messageId_is_None(self, get_payments_by_message_id, generate_new_payments, concatenate_payments_with_errors_and_retries, environment, app):
        # When
        generate_and_send_payments(None)

        # Then
        generate_new_payments.assert_called_once()
        concatenate_payments_with_errors_and_retries.assert_called_once()
        get_payments_by_message_id.assert_not_called()


    @patch('os.environ', return_value={
        'PASS_CULTURE_IBAN': '1234567',
        'PASS_CULTURE_BIC': '1234567',
        'PASS_CULTURE_REMITTANCE_CODE': '1234567',
    })
    @patch('scripts.payment.batch_steps.concatenate_payments_with_errors_and_retries', return_value={})
    @patch('scripts.payment.batch.generate_new_payments', return_value=([], []))
    @patch('scripts.payment.batch.get_payments_by_message_id', return_value=[])
    @clean_database
    def test_should_start_script_at_third_step_when_messageId_is_Given(self, get_payments_by_message_id, generate_new_payments, concatenate_payments_with_errors_and_retries, environment, app):
        # When
        generate_and_send_payments('ar5y65dtre45')

        # Then
        generate_new_payments.assert_not_called()
        get_payments_by_message_id.assert_called_once()
