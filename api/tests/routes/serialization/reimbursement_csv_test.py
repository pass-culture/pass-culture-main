from datetime import datetime
from datetime import timedelta
from unittest import mock

import freezegun
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational import factories as educational_factories
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import _get_validation_period
from pcapi.routes.serialization.reimbursement_csv_serialize import _legacy_get_validation_period
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.utils.date import utc_datetime_to_department_timezone


today = datetime.utcnow().date()
in_two_days = today + timedelta(days=2)
reimbursement_period = (today, in_two_days)


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
class ReimbursementDetailsTest:
    def test_reimbursement_details_as_csv_individual_booking(self) -> None:
        business_unit = offerers_factories.VenueFactory(
            siret="siret bu",
            name="Ma petite business unit",
            address="1 rue de la business unit",
            city="Nantes",
            postalCode="44000",
            businessUnit__bankAccount__iban="CF13QSDFGH456789",
        ).businessUnit
        payment = finance_factories.PaymentFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2022",
            booking__amount=10.5,
            booking__quantity=2,
            booking__dateUsed=datetime(2022, 6, 18),
            booking__stock__offer__venue__businessUnit=business_unit,
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.SENT,
        )
        booking = payment.booking
        finance_factories.PricingFactory(
            booking=booking,
            amount=-2100,
            standardRule="Remboursement total pour les offres physiques",
            status=finance_models.PricingStatus.VALIDATED,
        )
        with freezegun.freeze_time(datetime(2022, 7, 1, 12, 0)):
            finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
            finance_api.generate_invoices()
        cashflow = finance_models.Cashflow.query.one()
        invoice = finance_models.Invoice.query.one()

        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offerer.id,
            reimbursement_period,
        )

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        assert row[0] == "Validées et remboursables sur juin : 2nde quinzaine"
        assert row[1] == invoice.date
        assert row[2] == invoice.reference
        assert row[3] == cashflow.batch.label
        # business unit
        assert row[4] == "Ma petite business unit"
        assert row[5] == "1 rue de la business unit 44000 Nantes"
        assert row[6] == "siret bu"
        assert row[7] == business_unit.bankAccount.iban
        # venue
        assert row[8] == booking.venue.name
        assert row[9] == "1 boulevard Poissonnière 75000 Paris"
        assert row[10] == booking.venue.siret
        # offer and booking
        assert row[11] == booking.stock.offer.name
        assert row[12] == ""  # Unused for individual offer
        assert row[13] == ""  # Unused for individual offer
        assert row[14] == ""  # Unused for individual offer
        assert row[15] == ""  # Unused for individual offer
        assert row[16] == booking.token
        assert row[17] == booking.dateUsed
        # reimbursement
        assert row[18] == "21,00"
        assert row[19] == "100 %"
        assert row[20] == "21,00"
        assert row[21] == "offre grand public"

        # legacy payment data
        row = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert row[0] == "Validées et remboursables sur juin : 2nde quinzaine"
        assert row[1] == ""  # no invoice, no date
        assert row[2] == ""  # no invoice, no label
        assert row[3] == ""  # unknown transfer label
        # business unit (not known, hence supposed to be the venue)
        assert row[4] == booking.venue.name
        assert row[5] == "1 boulevard Poissonnière 75000 Paris"
        assert row[6] == booking.venue.siret
        assert row[7] == payment.iban
        # venue
        assert row[8] == booking.venue.name
        assert row[9] == "1 boulevard Poissonnière 75000 Paris"
        assert row[10] == booking.venue.siret
        # offer and booking
        assert row[11] == booking.stock.offer.name
        assert row[12] == ""  # Unused for individual offer
        assert row[13] == ""  # Unused for individual offer
        assert row[14] == ""  # Unused for individual offer
        assert row[15] == ""  # Unused for individual offer
        assert row[16] == booking.token
        assert row[17] == booking.dateUsed
        # reimbursement
        assert row[18] == "21,00"
        assert row[19] == f"{int(payment.reimbursementRate * 100)}%"
        assert row[20] == "21,00"
        assert row[21] == "offre grand public"

    def test_reimbursement_details_with_custom_rule_as_csv(self) -> None:
        # given
        custom_reimbursement_rule = payments_factories.CustomReimbursementRuleFactory(
            amount=None,
            rate=0.1234,
        )
        payment = finance_factories.PaymentWithCustomRuleFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2022",
            amount=2.71,
            customReimbursementRule=custom_reimbursement_rule,
            booking__amount=10.5,
            booking__quantity=2,
            booking__stock__offer__venue__businessUnit__bankAccount__iban="CF13QSDFGH456789",
        )
        finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
        finance_factories.PricingFactory(
            booking=payment.booking,
            amount=-271,
            standardRule="",
            customRule=custom_reimbursement_rule,
            status=finance_models.PricingStatus.VALIDATED,
        )
        finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
        finance_api.generate_invoices()

        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offererId,
            reimbursement_period,
        )

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        assert row[19] == "12,34 %"

        # legacy payment data
        row = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert row[19] == ""


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
def test_generate_reimbursement_details_csv() -> None:
    # given
    payment = finance_factories.PaymentFactory(
        booking__stock__offer__name='Mon titre ; un peu "spécial"',
        booking__stock__offer__venue__name='Mon lieu ; un peu "spécial"',
        booking__stock__offer__venue__siret="siret-1234",
        booking__stock__offer__venue__businessUnit__bankAccount__iban="CF13QSDFGH456789",
        booking__token="0E2722",
        booking__amount=10.5,
        booking__quantity=2,
        booking__dateUsed=datetime(2022, 1, 18, 12, 0),
        iban="CF13QSDFGH456789",
        transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2022",
    )
    finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
    offerer = payment.booking.offerer

    finance_factories.PricingFactory(
        booking=payment.booking,
        amount=-2100,
        standardRule="Remboursement total pour les offres physiques",
    )
    with freezegun.freeze_time(datetime(2022, 7, 1, 12, 0)):
        finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
        finance_api.generate_invoices()
    # Invoice.date is generated by PostgreSQL, it cannot be controlled
    # by freezegun.
    invoice = finance_models.Invoice.query.one()
    invoice_date_as_str = invoice.date.isoformat().replace("T", " ")

    period = (datetime(2022, 7, 1, 4, 0).date(), datetime.utcnow().date())
    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, period)
    csv = generate_reimbursement_details_csv(reimbursement_details)

    # then
    rows = csv.splitlines()
    assert (
        rows[0]
        == '''"Réservations concernées par le remboursement";"Date du justificatif";"N° du justificatif";"N° de virement";"Point de remboursement";"Adresse du point de remboursement";"SIRET du point de remboursement";"IBAN";"Raison sociale du lieu";"Adresse du lieu";"SIRET du lieu";"Nom de l'offre";"Nom (offre collective)";"Prénom (offre collective)";"Nom de l'établissement (offre collective)";"Date de l'évènement (offre collective)";"Contremarque";"Date de validation de la réservation";"Montant de la réservation";"Barème";"Montant remboursé";"Type d'offre"'''
    )
    assert (  # new pricing+cashflow data
        rows[1]
        == f'''"Validées et remboursables sur juin : 2nde quinzaine";"{invoice_date_as_str}";"F220000001";"VIR1";"Mon lieu ; un peu ""spécial""";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"CF13QSDFGH456789";"Mon lieu ; un peu ""spécial""";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"Mon titre ; un peu ""spécial""";"";"";"";"";"0E2722";"2022-01-18 12:00:00";"21,00";"100 %";"21,00";"offre grand public"'''
    )
    assert (  # legacy payment data
        rows[2]
        == '''"Validées et remboursables sur juin : 2nde quinzaine";"";"";"";"Mon lieu ; un peu ""spécial""";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"CF13QSDFGH456789";"Mon lieu ; un peu ""spécial""";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"Mon titre ; un peu ""spécial""";"";"";"";"";"0E2722";"2022-01-18 12:00:00";"21,00";"100%";"21,00";"offre grand public"'''
    )


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
def test_find_all_offerer_reimbursement_details() -> None:
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
    booking1 = bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue1)
    booking2 = bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue2)
    collective_booking3 = educational_factories.UsedCollectiveBookingFactory(
        collectiveStock__beginningDatetime=datetime.utcnow(),
        collectiveStock__collectiveOffer__venue=venue2,
    )
    label = ("pass Culture Pro - remboursement 1ère quinzaine 07-2019",)
    payment_1 = finance_factories.PaymentFactory(booking=booking1, transactionLabel=label)
    payment_2 = finance_factories.PaymentFactory(booking=booking2, transactionLabel=label)
    payment_3 = finance_factories.PaymentFactory(collectiveBooking=collective_booking3, transactionLabel=label)
    finance_factories.PaymentStatusFactory(payment=payment_1, status=finance_models.TransactionStatus.SENT)
    finance_factories.PaymentStatusFactory(payment=payment_2, status=finance_models.TransactionStatus.SENT)
    finance_factories.PaymentStatusFactory(payment=payment_3, status=finance_models.TransactionStatus.SENT)

    for booking in (booking1, booking2):
        finance_factories.PricingFactory(booking=booking)
    finance_factories.PricingFactory(collectiveBooking=collective_booking3)
    finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
    finance_api.generate_invoices()

    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

    assert len(reimbursement_details) == 6


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
class CollectiveReimbursementDetailsTest:
    def test_find_all_offerer_reimbursement_details_on_collective(self) -> None:
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            name="Le lieu unique",
            address="48 boulevard des turlupins",
            siret="12345678912345",
            businessUnit__bankAccount__iban="CF13QSDFGH456789",
        )
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            dateUsed=datetime(2022, 6, 18), stock__offer__venue=venue1
        )
        booking2 = bookings_factories.UsedIndividualBookingFactory(
            dateUsed=datetime(2022, 6, 18),
            stock__offer__venue=venue2,
        )
        booking3 = educational_factories.UsedCollectiveBookingFactory(
            dateUsed=datetime(2022, 6, 18),
            collectiveStock__beginningDatetime=datetime(2022, 6, 18),
            collectiveStock__collectiveOffer__venue=venue2,
            collectiveStock__collectiveOffer__name="Un super nom d'offre",
        )
        for booking in (booking1, booking2):
            finance_factories.PricingFactory(booking=booking)
        finance_factories.CollectivePricingFactory(collectiveBooking=booking3)

        with freezegun.freeze_time(datetime(2022, 7, 1, 12, 0)):
            finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
            finance_api.generate_invoices()
        cashflow = finance_models.Cashflow.query.filter_by(businessUnit=venue2.businessUnit).one()
        invoice = finance_models.Invoice.query.filter_by(businessUnit=venue2.businessUnit).one()

        reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

        assert len(reimbursement_details) == 3

        collective_reimbursement_detail = reimbursement_details[2]

        assert collective_reimbursement_detail.as_csv_row() == [
            "Validées et remboursables sur juin : 2nde quinzaine",
            invoice.date,
            invoice.reference,
            cashflow.batch.label,
            "Le lieu unique",
            "48 boulevard des turlupins 75000 Paris",
            booking3.venue.siret,
            venue2.businessUnit.bankAccount.iban,
            booking3.venue.name,
            "48 boulevard des turlupins 75000 Paris",
            booking3.venue.siret,
            booking3.collectiveStock.collectiveOffer.name,
            "Khteur",
            "Reda",
            booking3.educationalInstitution.name,
            utc_datetime_to_department_timezone(booking3.collectiveStock.beginningDatetime, "75").strftime(
                "%d/%m/%Y %H:%M"
            ),
            None,
            booking3.dateUsed,
            "100,00",
            "100 %",
            "100,00",
            "offre collective",
        ]

    def test_reimbursement_details_as_csv_collective_booking(self) -> None:
        business_unit = offerers_factories.VenueFactory(
            siret="siret bu",
            name="Ma petite business unit",
            address="1 rue de la business unit",
            city="Nantes",
            postalCode="44000",
            businessUnit__bankAccount__iban="CF13QSDFGH456789",
        ).businessUnit
        venue = offerers_factories.VenueFactory(businessUnit=business_unit)
        booking = educational_factories.UsedCollectiveBookingFactory(
            dateUsed=datetime(2022, 6, 18),
            collectiveStock__price=21,
            collectiveStock__beginningDatetime=datetime(2022, 6, 18),
            collectiveStock__collectiveOffer__venue=venue,
        )
        finance_factories.CollectivePricingFactory(
            collectiveBooking=booking,
            standardRule="Remboursement total pour les offres physiques",
            status=finance_models.PricingStatus.VALIDATED,
            businessUnit=venue.businessUnit,
        )
        with freezegun.freeze_time(datetime(2022, 7, 1, 12, 0)):
            finance_api.generate_cashflows_and_payment_files(cutoff=datetime.utcnow())
            finance_api.generate_invoices()
        cashflow = finance_models.Cashflow.query.one()
        invoice = finance_models.Invoice.query.one()

        payments_info = finance_repository.find_all_offerer_payments(
            booking.offerer.id,
            reimbursement_period,
        )

        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        assert row[0] == "Validées et remboursables sur juin : 2nde quinzaine"
        assert row[1] == invoice.date
        assert row[2] == invoice.reference
        assert row[3] == cashflow.batch.label
        # business unit
        assert row[4] == "Ma petite business unit"
        assert row[5] == "1 rue de la business unit 44000 Nantes"
        assert row[6] == "siret bu"
        assert row[7] == business_unit.bankAccount.iban
        # venue
        assert row[8] == booking.venue.name
        assert row[9] == "1 boulevard Poissonnière 75000 Paris"
        assert row[10] == booking.venue.siret
        # offer and booking
        assert row[11] == booking.collectiveStock.collectiveOffer.name
        assert row[12] == booking.educationalRedactor.lastName
        assert row[13] == booking.educationalRedactor.firstName
        assert row[14] == booking.educationalInstitution.name
        assert row[15] == utc_datetime_to_department_timezone(booking.collectiveStock.beginningDatetime, "75").strftime(
            "%d/%m/%Y %H:%M"
        )
        assert row[16] is None
        assert row[17] == booking.dateUsed
        # reimbursement
        assert row[18] == "21,00"
        assert row[19] == "100 %"
        assert row[20] == "21,00"
        assert row[21] == "offre collective"


def test_get_validation_period() -> None:
    assert (
        _get_validation_period(cutoff=datetime(2022, 1, 16)) == "Validées et remboursables sur janvier : 1ère quinzaine"
    )
    assert (
        _get_validation_period(cutoff=datetime(2022, 2, 1)) == "Validées et remboursables sur janvier : 2nde quinzaine"
    )


def test_legacy_get_validation_period() -> None:
    assert (
        _legacy_get_validation_period("pass Culture Pro - remboursement 1ère quinzaine 06-2019")
        == "Validées et remboursables sur mai : 2nde quinzaine"
    )
    assert (
        _legacy_get_validation_period("pass Culture Pro - remboursement 2ème quinzaine 06-2019")
        == "Validées et remboursables sur juin : 1ère quinzaine"
    )
