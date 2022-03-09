from datetime import datetime

import pytest

from pcapi.domain.payments import make_transaction_label


class PaymentTransactionLabelTest:
    @pytest.mark.parametrize("date", [datetime(2018, 7, d) for d in range(1, 15)])
    def test_in_first_half_of_a_month(self, date):
        # when
        message = make_transaction_label(date)

        # then
        assert message == "pass Culture Pro - remboursement 1ère quinzaine 07-2018"

    @pytest.mark.parametrize("date", [datetime(2018, 7, d) for d in range(15, 31)])
    def test_in_second_half_of_a_month(self, date):
        # when
        message = make_transaction_label(date)

        # then
        assert message == "pass Culture Pro - remboursement 2nde quinzaine 07-2018"
