import datetime
from decimal import Decimal

import pytest

from pcapi.core.bookings.factories import UsedEducationalBookingFactory
from pcapi.core.bookings.factories import UsedIndividualBookingFactory
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import assert_num_queries
from pcapi.domain.payments import generate_payment_details_csv
from pcapi.domain.payments import generate_wallet_balances_csv
from pcapi.models.payment import Payment
from pcapi.models.wallet_balance import WalletBalance
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class GeneratePaymentDetailsCsvTest:
    def test_generate_csv(self):
        creation_date = datetime.datetime(2020, 1, 1)
        used_date = datetime.datetime(2020, 1, 2)
        venue1 = offers_factories.VenueFactory(
            name="Le Petit Rintintin",
            siret="11111111122222",
            managingOfferer__name="Le Petit Rintintin Management Ltd.",
            managingOfferer__siren="111111111",
        )
        payment_message = payments_factories.PaymentMessageFactory()
        p1_booking = UsedIndividualBookingFactory(
            amount=10,
            dateCreated=creation_date,
            dateUsed=used_date,
            stock__offer__product__name="Une histoire formidable",
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            stock__offer__venue=venue1,
        )
        p1 = payments_factories.PaymentFactory(
            booking=p1_booking,
            iban="IBAN1",
            amount=9,
            reimbursementRate=0.9,
            paymentMessage=payment_message,
        )
        venue2 = offers_factories.VenueFactory(
            name="Le Gigantesque Cubitus",
            siret="22222222233333",
            managingOfferer__name="Le Gigantesque Cubitus Management Ltd.",
            managingOfferer__siren="222222222",
        )
        p2_booking = UsedIndividualBookingFactory(
            amount=12,
            dateCreated=creation_date,
            dateUsed=used_date,
            stock__offer__product__name="Une histoire plutôt bien",
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            stock__offer__venue=venue2,
        )
        p2 = payments_factories.PaymentFactory(
            booking=p2_booking,
            iban="IBAN2",
            amount=11,
            reimbursementRate=None,
            reimbursementRule=None,
            customReimbursementRule=payments_factories.CustomReimbursementRuleFactory(),
            paymentMessage=payment_message,
        )
        p3_booking = UsedEducationalBookingFactory(
            amount=12,
            dateCreated=creation_date,
            dateUsed=used_date,
            stock__offer__product__name="Une histoire plutôt bien",
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            stock__offer__venue=venue2,
        )
        p3 = payments_factories.PaymentFactory(
            booking=p3_booking,
            iban="IBAN2",
            amount=11,
            reimbursementRate=None,
            reimbursementRule=None,
            customReimbursementRule=payments_factories.CustomReimbursementRuleFactory(),
            paymentMessage=payment_message,
        )

        n_queries = 1  # select min(id), max(id) in `utils.db.get_batches()`
        n_queries += 1  # select payments
        with assert_num_queries(n_queries):
            csv = generate_payment_details_csv(Payment.query)

        rows = csv.splitlines()
        assert len(rows) == 4
        assert rows[0].split(",") == [
            '"Libellé fournisseur"',
            '"Raison sociale de la structure"',
            '"SIREN"',
            '"Raison sociale du lieu"',
            '"SIRET"',
            '"ID du lieu"',
            '"ID de l\'offre"',
            '"Nom de l\'offre"',
            '"Type de l\'offre"',
            '"Date de la réservation"',
            '"Prix de la réservation"',
            '"Type de réservation"',
            '"Date de validation"',
            '"IBAN"',
            '"Paiement ID"',
            '"Taux de remboursement"',
            '"Montant remboursé à l\'offreur"',
            '"Marge"',
        ]
        assert rows[1].split(",") == [
            '"Le Petit Rintintin Management Ltd.-Le Petit Rintintin"',
            '"Le Petit Rintintin Management Ltd."',
            '"111111111"',
            '"Le Petit Rintintin"',
            '"11111111122222"',
            f'"{humanize(venue1.id)}"',
            f'"{p1.booking.stock.offerId}"',
            '"Une histoire formidable"',
            '"Audiovisuel - films sur supports physiques et VOD"',
            '"2020-01-01 00:00:00"',
            '"10.00"',
            '"PC"',
            '"2020-01-02 00:00:00"',
            '"IBAN1"',
            f'"{p1.id}"',
            '"0.90"',
            '"9.00"',
            '"1.00"',
        ]
        assert rows[2].split(",") == [
            '"Le Gigantesque Cubitus Management Ltd.-Le Gigantesque Cubitus"',
            '"Le Gigantesque Cubitus Management Ltd."',
            '"222222222"',
            '"Le Gigantesque Cubitus"',
            '"22222222233333"',
            f'"{humanize(venue2.id)}"',
            f'"{p2.booking.stock.offerId}"',
            '"Une histoire plutôt bien"',
            '"Audiovisuel - films sur supports physiques et VOD"',
            '"2020-01-01 00:00:00"',
            '"12.00"',
            '"PC"',
            '"2020-01-02 00:00:00"',
            '"IBAN2"',
            f'"{p2.id}"',
            '"0.92"',
            '"11.00"',
            '"1.00"',
        ]
        assert rows[3].split(",") == [
            '"Le Gigantesque Cubitus Management Ltd.-Le Gigantesque Cubitus"',
            '"Le Gigantesque Cubitus Management Ltd."',
            '"222222222"',
            '"Le Gigantesque Cubitus"',
            '"22222222233333"',
            f'"{humanize(venue2.id)}"',
            f'"{p3.booking.stock.offerId}"',
            '"Une histoire plutôt bien"',
            '"Cinéma - projections et autres évènements"',
            '"2020-01-01 00:00:00"',
            '"12.00"',
            '"EACC"',
            '"2020-01-02 00:00:00"',
            '"IBAN2"',
            f'"{p3.id}"',
            '"0.92"',
            '"11.00"',
            '"1.00"',
        ]

    def test_only_header_if_no_payment(self):
        csv = generate_payment_details_csv(Payment.query)
        assert len(csv.splitlines()) == 1


class WalletBalancesCSVTest:
    def test_generate_wallet_balances_csv_has_human_readable_header(self):
        # Given
        balances = [
            WalletBalance(123, Decimal(100), Decimal(50)),
            WalletBalance(456, Decimal(120), Decimal(60)),
            WalletBalance(789, Decimal(80), Decimal(40)),
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
            WalletBalance(789, Decimal(80), Decimal(40)),
        ]

        # When
        csv = generate_wallet_balances_csv(balances)

        # Then
        assert _count_non_empty_lines(csv) == 4


def _get_header(csv):
    return csv.split("\n")[0]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != "", csv.split("\n"))))
