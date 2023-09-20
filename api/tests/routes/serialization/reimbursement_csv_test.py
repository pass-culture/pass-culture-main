from datetime import datetime
from datetime import timedelta
from itertools import count
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
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import _get_validation_period
from pcapi.routes.serialization.reimbursement_csv_serialize import _legacy_get_validation_period
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.string import u_nbsp


today = datetime.utcnow().date()
in_two_days = today + timedelta(days=2)
reimbursement_period = (today, in_two_days)


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
class ReimbursementDetailsTest:
    def test_reimbursement_details_as_csv_individual_booking(self) -> None:
        reimbursement_point = offerers_factories.VenueFactory(
            siret="siret-rp",
            name="Mon point de remboursement",
            address="1 rue du point de remboursement",
            city="Nantes",
            postalCode="44000",
        )
        # FIXME (dbaty, 2022-09-14): the BankInformation object should
        # automatically be created by the Venue factory when linking a
        # reimbursement point.
        finance_factories.BankInformationFactory(
            venue=reimbursement_point,
            iban="CF13QSDFGH456789",
        )
        payment = finance_factories.PaymentFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2022",
            booking__amount=10.5,
            booking__quantity=2,
            booking__dateUsed=datetime(2022, 6, 18),
            booking__stock__offer__venue__reimbursement_point=reimbursement_point,
            booking__priceCategoryLabel="Tarif unique",
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
        with freezegun.freeze_time(datetime(2023, 7, 1, 12, 0)):
            batch = finance_api.generate_cashflows_and_payment_files(datetime.utcnow())
            finance_api.generate_invoices(batch)
        cashflow = finance_models.Cashflow.query.one()
        invoice = finance_models.Invoice.query.one()

        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offerer.id,
            reimbursement_period,
        )
        row_number = count()
        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        assert row[next(row_number)] == "Validées et remboursables sur juin : 2nde quinzaine"
        assert row[next(row_number)] == invoice.date.date()
        assert row[next(row_number)] == invoice.reference
        assert row[next(row_number)] == cashflow.batch.label
        # reimbursement point
        assert row[next(row_number)] == "Mon point de remboursement"
        assert row[next(row_number)] == "1 rue du point de remboursement 44000 Nantes"
        assert row[next(row_number)] == reimbursement_point.siret
        assert row[next(row_number)] == reimbursement_point.iban
        # venue
        assert row[next(row_number)] == booking.venue.name
        assert row[next(row_number)] == "1 boulevard Poissonnière 75000 Paris"
        assert row[next(row_number)] == booking.venue.siret
        # offer and booking
        assert row[next(row_number)] == booking.stock.offer.name
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == booking.token
        assert row[next(row_number)] == booking.dateUsed
        # reimbursement
        assert row[next(row_number)] == booking.priceCategoryLabel
        assert row[next(row_number)] == "21,00"
        assert row[next(row_number)] == f"100{u_nbsp}%"
        assert row[next(row_number)] == "21,00"
        assert row[next(row_number)] == "offre grand public"

        # legacy payment data
        row_number = count()
        row = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert row[next(row_number)] == "Validées et remboursables sur juin : 2nde quinzaine"
        assert row[next(row_number)] == ""  # no invoice, no date
        assert row[next(row_number)] == ""  # no invoice, no label
        assert row[next(row_number)] == ""  # unknown transfer label
        # reimbursement point (not known, hence supposed to be the venue)
        assert row[next(row_number)] == booking.venue.name
        assert row[next(row_number)] == "1 boulevard Poissonnière 75000 Paris"
        assert row[next(row_number)] == booking.venue.siret
        assert row[next(row_number)] == payment.iban
        # venue
        assert row[next(row_number)] == booking.venue.name
        assert row[next(row_number)] == "1 boulevard Poissonnière 75000 Paris"
        assert row[next(row_number)] == booking.venue.siret
        # offer and booking
        assert row[next(row_number)] == booking.stock.offer.name
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == ""  # Unused for individual offer
        assert row[next(row_number)] == booking.token
        assert row[next(row_number)] == booking.dateUsed
        # reimbursement
        assert row[next(row_number)] == booking.priceCategoryLabel
        assert row[next(row_number)] == "21,00"
        assert row[next(row_number)] == f"{int(payment.reimbursementRate * 100)}%"
        assert row[next(row_number)] == "21,00"
        assert row[next(row_number)] == "offre grand public"

    def test_reimbursement_details_with_custom_rule_as_csv(self) -> None:
        # given
        custom_reimbursement_rule = finance_factories.CustomReimbursementRuleFactory(
            amount=None,
            rate=0.1234,
        )
        reimbursement_point = offerers_factories.VenueFactory()
        # FIXME (dbaty, 2022-09-14): the BankInformation object should
        # automatically be created by the Venue factory when linking a
        # reimbursement point.
        finance_factories.BankInformationFactory(venue=reimbursement_point)
        payment = finance_factories.PaymentWithCustomRuleFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2022",
            amount=2.71,
            customReimbursementRule=custom_reimbursement_rule,
            booking__amount=10.5,
            booking__quantity=2,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point,
        )
        finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
        finance_factories.PricingFactory(
            booking=payment.booking,
            amount=-271,
            standardRule="",
            customRule=custom_reimbursement_rule,
            status=finance_models.PricingStatus.VALIDATED,
        )
        batch = finance_api.generate_cashflows_and_payment_files(datetime.utcnow())
        finance_api.generate_invoices(batch)

        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offererId,
            reimbursement_period,
        )

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        assert row[21] == f"12,34{u_nbsp}%"

        # legacy payment data
        row = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert row[21] == ""


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
def test_generate_reimbursement_details_csv() -> None:
    # given
    payment = finance_factories.PaymentFactory(
        booking__stock__offer__name='Mon titre ; un peu "spécial"',
        booking__stock__offer__venue__name='Mon lieu ; un peu "spécial"',
        booking__stock__offer__venue__publicName="Un nom public pas très spécial",
        booking__stock__offer__venue__siret="siret-1234",
        booking__stock__offer__venue__reimbursement_point="self",
        booking__token="0E2722",
        booking__amount=10.5,
        booking__quantity=2,
        booking__dateUsed=datetime(2022, 1, 18, 12, 0),
        iban="CF13QSDFGH456789",
        transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2022",
    )
    venue = payment.booking.venue
    # FIXME (dbaty, 2022-09-14): the BankInformation object should
    # automatically be created by the Venue factory when linking a
    # reimbursement point.
    finance_factories.BankInformationFactory(
        venue=venue,
        iban="CF13QSDFGH456789",
    )
    finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
    offerer = payment.booking.offerer

    finance_factories.PricingFactory(
        booking=payment.booking,
        amount=-2100,
        standardRule="Remboursement total pour les offres physiques",
    )
    with freezegun.freeze_time(datetime(2023, 7, 1, 12, 0)):
        batch = finance_api.generate_cashflows_and_payment_files(datetime.utcnow())
        finance_api.generate_invoices(batch)
    # Invoice.date is generated by PostgreSQL, it cannot be controlled
    # by freezegun.
    invoice = finance_models.Invoice.query.one()
    invoice_date_as_str = invoice.date.date().isoformat()

    period = (datetime(2022, 7, 1, 4, 0).date(), datetime.utcnow().date())
    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, period)
    csv = generate_reimbursement_details_csv(reimbursement_details)

    # then
    rows = csv.splitlines()
    assert (
        rows[0]
        == '''"Réservations concernées par le remboursement";"Date du justificatif";"N° du justificatif";"N° de virement";"Point de remboursement";"Adresse du point de remboursement";"SIRET du point de remboursement";"IBAN";"Raison sociale du lieu";"Adresse du lieu";"SIRET du lieu";"Nom de l'offre";"N° de réservation (offre collective)";"Nom (offre collective)";"Prénom (offre collective)";"Nom de l'établissement (offre collective)";"Date de l'évènement (offre collective)";"Contremarque";"Date de validation de la réservation";"Intitulé du tarif";"Montant de la réservation";"Barème";"Montant remboursé";"Type d'offre"'''
    )
    assert (  # new pricing+cashflow data
        rows[1]
        == f'''"Validées et remboursables sur juin : 2nde quinzaine";"{invoice_date_as_str}";"F230000001";"VIR1";"Un nom public pas très spécial";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"CF13QSDFGH456789";"Mon lieu ; un peu ""spécial""";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"Mon titre ; un peu ""spécial""";"";"";"";"";"";"0E2722";"2022-01-18 12:00:00";"";"21,00";"100{u_nbsp}%";"21,00";"offre grand public"'''
    )
    assert (  # legacy payment data
        rows[2]
        == '''"Validées et remboursables sur juin : 2nde quinzaine";"";"";"";"Un nom public pas très spécial";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"CF13QSDFGH456789";"Mon lieu ; un peu ""spécial""";"1 boulevard Poissonnière 75000 Paris";"siret-1234";"Mon titre ; un peu ""spécial""";"";"";"";"";"";"0E2722";"2022-01-18 12:00:00";"";"21,00";"100%";"21,00";"offre grand public"'''
    )


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
def test_find_all_offerer_reimbursement_details() -> None:
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        reimbursement_point="self",
    )
    venue2 = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        reimbursement_point="self",
    )
    # FIXME (dbaty, 2022-09-14): the BankInformation object should
    # automatically be created by the Venue factory when linking a
    # reimbursement point.
    finance_factories.BankInformationFactory(venue=venue1)
    finance_factories.BankInformationFactory(venue=venue2)
    booking1 = bookings_factories.UsedBookingFactory(stock__offer__venue=venue1)
    booking2 = bookings_factories.UsedBookingFactory(stock__offer__venue=venue2)
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
    finance_factories.CollectivePricingFactory(collectiveBooking=collective_booking3)
    batch = finance_api.generate_cashflows_and_payment_files(datetime.utcnow())
    finance_api.generate_invoices(batch)

    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

    assert len(reimbursement_details) == 6


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.finance.api._store_invoice_pdf", lambda **kwargs: "make it quick")
class CollectiveReimbursementDetailsTest:
    def test_find_all_offerer_reimbursement_details_on_collective(self) -> None:
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            reimbursement_point="self",
        )
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            name="Le lieu unique",
            address="48 boulevard des turlupins",
            siret="12345678912345",
            pricing_point="self",
            reimbursement_point="self",
        )
        # FIXME (dbaty, 2022-09-14): the BankInformation object should
        # automatically be created by the Venue factory when linking a
        # reimbursement point.
        finance_factories.BankInformationFactory(venue=venue1)
        finance_factories.BankInformationFactory(venue=venue2)
        booking1 = bookings_factories.UsedBookingFactory(dateUsed=datetime(2022, 6, 18), stock__offer__venue=venue1)
        booking2 = bookings_factories.UsedBookingFactory(
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

        with freezegun.freeze_time(datetime(2023, 7, 1, 12, 0)):
            batch = finance_api.generate_cashflows_and_payment_files(datetime.utcnow())
            finance_api.generate_invoices(batch)
        cashflow = finance_models.Cashflow.query.filter_by(reimbursementPoint=venue2).one()
        invoice = finance_models.Invoice.query.filter_by(reimbursementPoint=venue2).one()

        reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

        assert len(reimbursement_details) == 3

        collective_reimbursement_detail = reimbursement_details[2]

        assert collective_reimbursement_detail.as_csv_row() == [
            "Validées et remboursables sur juin : 2nde quinzaine",
            invoice.date.date(),
            invoice.reference,
            cashflow.batch.label,
            "Le lieu unique",
            "48 boulevard des turlupins 75000 Paris",
            booking3.venue.siret,
            venue2.iban,
            booking3.venue.name,
            "48 boulevard des turlupins 75000 Paris",
            booking3.venue.siret,
            booking3.collectiveStock.collectiveOffer.name,
            booking3.id,
            "Khteur",
            "Reda",
            booking3.educationalInstitution.name,
            utc_datetime_to_department_timezone(booking3.collectiveStock.beginningDatetime, "75").strftime(
                "%d/%m/%Y %H:%M"
            ),
            None,
            booking3.dateUsed,
            None,
            "100,00",
            f"100{u_nbsp}%",
            "100,00",
            "offre collective",
        ]

    def test_reimbursement_details_as_csv_collective_booking(self) -> None:
        reimbursement_point = offerers_factories.VenueFactory(
            siret="siret-rp",
            name="Mon point de remboursement",
            address="1 rue du point de remboursement",
            city="Nantes",
            postalCode="44000",
        )
        finance_factories.BankInformationFactory(
            venue=reimbursement_point,
            iban="CF13QSDFGH456789",
        )
        venue = offerers_factories.VenueFactory(reimbursement_point=reimbursement_point)
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
        )
        with freezegun.freeze_time(datetime(2023, 7, 1, 12, 0)):
            batch = finance_api.generate_cashflows_and_payment_files(datetime.utcnow())
            finance_api.generate_invoices(batch)
        cashflow = finance_models.Cashflow.query.one()
        invoice = finance_models.Invoice.query.one()

        payments_info = finance_repository.find_all_offerer_payments(
            booking.offerer.id,
            reimbursement_period,
        )

        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        row_number = count()
        assert row[next(row_number)] == "Validées et remboursables sur juin : 2nde quinzaine"
        assert row[next(row_number)] == invoice.date.date()
        assert row[next(row_number)] == invoice.reference
        assert row[next(row_number)] == cashflow.batch.label
        # reimbursement point
        assert row[next(row_number)] == "Mon point de remboursement"
        assert row[next(row_number)] == "1 rue du point de remboursement 44000 Nantes"
        assert row[next(row_number)] == "siret-rp"
        assert row[next(row_number)] == reimbursement_point.iban
        # venue
        assert row[next(row_number)] == booking.venue.name
        assert row[next(row_number)] == "1 boulevard Poissonnière 75000 Paris"
        assert row[next(row_number)] == booking.venue.siret
        # offer and booking
        assert row[next(row_number)] == booking.collectiveStock.collectiveOffer.name
        assert row[next(row_number)] == booking.id
        assert row[next(row_number)] == booking.educationalRedactor.lastName
        assert row[next(row_number)] == booking.educationalRedactor.firstName
        assert row[next(row_number)] == booking.educationalInstitution.name
        assert row[next(row_number)] == utc_datetime_to_department_timezone(
            booking.collectiveStock.beginningDatetime, "75"
        ).strftime("%d/%m/%Y %H:%M")
        assert row[next(row_number)] is None
        assert row[next(row_number)] == booking.dateUsed
        # reimbursement
        assert row[next(row_number)] is None
        assert row[next(row_number)] == "21,00"
        assert row[next(row_number)] == f"100{u_nbsp}%"
        assert row[next(row_number)] == "21,00"
        assert row[next(row_number)] == "offre collective"


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
