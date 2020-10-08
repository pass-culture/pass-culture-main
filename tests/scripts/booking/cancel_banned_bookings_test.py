from datetime import datetime, timedelta

from models import BookingSQLEntity
from models.payment_status import TransactionStatus
from repository import repository
from scripts.booking.cancel_banned_bookings import cancel_banned_bookings
import pytest
from model_creators.generic_creators import create_booking, create_stock, create_venue, create_offerer, \
    create_user, create_deposit, create_payment, create_payment_status
from model_creators.specific_creators import create_offer_with_thing_product


class CancelBannedBookingsTest:
    WANTED_SENT_DATETIME = datetime.strptime("16/04/2020", "%d/%m/%Y")
    WANTED_BANNED_DATETIME = datetime.strptime("17/04/2020", "%d/%m/%Y")

    def setup_method(self):
        self.beneficiary = create_user()
        create_deposit(user=self.beneficiary)
        self.offerer = create_offerer()
        venue = create_venue(self.offerer)
        offer = create_offer_with_thing_product(venue)
        self.stock = create_stock(offer=offer)

    @pytest.mark.usefixtures("db_session")
    def test_should_not_cancel_pending_bookings(self, app):
        # Given
        booking = create_booking(stock=self.stock, user=self.beneficiary, date_used=datetime.utcnow(), is_used=True)
        payment = create_payment(offerer=self.offerer, booking=booking)
        repository.save(payment)

        # When
        cancel_banned_bookings()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_cancel_reimbursed_bookings(self, app):
        # Given
        booking = create_booking(stock=self.stock, user=self.beneficiary, date_used=datetime.utcnow(), is_used=True)
        payment = create_payment(offerer=self.offerer, booking=booking, status=TransactionStatus.SENT)
        repository.save(payment)

        # When
        cancel_banned_bookings()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_cancel_banned_bookings(self, app):
        # Given
        booking = create_booking(stock=self.stock, user=self.beneficiary, date_used=datetime.utcnow(), is_used=True)
        payment = create_payment(offerer=self.offerer, booking=booking, status=TransactionStatus.BANNED)
        repository.save(payment)

        # When
        cancel_banned_bookings()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_cancel_reimbursed_and_banned_bookings_with_current_status_sent(self, app):
        # Given
        booking = create_booking(stock=self.stock, user=self.beneficiary, date_used=datetime.utcnow(), is_used=True)
        payment = create_payment(offerer=self.offerer, booking=booking, status=TransactionStatus.BANNED)
        payment.setStatus(TransactionStatus.SENT)
        repository.save(payment)

        # When
        cancel_banned_bookings()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_cancel_reimbursed_and_banned_bookings_with_current_status_banned_and_unwanted_sent_date(self, app):
        # Given
        unwanted_sent_date = self.WANTED_SENT_DATETIME - timedelta(days=1)
        booking = create_booking(stock=self.stock, user=self.beneficiary, date_used=datetime.utcnow(), is_used=True)
        payment = create_payment(offerer=self.offerer, booking=booking, status=TransactionStatus.SENT, status_date=unwanted_sent_date)
        payment_banned_status = create_payment_status(payment=payment, status=TransactionStatus.BANNED, date=self.WANTED_BANNED_DATETIME)
        payment.statuses.append(payment_banned_status)
        repository.save(payment)

        # When
        cancel_banned_bookings()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_not_cancel_reimbursed_and_banned_bookings_with_current_status_banned_and_unwanted_banned_date(self, app):
        # Given
        booking = create_booking(stock=self.stock, user=self.beneficiary, date_used=datetime.utcnow(), is_used=True)
        payment = create_payment(offerer=self.offerer, booking=booking, status=TransactionStatus.SENT, status_date=self.WANTED_SENT_DATETIME)
        payment.setStatus(TransactionStatus.BANNED)
        repository.save(payment)

        # When
        cancel_banned_bookings()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed is not None

    @pytest.mark.usefixtures("db_session")
    def test_should_cancel_reimbursed_and_banned_bookings_with_current_status_banned_and_wanted_dates(self, app):
        # Given
        booking = create_booking(stock=self.stock, user=self.beneficiary, date_used=datetime.utcnow(), is_used=True)
        payment = create_payment(offerer=self.offerer, booking=booking, status=TransactionStatus.SENT, status_date=self.WANTED_SENT_DATETIME)
        payment_banned_status = create_payment_status(payment=payment, status=TransactionStatus.BANNED, date=self.WANTED_BANNED_DATETIME)
        payment.statuses.append(payment_banned_status)
        repository.save(payment)

        # When
        cancel_banned_bookings()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is True
        assert corrected_booking.cancellationDate is not None
        assert corrected_booking.isUsed is False
        assert corrected_booking.dateUsed is None
