from decimal import Decimal

from domain.payments import generate_payment_details_csv, generate_wallet_balances_csv
from models.user import WalletBalance
from tests.model_creators.generic_creators import create_payment_details


class PaymentDetailsCSVTest:
    def test_generate_payment_details_csv_has_human_readable_header(self):
        # given
        payments_details = [
            create_payment_details(),
            create_payment_details(),
            create_payment_details()
        ]

        # when
        csv = generate_payment_details_csv(payments_details)

        # then
        assert _get_header(csv) == '"ID de l\'utilisateur","Email de l\'utilisateur",' \
                                   '"Raison sociale de la structure","SIREN",' \
                                   '"Raison sociale du lieu","SIRET",' \
                                   '"Nom de l\'offre","Type de l\'offre",' \
                                   '"Date de la réservation","Prix de la réservation","Date de validation",' \
                                   '"IBAN","Payment Message Name","Transaction ID","Paiement ID",' \
                                   '"Taux de remboursement","Montant remboursé à l\'offreur"\r'

    def test_generate_payment_details_csv_with_headers_and_three_payment_details_lines(self):
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

    def test_generate_payment_details_csv_with_headers_and_zero_payment_details_lines(self):
        # given
        payments_details = []

        # when
        csv = generate_payment_details_csv(payments_details)

        # then
        assert _count_non_empty_lines(csv) == 1


class WalletBalancesCSVTest:
    def test_generate_wallet_balances_csv_has_human_readable_header(self):
        # given
        balances = [
            WalletBalance(123, Decimal(100), Decimal(50)),
            WalletBalance(456, Decimal(120), Decimal(60)),
            WalletBalance(789, Decimal(80), Decimal(40))
        ]
        # when
        csv = generate_wallet_balances_csv(balances)

        # then
        assert _get_header(csv) == '"ID de l\'utilisateur","Solde théorique","Solde réel"\r'

    def test_generate_wallet_balances_csv_with_headers_and_three_user_wallet_balances_lines(self):
        # given
        balances = [
            WalletBalance(123, Decimal(100), Decimal(50)),
            WalletBalance(456, Decimal(120), Decimal(60)),
            WalletBalance(789, Decimal(80), Decimal(40))
        ]

        # when
        csv = generate_wallet_balances_csv(balances)

        # then
        assert _count_non_empty_lines(csv) == 4


def _get_header(csv):
    return csv.split('\n')[0]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != '', csv.split('\n'))))
