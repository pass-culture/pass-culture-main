from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.offerers.models import Offerer
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.factories as users_factories
from pcapi.domain.payments import PaymentDetails
from pcapi.domain.payments import UnmatchedPayments
from pcapi.domain.payments import _set_end_to_end_id_and_group_into_transactions
from pcapi.domain.payments import apply_banishment
from pcapi.domain.payments import create_payment_for_booking
from pcapi.domain.payments import filter_out_already_paid_for_bookings
from pcapi.domain.payments import filter_out_bookings_without_cost
from pcapi.domain.payments import generate_venues_csv
from pcapi.domain.payments import keep_only_not_processable_payments
from pcapi.domain.payments import make_transaction_label
from pcapi.domain.reimbursement import BookingReimbursement
from pcapi.domain.reimbursement import PhysicalOffersReimbursement
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Booking
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import payment_queries
from pcapi.utils.human_ids import humanize


@freeze_time("2021-01-01 12:00:00")
@pytest.mark.usefixtures("db_session")
class CreatePaymentForBookingTest:
    def test_basics(self):
        offerer = offers_factories.OffererFactory(name="offerer", siren="123456")
        booking = bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer)
        reimbursement = BookingReimbursement(booking, PhysicalOffersReimbursement(), Decimal(10))
        batch_date = datetime.utcnow()

        payment = create_payment_for_booking(reimbursement, batch_date)

        assert payment.bookingId == booking.id
        assert payment.amount == 10
        assert payment.reimbursementRule == PhysicalOffersReimbursement().description
        assert payment.reimbursementRate == PhysicalOffersReimbursement().rate
        assert payment.comment is None
        assert payment.author == "batch"
        assert payment.transactionLabel == "pass Culture Pro - remboursement 1ère quinzaine 01-2021"
        assert payment.batchDate == batch_date
        assert payment.iban is None
        assert payment.bic is None
        assert payment.recipientName == "offerer"
        assert payment.recipientSiren == "123456"

    def test_use_iban_and_bic_from_venue(self):
        booking = bookings_factories.BookingFactory()
        offers_factories.BankInformationFactory(venue=booking.venue, iban="iban1", bic="bic1")
        offers_factories.BankInformationFactory(offerer=booking.offerer, iban="iban2", bic="bic2")
        reimbursement = BookingReimbursement(booking, PhysicalOffersReimbursement(), Decimal(10))
        batch_date = datetime.utcnow()

        payment = create_payment_for_booking(reimbursement, batch_date)

        assert payment.iban == "IBAN1"
        assert payment.bic == "BIC1"

    def test_use_iban_and_bic_from_offerer(self):
        booking = bookings_factories.BookingFactory()
        offers_factories.BankInformationFactory(offerer=booking.offerer, iban="iban", bic="bic")
        reimbursement = BookingReimbursement(booking, PhysicalOffersReimbursement(), Decimal(10))
        batch_date = datetime.utcnow()

        payment = create_payment_for_booking(reimbursement, batch_date)

        assert payment.iban == "IBAN"
        assert payment.bic == "BIC"

    def test_with_custom_reimbursement_rule(self):
        booking = bookings_factories.BookingFactory()
        rule = payments_factories.CustomReimbursementRuleFactory(offer=booking.stock.offer, amount=2)
        reimbursement = BookingReimbursement(booking, rule, Decimal(2))
        batch_date = datetime.utcnow()

        payment = create_payment_for_booking(reimbursement, batch_date)
        assert payment.amount == 2
        assert payment.customReimbursementRuleId == rule.id
        assert payment.reimbursementRate is None
        assert payment.reimbursementRule is None


class FilterOutAlreadyPaidForBookingsTest:
    def test_it_returns_reimbursements_on_bookings_with_no_existing_payments(self):
        # Given
        booking_paid = Booking()
        booking_paid.payments = [Payment()]
        booking_reimbursement1 = BookingReimbursement(booking_paid, PhysicalOffersReimbursement(), Decimal(10))
        booking_not_paid = Booking()
        booking_reimbursement2 = BookingReimbursement(booking_not_paid, PhysicalOffersReimbursement(), Decimal(10))
        booking_reimbursements = [booking_reimbursement1, booking_reimbursement2]

        # When
        bookings_not_paid = filter_out_already_paid_for_bookings(booking_reimbursements)

        # Then
        assert len(bookings_not_paid) == 1
        assert not bookings_not_paid[0].booking.payments

    def test_it_returns_an_empty_list_if_everything_has_been_reimbursed(self):
        # Given
        booking_paid1 = Booking()
        booking_paid1.payments = [Payment()]
        booking_reimbursement1 = BookingReimbursement(booking_paid1, PhysicalOffersReimbursement(), Decimal(10))

        booking_paid2 = Booking()
        booking_paid2.payments = [Payment()]
        booking_reimbursement2 = BookingReimbursement(booking_paid2, PhysicalOffersReimbursement(), Decimal(10))

        # When
        bookings_not_paid = filter_out_already_paid_for_bookings([booking_reimbursement1, booking_reimbursement2])

        # Then
        assert bookings_not_paid == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # When
        bookings_not_paid = filter_out_already_paid_for_bookings([])

        # Then
        assert bookings_not_paid == []


class FilterOutBookingsWithoutCostTest:
    def test_it_returns_reimbursements_on_bookings_with_reimbursed_value_greater_than_zero(self):
        # given
        reimbursement1 = BookingReimbursement(Booking(), PhysicalOffersReimbursement(), Decimal(10))
        reimbursement2 = BookingReimbursement(Booking(), PhysicalOffersReimbursement(), Decimal(0))

        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([reimbursement1, reimbursement2])

        # then
        assert len(bookings_reimbursements_with_cost) == 1
        assert bookings_reimbursements_with_cost[0].reimbursed_amount > Decimal(0)

    def test_it_returns_an_empty_list_if_everything_has_a_cost(self):
        # given
        reimbursement1 = BookingReimbursement(Booking(), PhysicalOffersReimbursement(), Decimal(0))
        reimbursement2 = BookingReimbursement(Booking(), PhysicalOffersReimbursement(), Decimal(0))

        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([reimbursement1, reimbursement2])

        # then
        assert bookings_reimbursements_with_cost == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # when
        bookings_reimbursements_with_cost = filter_out_bookings_without_cost([])

        # then
        assert bookings_reimbursements_with_cost == []


class KeepOnlyNotProcessablePaymentsTest:
    def test_it_returns_only_payments_with_current_status_as_not_processable(self):
        # given
        user = users_factories.UserFactory.build()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payments = [
            create_payment(booking, offerer, 30, status=TransactionStatus.PENDING),
            create_payment(booking, offerer, 30, status=TransactionStatus.NOT_PROCESSABLE),
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR),
        ]

        # when
        pending_payments = keep_only_not_processable_payments(payments)

        # then
        assert len(pending_payments) == 1
        assert pending_payments[0].currentStatus.status == TransactionStatus.NOT_PROCESSABLE

    def test_it_returns_an_empty_list_if_everything_has_no_not_processable_payment(self):
        # given
        user = users_factories.UserFactory.build()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payments = [
            create_payment(booking, offerer, 30, status=TransactionStatus.SENT),
            create_payment(booking, offerer, 30, status=TransactionStatus.SENT),
            create_payment(booking, offerer, 30, status=TransactionStatus.ERROR),
        ]

        # when
        pending_payments = keep_only_not_processable_payments(payments)

        # then
        assert pending_payments == []

    def test_it_returns_an_empty_list_if_an_empty_list_is_given(self):
        # when
        pending_payments = keep_only_not_processable_payments([])

        # then
        assert pending_payments == []


class CreatePaymentDetailsTest:
    def test_contains_info_on_bank_transaction(self):
        # given
        user = users_factories.UserFactory.build()
        booking = create_booking(user=user)
        offerer = create_offerer()
        payment = create_payment(booking, offerer, 35, iban="123456789")

        # when
        details = PaymentDetails(payment)

        # then
        assert details.payment_iban == "123456789"
        assert details.reimbursed_amount == 35
        assert details.reimbursement_rate == 0.5

    @pytest.mark.usefixtures("db_session")
    def test_contains_info_on_booking(self):
        # given
        booking = bookings_factories.BookingFactory(
            dateCreated=datetime(2018, 2, 5),
            dateUsed=datetime(2018, 2, 19),
        )
        payment = payments_factories.PaymentFactory(booking=booking)

        # when
        details = PaymentDetails(payment)

        # then
        assert details.booking_date == datetime(2018, 2, 5)
        assert details.booking_amount == booking.stock.price * booking.quantity
        assert details.booking_used_date == datetime(2018, 2, 19)

    def test_contains_info_on_offerer(self):
        # given
        user = users_factories.UserFactory.build(email="jane.doe@test.com", id=3)
        offerer = create_offerer(siren="987654321", name="Joe le Libraire")
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)

        # when
        details = PaymentDetails(payment)

        # then
        assert details.offerer_name == "Joe le Libraire"
        assert details.offerer_siren == "987654321"

    def test_contains_info_on_venue(self):
        # given
        user = users_factories.UserFactory.build(email="jane.doe@test.com", id=3)
        offerer = create_offerer(siren="987654321", name="Joe le Libraire")
        venue = create_venue(offerer, name="Jack le Sculpteur", siret="1234567891234", idx=1)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)

        # when
        details = PaymentDetails(payment)

        # then
        assert details.venue_name == "Jack le Sculpteur"
        assert details.venue_siret == "1234567891234"
        assert details.venue_humanized_id == humanize(venue.id)

    def test_contains_info_on_offer(self):
        # given
        user = users_factories.UserFactory.build(email="jane.doe@test.com", id=3)
        offerer = create_offerer(siren="987654321", name="Joe le Libraire")
        venue = create_venue(offerer, name="Jack le Sculpteur", siret="1234567891234")
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=12, quantity=5)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2018, 2, 5), idx=5, quantity=2)
        payment = create_payment(booking, offerer, 35)

        # when
        details = PaymentDetails(payment)

        # then
        assert details.offer_name == "Test Book"
        assert details.offer_subcategory_id == "VOD"


@pytest.mark.usefixtures("db_session")
def test_generate_venues_csv():
    venue1 = offers_factories.VenueFactory(
        name="Venue 1",
        siret="siret1",
        managingOfferer__name="Offerer 1",
        managingOfferer__siren="siren1",
    )
    payments_factories.PaymentFactory(
        booking__stock__offer__venue=venue1,
        author="",
        iban="iban1",
        bic="bic1",
        amount=10,
    )
    venue2 = offers_factories.VenueFactory(
        name="Venue 2",
        siret="siret2",
        managingOfferer__name="Offerer 2",
        managingOfferer__siren="siren2",
    )
    payments_factories.PaymentFactory(
        booking__stock__offer__venue=venue2,
        author="",
        iban="iban2",
        bic="bic2",
        amount=20,
    )
    payments_factories.PaymentFactory(
        booking__stock__offer__venue=venue2,
        author="",
        iban="iban2",
        bic="bic2",
        amount=40,
    )

    csv = generate_venues_csv(Payment.query)

    rows = csv.splitlines()
    assert len(rows) == 3
    assert rows[0].startswith('"ID lieu","SIREN"')
    assert rows[1] == ",".join(
        [
            f'"{humanize(venue1.id)}"',
            '"siren1"',
            '"Offerer 1"',
            '"siret1"',
            '"Venue 1"',
            '"Offerer 1-Venue 1"',
            '"iban1"',
            '"bic1"',
            "10.00",
        ],
    )
    assert rows[2] == ",".join(
        [
            f'"{humanize(venue2.id)}"',
            '"siren2"',
            '"Offerer 2"',
            '"siret2"',
            '"Venue 2"',
            '"Offerer 2-Venue 2"',
            '"iban2"',
            '"bic2"',
            "60.00",
        ],
    )


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


class ApplyBanishmentTest:
    def test_payments_matching_given_ids_must_be_banned(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
            create_payment(Booking(), Offerer(), 10, idx=333),
            create_payment(Booking(), Offerer(), 10, idx=444),
        ]
        ids_to_ban = [222, 333]

        # when
        banned_payments, _retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(banned_payments) == 2
        for p in banned_payments:
            assert p.currentStatus.status == TransactionStatus.BANNED
            assert p.id in ids_to_ban

    def test_payments_not_matching_given_ids_must_be_retried(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
            create_payment(Booking(), Offerer(), 10, idx=333),
            create_payment(Booking(), Offerer(), 10, idx=444),
        ]
        ids_to_ban = [222, 333]

        # when
        _banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(retry_payments) == 2
        for p in retry_payments:
            assert p.currentStatus.status == TransactionStatus.RETRY
            assert p.id not in ids_to_ban

    def test_no_payments_to_retry_if_all_are_banned(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
        ]
        ids_to_ban = [111, 222]

        # when
        banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert len(banned_payments) == 2
        assert retry_payments == []

    def test_no_payments_are_returned_if_no_ids_are_provided(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
        ]
        ids_to_ban = []

        # when
        banned_payments, retry_payments = apply_banishment(payments, ids_to_ban)

        # then
        assert banned_payments == []
        assert retry_payments == []

    def test_value_error_is_raised_if_payments_ids_do_not_match_payments(self):
        # given
        payments = [
            create_payment(Booking(), Offerer(), 10, idx=111),
            create_payment(Booking(), Offerer(), 10, idx=222),
        ]
        ids_to_ban = [222, 333]

        # when
        with pytest.raises(UnmatchedPayments) as e:
            apply_banishment(payments, ids_to_ban)

        # then
        assert e.value.payment_ids == {333}


@pytest.mark.usefixtures("db_session")
def test_set_end_to_end_id_and_group_into_transactions():
    batch_date = datetime.now()
    transaction_label = "remboursement 1ère quinzaine 09-2018"
    iban1, bic1 = "CF13QSDFGH456789", "QSDFGH8Z555"
    offerer1 = offers_factories.OffererFactory(siren="siren1")
    p1 = payments_factories.PaymentFactory(
        batchDate=batch_date,
        amount=10,
        iban=iban1,
        bic=bic1,
        transactionLabel=transaction_label,
        recipientName="offerer1",
        booking__stock__offer__venue__managingOfferer=offerer1,
    )
    offerer2 = offers_factories.OffererFactory(siren="siren2")
    iban2, bic2 = "FR14WXCVBN123456", "WXCVBN7B444"
    p2 = payments_factories.PaymentFactory(
        batchDate=batch_date,
        amount=20,
        iban=iban2,
        bic=bic2,
        recipientName="offerer2",
        transactionLabel=transaction_label,
        booking__stock__offer__venue__managingOfferer=offerer2,
    )
    p3 = payments_factories.PaymentFactory(
        batchDate=batch_date,
        amount=40,
        iban=iban2,
        bic=bic2,
        recipientName="offerer2",
        transactionLabel=transaction_label,
        booking__stock__offer__venue__managingOfferer=offerer2,
    )
    offerer3 = offers_factories.OffererFactory(siren="siren3")
    p4 = payments_factories.PaymentFactory(
        batchDate=batch_date - timedelta(days=1),
        amount=40,
        iban=iban2,
        bic=bic2,
        recipientName="offerer3, ignored because not the same batch date",
        transactionLabel=transaction_label,
        booking__stock__offer__venue__managingOfferer=offerer3,
    )
    p5 = payments_factories.PaymentFactory(
        batchDate=batch_date,
        amount=40,
        iban=iban2,
        bic=bic2,
        recipientName="offerer3, ignored because not processable",
        transactionLabel=transaction_label,
        booking__stock__offer__venue__managingOfferer=offerer3,
    )
    payments_factories.PaymentStatusFactory(payment=p5, status=TransactionStatus.NOT_PROCESSABLE)

    # Mimic the query that `generate_and_send_payments()` passes to
    # `send_transactions()` that itself passes it to
    # `_set_end_to_end_id_and_group_into_transactions()`
    payment_query = payment_queries.get_payments_by_status(
        (TransactionStatus.PENDING, TransactionStatus.ERROR, TransactionStatus.RETRY), batch_date
    )
    transactions = _set_end_to_end_id_and_group_into_transactions(payment_query, batch_date)

    assert len(transactions) == 2
    assert transactions[0].creditor_iban == iban1
    assert transactions[0].creditor_bic == bic1
    assert transactions[0].creditor_name == "offerer1"
    assert transactions[0].creditor_siren == "siren1"
    assert transactions[0].end_to_end_id == p1.transactionEndToEndId
    assert transactions[0].amount == 10
    assert transactions[0].custom_message == p1.transactionLabel

    assert transactions[1].creditor_iban == iban2
    assert transactions[1].creditor_bic == bic2
    assert transactions[1].creditor_name == "offerer2"
    assert transactions[1].creditor_siren == "siren2"
    assert transactions[1].end_to_end_id == p2.transactionEndToEndId
    assert transactions[1].amount == 60
    assert transactions[1].custom_message == p2.transactionLabel

    # FIXME: check transactionEndToEndId
    assert p1.transactionEndToEndId is not None
    assert p1.transactionEndToEndId != p2.transactionEndToEndId
    assert p2.transactionEndToEndId == p3.transactionEndToEndId
    assert p4.transactionEndToEndId is None
    assert p5.transactionEndToEndId is None
