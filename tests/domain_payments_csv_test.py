from domain.payments import generate_payment_details_csv
from utils.test_utils import create_payment_details


def test_generate_payment_details_csv_with_headers_and_three_payment_details_lines():
    # given
    payments_details = [
        create_payment_details(),
        create_payment_details(),
        create_payment_details()
    ]

    # when
    csv = generate_payment_details_csv(payments_details)

    # then
    assert _count_non_empty_lines(csv) == 4


def test_generate_payment_details_csv_with_headers_and_zero_payment_details_lines():
    # given
    payments_details = []

    # when
    csv = generate_payment_details_csv(payments_details)

    # then
    assert _count_non_empty_lines(csv) == 1


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != '', csv.split('\n'))))
