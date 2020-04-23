from datetime import datetime
from decimal import Decimal

from domain.payments import generate_payment_details_csv, generate_wallet_balances_csv
from models.user_sql_entity import WalletBalance
from tests.model_creators.generic_creators import create_payment_details


class PaymentDetailsCSVTest:
    def test_generate_payment_details_csv_has_human_readable_header(self):
        # Given
        payments_details = [
            create_payment_details(),
            create_payment_details(),
            create_payment_details()
        ]

        # When
        csv = generate_payment_details_csv(payments_details)

        # Then
        assert _get_header(csv) == '"ID de l\'utilisateur","Email de l\'utilisateur",' \
                                   '"Raison sociale de la structure","SIREN",' \
                                   '"Raison sociale du lieu","SIRET","ID du lieu",' \
                                   '"Nom de l\'offre","Type de l\'offre",' \
                                   '"Date de la réservation","Prix de la réservation","Date de validation",' \
                                   '"IBAN","Payment Message Name","Transaction ID","Paiement ID",' \
                                   '"Taux de remboursement","Montant remboursé à l\'offreur"\r'

    def test_generate_payment_details_csv_with_headers_and_two_payment_details_lines(self):
        # Given
        payments_details = [
            create_payment_details(booking_date=datetime(2020, 1, 1), booking_used_date=datetime(2020, 1, 2)),
            create_payment_details(booking_date=datetime(2020, 1, 1), booking_used_date=datetime(2020, 1, 2)),
        ]

        # When
        csv = generate_payment_details_csv(payments_details)

        # Then
        assert _count_non_empty_lines(csv) == 3
        csv_as_lines = csv.splitlines()
        assert csv_as_lines[1] == "\"1234\"," \
                                  "\"john.doe@example.com\"," \
                                  "\"Les petites librairies\"," \
                                  "\"123456789\"," \
                                  "\"Vive les BDs\"," \
                                  "\"12345678912345\"," \
                                  "\"AE\"," \
                                  "\"Blake & Mortimer\"," \
                                  "\"ThingType.LIVRE_EDITION\"," \
                                  "\"2020-01-01 00:00:00\"," \
                                  "\"15\"," \
                                  "\"2020-01-02 00:00:00\"," \
                                  "\"FR7630001007941234567890185\"," \
                                  "\"AZERTY123456\"," \
                                  "\"None\"," \
                                  "\"123\"," \
                                  "\"0.5\"," \
                                  "\"7.5\""
        assert csv_as_lines[2] == "\"1234\"," \
                                  "\"john.doe@example.com\"," \
                                  "\"Les petites librairies\"," \
                                  "\"123456789\"," \
                                  "\"Vive les BDs\"," \
                                  "\"12345678912345\"," \
                                  "\"AE\"," \
                                  "\"Blake & Mortimer\"," \
                                  "\"ThingType.LIVRE_EDITION\"," \
                                  "\"2020-01-01 00:00:00\"," \
                                  "\"15\"," \
                                  "\"2020-01-02 00:00:00\"," \
                                  "\"FR7630001007941234567890185\"," \
                                  "\"AZERTY123456\"," \
                                  "\"None\"," \
                                  "\"123\"," \
                                  "\"0.5\"," \
                                  "\"7.5\""

    def test_generate_payment_details_csv_with_headers_and_zero_payment_details_lines(self):
        # Given
        payments_details = []

        # When
        csv = generate_payment_details_csv(payments_details)

        # Then
        assert _count_non_empty_lines(csv) == 1


class WalletBalancesCSVTest:
    def test_generate_wallet_balances_csv_has_human_readable_header(self):
        # Given
        balances = [
            WalletBalance(123, Decimal(100), Decimal(50)),
            WalletBalance(456, Decimal(120), Decimal(60)),
            WalletBalance(789, Decimal(80), Decimal(40))
        ]
        # When
        csv = generate_wallet_balances_csv(balances)

        # Then
        assert _get_header(csv) == '"ID de l\'utilisateur","Solde théorique","Solde réel"\r'

    def test_generate_wallet_balances_csv_with_headers_and_three_user_wallet_balances_lines(self):
        # Given
        balances = [
            WalletBalance(123, Decimal(100), Decimal(50)),
            WalletBalance(456, Decimal(120), Decimal(60)),
            WalletBalance(789, Decimal(80), Decimal(40))
        ]

        # When
        csv = generate_wallet_balances_csv(balances)

        # Then
        assert _count_non_empty_lines(csv) == 4


def _get_header(csv):
    return csv.split('\n')[0]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != '', csv.split('\n'))))
