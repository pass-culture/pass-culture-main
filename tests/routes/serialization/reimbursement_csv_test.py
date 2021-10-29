from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as booking_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.payments.factories import PaymentFactory
from pcapi.core.payments.factories import PaymentWithCustomRuleFactory
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository.reimbursement_queries import find_all_offerer_payments
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import _get_reimbursement_current_status_in_details
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv


today = datetime.utcnow().date()
in_two_days = today + timedelta(days=2)
reimbursement_period = (today, in_two_days)


@pytest.mark.usefixtures("db_session")
class ReimbursementDetailsTest:
    def test_reimbursementDetail_as_csv_individual_booking(self, app):
        # given
        payment = PaymentFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            booking__amount=10.5,
            booking__quantity=2,
        )
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT)

        payments_info = find_all_offerer_payments(payment.booking.offerer.id, reimbursement_period)

        # when
        raw_csv = ReimbursementDetails(payments_info[0]).as_csv_row()

        # then
        assert raw_csv[0] == "2019"
        assert raw_csv[1] == "Juillet : remboursement 1ère quinzaine"
        assert raw_csv[2] == payment.booking.venue.name
        assert raw_csv[3] == payment.booking.venue.siret
        assert raw_csv[4] == payment.booking.venue.address
        assert raw_csv[5] == payment.iban
        assert raw_csv[6] == payment.booking.venue.name
        assert raw_csv[7] == payment.booking.stock.offer.name
        assert raw_csv[8] == "Doux"
        assert raw_csv[9] == "Jeanne"
        assert raw_csv[10] == payment.booking.token
        assert raw_csv[11] == payment.booking.dateUsed
        assert raw_csv[12] == "21,00"
        assert raw_csv[13] == f"{int(payment.reimbursementRate * 100)}%"
        assert raw_csv[14] == "21,00"
        assert raw_csv[15] == "Remboursement envoyé"

    def test_reimbursementDetail_as_csv_educational_booking(self, app):
        # given
        booking = booking_factories.UsedEducationalBookingFactory(amount=10.5, quantity=2)
        payment = PaymentFactory(
            booking=booking,
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT)

        payments_info = find_all_offerer_payments(payment.booking.offerer.id, reimbursement_period)

        # when
        raw_csv = ReimbursementDetails(payments_info[0]).as_csv_row()

        # then
        assert raw_csv[0] == "2019"
        assert raw_csv[1] == "Juillet : remboursement 1ère quinzaine"
        assert raw_csv[2] == payment.booking.venue.name
        assert raw_csv[3] == payment.booking.venue.siret
        assert raw_csv[4] == payment.booking.venue.address
        assert raw_csv[5] == payment.iban
        assert raw_csv[6] == payment.booking.venue.name
        assert raw_csv[7] == payment.booking.stock.offer.name
        assert raw_csv[8] == payment.booking.educationalBooking.educationalRedactor.lastName
        assert raw_csv[9] == payment.booking.educationalBooking.educationalRedactor.firstName
        assert raw_csv[10] == payment.booking.token
        assert raw_csv[11] == payment.booking.dateUsed
        assert raw_csv[12] == "21,00"
        assert raw_csv[13] == f"{int(payment.reimbursementRate * 100)}%"
        assert raw_csv[14] == "21,00"
        assert raw_csv[15] == "Remboursement envoyé"

    def test_reimbursementDetail_with_custom_rule_as_csv(self, app):
        # given
        payment = PaymentWithCustomRuleFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            booking__amount=10.5,
            booking__quantity=2,
        )
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT)

        payments_info = find_all_offerer_payments(payment.booking.offererId, reimbursement_period)

        # when
        raw_csv = ReimbursementDetails(payments_info[0]).as_csv_row()

        # then
        assert raw_csv[13] == ""


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


@pytest.mark.usefixtures("db_session")
def test_generate_reimbursement_details_csv():
    # given
    payment = PaymentFactory(
        booking__stock__offer__name='Mon titre ; un peu "spécial"',
        booking__stock__offer__venue__name='Mon lieu ; un peu "spécial"',
        booking__stock__offer__venue__siret="siret-1234",
        booking__token="0E2722",
        booking__amount=10.5,
        booking__quantity=2,
        booking__dateUsed=datetime(2021, 1, 1, 12, 0),
        iban="iban-1234",
        transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
    )
    payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT)
    offerer = payment.booking.offerer
    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

    # when
    csv = generate_reimbursement_details_csv(reimbursement_details)

    # then
    rows = csv.splitlines()
    assert (
        rows[0]
        == '"Année";"Virement";"Créditeur";"SIRET créditeur";"Adresse créditeur";"IBAN";"Raison sociale du lieu";"Nom de l\'offre";"Nom utilisateur";"Prénom utilisateur";"Contremarque";"Date de validation de la réservation";"Montant de la réservation";"Barème";"Montant remboursé";"Statut du remboursement"'
    )
    assert (
        rows[1]
        == '"2019";"Juillet : remboursement 1ère quinzaine";"Mon lieu ; un peu ""spécial""";"siret-1234";"1 boulevard Poissonnière";"iban-1234";"Mon lieu ; un peu ""spécial""";"Mon titre ; un peu ""spécial""";"Doux";"Jeanne";"0E2722";"2021-01-01 12:00:00";"21,00";"100%";"21,00";"Remboursement envoyé"'
    )


@pytest.mark.usefixtures("db_session")
def test_generate_reimbursement_details_csv_educational_booking():
    # given
    educational_booking = booking_factories.UsedEducationalBookingFactory(
        stock__offer__name='Mon titre ; un peu "spécial"',
        stock__offer__venue__name='Mon lieu ; un peu "spécial"',
        stock__offer__venue__siret="siret-1234",
        token="0E2722",
        amount=10.5,
        quantity=2,
        dateUsed=datetime(2021, 1, 1, 12, 0),
    )

    payment = PaymentFactory(
        booking=educational_booking,
        iban="iban-1234",
        transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
    )
    payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT)
    offerer = payment.booking.offerer
    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

    # when
    csv = generate_reimbursement_details_csv(reimbursement_details)

    # then
    rows = csv.splitlines()
    assert (
        rows[0]
        == '"Année";"Virement";"Créditeur";"SIRET créditeur";"Adresse créditeur";"IBAN";"Raison sociale du lieu";"Nom de l\'offre";"Nom utilisateur";"Prénom utilisateur";"Contremarque";"Date de validation de la réservation";"Montant de la réservation";"Barème";"Montant remboursé";"Statut du remboursement"'
    )
    assert (
        rows[1]
        == '"2019";"Juillet : remboursement 1ère quinzaine";"Mon lieu ; un peu ""spécial""";"siret-1234";"1 boulevard Poissonnière";"iban-1234";"Mon lieu ; un peu ""spécial""";"Mon titre ; un peu ""spécial""";"Khteur";"Reda";"0E2722";"2021-01-01 12:00:00";"21,00";"100%";"21,00";"Remboursement envoyé"'
    )


@pytest.mark.usefixtures("db_session")
def test_find_all_offerer_reimbursement_details():
    offerer = offers_factories.OffererFactory()
    venue1 = offers_factories.VenueFactory(managingOfferer=offerer)
    venue2 = offers_factories.VenueFactory(managingOfferer=offerer)
    educational_booking = booking_factories.UsedEducationalBookingFactory(stock__offer__venue=venue2)
    label = ("pass Culture Pro - remboursement 1ère quinzaine 07-2019",)
    payment_1 = payments_factories.PaymentFactory(booking__stock__offer__venue=venue1, transactionLabel=label)
    payment_2 = payments_factories.PaymentFactory(booking__stock__offer__venue=venue2, transactionLabel=label)
    payment_3 = payments_factories.PaymentFactory(booking=educational_booking, transactionLabel=label)
    payments_factories.PaymentStatusFactory(payment=payment_1, status=TransactionStatus.SENT)
    payments_factories.PaymentStatusFactory(payment=payment_2, status=TransactionStatus.SENT)
    payments_factories.PaymentStatusFactory(payment=payment_3, status=TransactionStatus.SENT)

    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

    assert len(reimbursement_details) == 3
