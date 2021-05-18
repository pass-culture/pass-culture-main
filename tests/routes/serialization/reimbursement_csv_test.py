from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.payments.factories import PaymentFactory
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository.reimbursement_queries import find_all_offerer_payments
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import _get_reimbursement_current_status_in_details
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.scripts.payment.batch_steps import generate_new_payments


class ReimbursementDetailsTest:
    @pytest.mark.usefixtures("db_session")
    def test_reimbursementDetail_as_csv(self, app):
        # given
        payment = PaymentFactory(transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019")

        payments_info = find_all_offerer_payments(payment.booking.stock.offer.venue.managingOfferer.id)

        # when
        raw_csv = ReimbursementDetails(payments_info[0]).as_csv_row()

        # then
        assert raw_csv[0] == "2019"
        assert raw_csv[1] == "Juillet : remboursement 1ère quinzaine"
        assert raw_csv[2] == payment.booking.stock.offer.venue.name
        assert raw_csv[3] == payment.booking.stock.offer.venue.siret
        assert raw_csv[4] == payment.booking.stock.offer.venue.address
        assert raw_csv[5] == payment.iban
        assert raw_csv[6] == payment.booking.stock.offer.venue.name
        assert raw_csv[7] == payment.booking.stock.offer.name
        assert raw_csv[8] == "Doux"
        assert raw_csv[9] == "Jeanne"
        assert raw_csv[10] == payment.booking.token
        assert raw_csv[11] == payment.booking.dateUsed
        assert raw_csv[12] == payment.booking.amount
        assert raw_csv[13] == "Remboursement en cours"


@pytest.mark.parametrize(
    "current_status,expected_display",
    [
        (TransactionStatus.PENDING, "Remboursement en cours"),
        (TransactionStatus.NOT_PROCESSABLE, "Remboursement impossible : Iban Non Fourni"),
        (TransactionStatus.SENT, "Remboursement envoyé"),
        (TransactionStatus.RETRY, "Remboursement à renvoyer"),
        (TransactionStatus.BANNED, "Remboursement rejeté"),
        (TransactionStatus.ERROR, "Remboursement en cours"),
        (TransactionStatus.UNDER_REVIEW, "Remboursement en cours"),
    ],
)
def test_human_friendly_status_can_contain_details_only_for_not_processable_transaction(
    current_status, expected_display
):
    # given
    current_status_details = "Iban Non Fourni"

    # when
    human_friendly_status = _get_reimbursement_current_status_in_details(current_status, current_status_details)

    # then
    assert human_friendly_status == expected_display


def test_human_friendly_status_contains_details_for_not_processable_transaction_only_when_details_exists():
    # given
    current_status = TransactionStatus.NOT_PROCESSABLE
    current_status_details = ""

    # when
    human_friendly_status = _get_reimbursement_current_status_in_details(current_status, current_status_details)

    # then
    assert human_friendly_status == "Remboursement impossible"


@freeze_time("2019-07-10")
class ReimbursementDetailsCSVTest:
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_details_csv_with_human_readable_header(self, app):
        # given
        reimbursement_details = []

        # when
        csv = generate_reimbursement_details_csv(reimbursement_details)

        # then
        assert (
            _get_line(csv, 0)
            == '"Année";"Virement";"Créditeur";"SIRET créditeur";"Adresse créditeur";"IBAN";"Raison sociale du lieu";"Nom de l\'offre";"Nom utilisateur";"Prénom utilisateur";"Contremarque";"Date de validation de la réservation";"Montant remboursé";"Statut du remboursement"'
        )

    @freeze_time("2019-07-05 12:00:00")
    @pytest.mark.usefixtures("db_session")
    def test_generate_payment_details_csv_with_right_values(self, app):
        # given
        stock = offers_factories.StockFactory(price=10, offer__name='Mon titre ; un peu "spécial"')
        venue = stock.offer.venue
        user_offerer = offers_factories.UserOffererFactory(offerer=venue.managingOfferer)
        bank_informations = offers_factories.BankInformationFactory(venue=venue)
        bookings_factories.BookingFactory(stock=stock, isUsed=True, token="0E2722")
        bookings_factories.BookingFactory(stock=stock, token="LDVNNW")

        generate_new_payments()

        reimbursement_details = find_all_offerer_reimbursement_details(user_offerer.offererId)

        # when
        csv = generate_reimbursement_details_csv(reimbursement_details)

        # then
        assert _count_non_empty_lines(csv) == 2
        assert (
            _get_line(csv, 1)
            == f'"2019";"Juillet : remboursement 1ère quinzaine";"{venue.name}";"{venue.siret}";"1 boulevard Poissonnière";"{bank_informations.iban}";"{venue.name}";"Mon titre ; un peu ""spécial""";"Doux";"Jeanne";"0E2722";"";10.00;"Remboursement en cours"'
        )


class FindReimbursementDetailsTest:
    @pytest.mark.usefixtures("db_session")
    def test_find_all_offerer_reimbursement_details(self, app):
        # Given
        user = users_factories.UserFactory(email="user+plus@email.fr")
        offerer1 = create_offerer(siren="123456789")
        venue1 = create_venue(offerer1)
        venue2 = create_venue(offerer1, siret="12345678912346")
        create_offer_with_thing_product(venue1, url="https://host/path/{token}?offerId={offerId}&email={email}")
        create_offer_with_thing_product(venue2)
        stock1 = create_stock_with_thing_offer(offerer=offerer1, venue=venue1, price=10)
        stock2 = create_stock_with_thing_offer(offerer=offerer1, venue=venue2, price=11)
        create_booking(user=user, stock=stock1, is_used=True, token="ABCDEF", venue=venue1)
        create_booking(user=user, stock=stock1, token="ABCDEG", venue=venue1)
        create_booking(user=user, stock=stock2, is_used=True, token="ABCDEH", venue=venue2)
        generate_new_payments()

        # When
        reimbursement_details = find_all_offerer_reimbursement_details(offerer1.id)

        # Then
        assert len(reimbursement_details) == 2


def _get_line(csv, line):
    return csv.split("\r\n")[line]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != "", csv.split("\r\n"))))
