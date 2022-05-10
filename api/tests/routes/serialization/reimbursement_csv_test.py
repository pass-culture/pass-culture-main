from datetime import date
from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational import factories as educational_factories
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import override_features
from pcapi.models import db
from pcapi.repository import repository
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv


today = datetime.utcnow().date()
in_two_days = today + timedelta(days=2)
reimbursement_period = (today, in_two_days)


@pytest.mark.usefixtures("db_session")
class ReimbursementDetailsTest:
    def test_reimbursement_details_as_csv_individual_booking(self):
        payment = finance_factories.PaymentFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            booking__amount=10.5,
            booking__quantity=2,
            booking__stock__offer__venue__businessUnit__bankAccount__iban="CF13QSDFGH456789",
        )
        finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
        finance_factories.PricingFactory(
            booking=payment.booking,
            amount=-2100,
            standardRule="Remboursement total pour les offres physiques",
            status=finance_models.PricingStatus.VALIDATED,
        )
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
        )
        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offerer.id,
            reimbursement_period,
        )

        # legacy payment data
        raw_csv = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert raw_csv[0] == "2019"
        assert raw_csv[1] == "juillet : remboursement 1ère quinzaine"
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
        assert raw_csv[16] == "offre grand public"

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        # The first 2 cells are tested in a separate test below.
        assert row[2] == payment.booking.venue.name
        assert row[3] == payment.booking.venue.siret
        assert row[4] == payment.booking.venue.address
        assert row[5] == payment.iban
        assert row[6] == payment.booking.venue.name
        assert row[7] == payment.booking.stock.offer.name
        assert row[8] == "Doux"
        assert row[9] == "Jeanne"
        assert row[10] == payment.booking.token
        assert row[11] == payment.booking.dateUsed
        assert row[12] == "21,00"
        assert row[13] == f"{int(payment.reimbursementRate * 100)} %"
        assert row[14] == "21,00"
        assert row[15] == "Remboursement envoyé"
        assert row[16] == "offre grand public"

    def test_reimbursement_details_as_csv_educational_booking(self):
        # given
        booking = bookings_factories.UsedEducationalBookingFactory(
            amount=10.5,
            quantity=2,
            stock__beginningDatetime=datetime.utcnow(),
            stock__offer__venue__businessUnit__bankAccount__iban="CF13QSDFGH456789",
        )
        payment = finance_factories.PaymentFactory(
            booking=booking,
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
        finance_factories.PricingFactory(
            booking=payment.booking,
            amount=-2100,
            standardRule="Remboursement total pour les offres physiques",
            status=finance_models.PricingStatus.VALIDATED,
        )
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
            synchronize_session=False,
        )
        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offerer.id,
            reimbursement_period,
        )

        # legacy payment data
        raw_csv = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert raw_csv[0] == "2019"
        assert raw_csv[1] == "juillet : remboursement 1ère quinzaine"
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
        assert raw_csv[16] == "offre collective"

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        # The first 2 cells are tested in a separate test below.
        assert row[2] == payment.booking.venue.name
        assert row[3] == payment.booking.venue.siret
        assert row[4] == payment.booking.venue.address
        assert row[5] == payment.iban
        assert row[6] == payment.booking.venue.name
        assert row[7] == payment.booking.stock.offer.name
        assert row[8] == payment.booking.educationalBooking.educationalRedactor.lastName
        assert row[9] == payment.booking.educationalBooking.educationalRedactor.firstName
        assert row[10] == payment.booking.token
        assert row[11] == payment.booking.dateUsed
        assert row[12] == "21,00"
        assert row[13] == f"{int(payment.reimbursementRate * 100)} %"
        assert row[14] == "21,00"
        assert row[15] == "Remboursement envoyé"
        assert row[16] == "offre collective"

    def test_reimbursement_details_with_custom_rule_as_csv(self):
        # given
        custom_reimbursement_rule = payments_factories.CustomReimbursementRuleFactory(
            amount=None,
            rate=0.1234,
        )
        payment = finance_factories.PaymentWithCustomRuleFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
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
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
        )
        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offererId,
            reimbursement_period,
        )

        # legacy payment data
        row = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert row[13] == ""

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        assert row[13] == "12,34 %"

    def test_reimbursement_details_date_columns(self):
        # Date columns of ReimbursementDetails are populated from
        # `Cashflow.creationDate` which is generated by the
        # database. They cannot be controlled with freezetime in the
        # tests above.
        booking = bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue__businessUnit__bankAccount__iban="CF13QSDFGH456789",
        )
        finance_factories.PricingFactory(
            booking=booking,
            status=finance_models.PricingStatus.VALIDATED,
        )
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
            synchronize_session=False,
        )
        cashflow = finance_models.Cashflow.query.one()

        cashflow.creationDate = datetime(2021, 1, 1, 4, 0)
        repository.save(cashflow)
        period = (cashflow.creationDate.date(), date.today() + timedelta(days=1))
        payments = finance_repository.find_all_offerer_payments(booking.offererId, period)
        row = ReimbursementDetails(payments[0]).as_csv_row()
        assert row[0] == 2021
        assert row[1] == "janvier : remboursement 1ère quinzaine"

        cashflow.creationDate = datetime(2021, 2, 16, 4, 0)
        repository.save(cashflow)
        payments = finance_repository.find_all_offerer_payments(booking.offererId, period)
        row = ReimbursementDetails(payments[0]).as_csv_row()
        assert row[0] == 2021
        assert row[1] == "février : remboursement 2nde quinzaine"


@pytest.mark.usefixtures("db_session")
def test_generate_reimbursement_details_csv():
    # given
    payment = finance_factories.PaymentFactory(
        booking__stock__offer__name='Mon titre ; un peu "spécial"',
        booking__stock__offer__isEducational=False,
        booking__stock__offer__venue__name='Mon lieu ; un peu "spécial"',
        booking__stock__offer__venue__siret="siret-1234",
        booking__stock__offer__venue__businessUnit__bankAccount__iban="CF13QSDFGH456789",
        booking__token="0E2722",
        booking__amount=10.5,
        booking__quantity=2,
        booking__dateUsed=datetime(2021, 1, 1, 12, 0),
        iban="CF13QSDFGH456789",
        transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
    )
    finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
    offerer = payment.booking.offerer

    finance_factories.PricingFactory(
        booking=payment.booking,
        amount=-2100,
        standardRule="Remboursement total pour les offres physiques",
        status=finance_models.PricingStatus.VALIDATED,
    )
    finance_api.generate_cashflows(cutoff=datetime.utcnow())
    finance_models.Pricing.query.update(
        {"status": finance_models.PricingStatus.INVOICED},
        synchronize_session=False,
    )
    finance_models.Cashflow.query.update({"creationDate": datetime(2019, 7, 1, 4, 0)}, synchronize_session=False)

    period = (datetime(2019, 7, 1, 4, 0).date(), datetime.utcnow().date())
    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, period)
    csv = generate_reimbursement_details_csv(reimbursement_details)

    # then
    rows = csv.splitlines()
    assert (
        rows[0]
        == '"Année";"Virement";"Créditeur";"SIRET créditeur";"Adresse créditeur";"IBAN";"Raison sociale du lieu";"Nom de l\'offre";"Nom utilisateur";"Prénom utilisateur";"Contremarque";"Date de validation de la réservation";"Montant de la réservation";"Barème";"Montant remboursé";"Statut du remboursement";"Type d\'offre"'
    )
    assert (  # legacy payment data
        rows[2]
        == '"2019";"juillet : remboursement 1ère quinzaine";"Mon lieu ; un peu ""spécial""";"siret-1234";"1 boulevard Poissonnière";"CF13QSDFGH456789";"Mon lieu ; un peu ""spécial""";"Mon titre ; un peu ""spécial""";"Doux";"Jeanne";"0E2722";"2021-01-01 12:00:00";"21,00";"100%";"21,00";"Remboursement envoyé";"offre grand public"'
    )
    assert (  # new pricing+cashflow data
        rows[1]
        == '2019;"juillet : remboursement 1ère quinzaine";"Mon lieu ; un peu ""spécial""";"siret-1234";"1 boulevard Poissonnière";"CF13QSDFGH456789";"Mon lieu ; un peu ""spécial""";"Mon titre ; un peu ""spécial""";"Doux";"Jeanne";"0E2722";"2021-01-01 12:00:00";"21,00";"100 %";"21,00";"Remboursement envoyé";"offre grand public"'
    )


@pytest.mark.usefixtures("db_session")
def test_find_all_offerer_reimbursement_details():
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer)
    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
    booking1 = bookings_factories.UsedBookingFactory(stock__offer__venue=venue1)
    booking2 = bookings_factories.UsedBookingFactory(stock__offer__venue=venue2)
    booking3 = bookings_factories.UsedEducationalBookingFactory(
        stock__beginningDatetime=datetime.utcnow(),
        stock__offer__venue=venue2,
    )
    label = ("pass Culture Pro - remboursement 1ère quinzaine 07-2019",)
    payment_1 = finance_factories.PaymentFactory(booking=booking1, transactionLabel=label)
    payment_2 = finance_factories.PaymentFactory(booking=booking2, transactionLabel=label)
    payment_3 = finance_factories.PaymentFactory(booking=booking3, transactionLabel=label)
    finance_factories.PaymentStatusFactory(payment=payment_1, status=finance_models.TransactionStatus.SENT)
    finance_factories.PaymentStatusFactory(payment=payment_2, status=finance_models.TransactionStatus.SENT)
    finance_factories.PaymentStatusFactory(payment=payment_3, status=finance_models.TransactionStatus.SENT)

    for booking in (booking1, booking2, booking3):
        finance_factories.PricingFactory(
            booking=booking,
            status=finance_models.PricingStatus.VALIDATED,
        )
    finance_api.generate_cashflows(cutoff=datetime.utcnow())
    finance_models.Pricing.query.update(
        {"status": finance_models.PricingStatus.INVOICED},
        synchronize_session=False,
    )

    reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

    assert len(reimbursement_details) == 6


@pytest.mark.usefixtures("db_session")
class CollectiveReimbursementDetailsTest:
    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_find_all_offerer_reimbursement_details_on_collective(self):
        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            name="Le lieu unique",
            address="48 boulevard des turlupins",
            siret="12345678912345",
            businessUnit__bankAccount__iban="CF13QSDFGH456789",
        )
        booking1 = bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue1)
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue2)
        booking3 = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__beginningDatetime=datetime.utcnow(),
            collectiveStock__collectiveOffer__venue=venue2,
            collectiveStock__collectiveOffer__name="Un super nom d'offre",
        )
        for booking in (booking1, booking2):
            finance_factories.PricingFactory(
                booking=booking,
                status=finance_models.PricingStatus.VALIDATED,
            )

        finance_factories.CollectivePricingFactory(
            collectiveBooking=booking3,
            status=finance_models.PricingStatus.VALIDATED,
            businessUnit=venue2.businessUnit,
        )
        finance_api.generate_cashflows(cutoff=datetime.utcnow())

        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
            synchronize_session=False,
        )

        reimbursement_details = find_all_offerer_reimbursement_details(offerer.id, reimbursement_period)

        assert len(reimbursement_details) == 3

        collective_reimbursement_detail = reimbursement_details[2]
        assert collective_reimbursement_detail.as_csv_row() == [
            collective_reimbursement_detail.year,  # This complex to test behavior is tested elsewhere
            collective_reimbursement_detail.transfer_name,  # This complex to test behavior is tested elsewhere
            "Le lieu unique",
            "12345678912345",
            "48 boulevard des turlupins",
            "CF13QSDFGH456789",
            "Le lieu unique",
            "Un super nom d'offre",
            "Khteur",
            "Reda",
            None,
            booking3.dateUsed,
            "100,00",
            "100\xa0%",
            "100,00",
            "Remboursement envoyé",
            "offre collective",
        ]

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_reimbursement_details_as_csv_individual_booking(self):
        venue = offerers_factories.VenueFactory(businessUnit__bankAccount__iban="CF13QSDFGH456789")
        payment = finance_factories.PaymentFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            booking__amount=10.5,
            booking__quantity=2,
            booking__stock__offer__venue=venue,
        )
        finance_factories.PaymentStatusFactory(payment=payment, status=finance_models.TransactionStatus.SENT)
        finance_factories.PricingFactory(
            booking=payment.booking,
            amount=-2100,
            standardRule="Remboursement total pour les offres physiques",
            status=finance_models.PricingStatus.VALIDATED,
            businessUnit=venue.businessUnit,
        )
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
        )
        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offerer.id,
            reimbursement_period,
        )

        # legacy payment data
        raw_csv = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert raw_csv[0] == "2019"
        assert raw_csv[1] == "juillet : remboursement 1ère quinzaine"
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
        assert raw_csv[16] == "offre grand public"

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        # The first 2 cells are tested in a separate test below.
        assert row[2] == payment.booking.venue.name
        assert row[3] == payment.booking.venue.siret
        assert row[4] == payment.booking.venue.address
        assert row[5] == payment.iban
        assert row[6] == payment.booking.venue.name
        assert row[7] == payment.booking.stock.offer.name
        assert row[8] == "Doux"
        assert row[9] == "Jeanne"
        assert row[10] == payment.booking.token
        assert row[11] == payment.booking.dateUsed
        assert row[12] == "21,00"
        assert row[13] == f"{int(payment.reimbursementRate * 100)} %"
        assert row[14] == "21,00"
        assert row[15] == "Remboursement envoyé"
        assert row[16] == "offre grand public"

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_reimbursement_details_as_csv_collective_booking(self):
        # given
        venue = offerers_factories.VenueFactory(businessUnit__bankAccount__iban="CF13QSDFGH456789")
        booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__price=21,
            collectiveStock__beginningDatetime=datetime.utcnow(),
            collectiveStock__collectiveOffer__venue=venue,
        )
        finance_factories.CollectivePricingFactory(
            collectiveBooking=booking,
            standardRule="Remboursement total pour les offres physiques",
            status=finance_models.PricingStatus.VALIDATED,
            businessUnit=venue.businessUnit,
        )
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
            synchronize_session=False,
        )
        payments_info = finance_repository.find_all_offerer_payments(
            booking.offerer.id,
            reimbursement_period,
        )

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        # The first 2 cells are tested in a separate test below.
        assert row[2] == venue.name
        assert row[3] == venue.siret
        assert row[4] == venue.address
        assert row[5] == "CF13QSDFGH456789"
        assert row[6] == venue.name
        assert row[7] == booking.collectiveStock.collectiveOffer.name
        assert row[8] == booking.educationalRedactor.lastName
        assert row[9] == booking.educationalRedactor.firstName
        assert row[10] == None
        assert row[11] == booking.dateUsed
        assert row[12] == "21,00"
        assert row[13] == "100\xa0%"
        assert row[14] == "21,00"
        assert row[15] == "Remboursement envoyé"
        assert row[16] == "offre collective"

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_reimbursement_details_with_custom_rule_as_csv(self):
        # given
        custom_reimbursement_rule = payments_factories.CustomReimbursementRuleFactory(
            amount=None,
            rate=0.1234,
        )
        payment = finance_factories.PaymentWithCustomRuleFactory(
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
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
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
        )
        payments_info = finance_repository.find_all_offerer_payments(
            payment.booking.offererId,
            reimbursement_period,
        )

        # legacy payment data
        row = ReimbursementDetails(payments_info[1]).as_csv_row()
        assert row[13] == ""

        # new pricing+cashflow data
        row = ReimbursementDetails(payments_info[0]).as_csv_row()
        assert row[13] == "12,34 %"

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_reimbursement_details_date_columns(self):
        # Date columns of ReimbursementDetails are populated from
        # `Cashflow.creationDate` which is generated by the
        # database. They cannot be controlled with freezetime in the
        # tests above.
        venue = offerers_factories.VenueFactory(businessUnit__bankAccount__iban="CF13QSDFGH456789")
        booking = bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
        )
        collective_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__beginningDatetime=datetime.utcnow(),
        )
        finance_factories.PricingFactory(
            booking=booking,
            status=finance_models.PricingStatus.VALIDATED,
        )
        finance_factories.CollectivePricingFactory(
            collectiveBooking=collective_booking,
            status=finance_models.PricingStatus.VALIDATED,
            businessUnit=venue.businessUnit,
        )
        finance_api.generate_cashflows(cutoff=datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
            synchronize_session=False,
        )
        finance_models.Cashflow.query.update(
            {finance_models.Cashflow.creationDate: datetime(2021, 1, 1, 4, 0)},
            synchronize_session=False,
        )
        db.session.commit()
        period = (datetime(2021, 1, 1, 4, 0).date(), date.today() + timedelta(days=1))
        payments = finance_repository.find_all_offerer_payments(booking.offererId, period)

        row_individual = ReimbursementDetails(payments[0]).as_csv_row()
        assert row_individual[0] == 2021
        assert row_individual[1] == "janvier : remboursement 1ère quinzaine"
        row_collective = ReimbursementDetails(payments[1]).as_csv_row()
        assert row_collective[0] == 2021
        assert row_collective[1] == "janvier : remboursement 1ère quinzaine"

        finance_models.Cashflow.query.update(
            {finance_models.Cashflow.creationDate: datetime(2021, 2, 16, 4, 0)},
            synchronize_session=False,
        )
        db.session.commit()

        period = (datetime(2021, 2, 16, 4, 0).date(), date.today() + timedelta(days=1))
        payments = finance_repository.find_all_offerer_payments(booking.offererId, period)
        row_individual = ReimbursementDetails(payments[0]).as_csv_row()
        assert row_individual[0] == 2021
        assert row_individual[1] == "février : remboursement 2nde quinzaine"

        row_collective = ReimbursementDetails(payments[1]).as_csv_row()
        assert row_collective[0] == 2021
        assert row_collective[1] == "février : remboursement 2nde quinzaine"
