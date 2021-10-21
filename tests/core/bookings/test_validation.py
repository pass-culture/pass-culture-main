from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest
import sqlalchemy.exc

from pcapi.core.bookings import api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import factories
from pcapi.core.bookings import models
from pcapi.core.bookings import validation
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class CheckCanBookFreeOfferTest:
    def test_dont_raise(self):
        user = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory()
        validation.check_can_book_free_offer(user, stock)  # should not raise

    @pytest.mark.usefixtures("db_session")
    def test_should_raise_exception_when_user_cannot_book_a_free_offer(self, app):
        user = users_factories.UserFactory()
        stock = offers_factories.StockFactory(price=0)

        with pytest.raises(exceptions.CannotBookFreeOffers) as error:
            validation.check_can_book_free_offer(user, stock)
        assert error.value.errors == {
            "cannotBookFreeOffers": ["Votre compte ne vous permet pas de faire de réservation."]
        }


@pytest.mark.usefixtures("db_session")
class CheckOfferAlreadyBookedTest:
    def test_dont_raise_if_user_never_booked_this_offer(self):
        offer = offers_factories.OfferFactory()
        user = users_factories.UserFactory()
        validation.check_offer_already_booked(user, offer)  # should not raise

    def test_dont_raise_if_user_cancelled(self):
        booking = factories.CancelledBookingFactory()
        validation.check_offer_already_booked(booking.user, booking.stock.offer)  # should not raise

    @pytest.mark.usefixtures("db_session")
    def test_raise_if_already_booked(self):
        booking = factories.BookingFactory()

        with pytest.raises(exceptions.OfferIsAlreadyBooked) as error:
            validation.check_offer_already_booked(booking.user, booking.stock.offer)
        assert error.value.errors == {"offerId": ["Cette offre a déja été reservée par l'utilisateur"]}


@pytest.mark.usefixtures("db_session")
class CheckQuantityTest:
    def test_ok_on_single(self):
        offer = offers_factories.OfferFactory()
        validation.check_quantity(offer, 1)  # should not raise

    @pytest.mark.parametrize("quantity", [1, 2])
    def test_ok_on_duo(self, quantity):
        offer = offers_factories.OfferFactory(isDuo=True)
        validation.check_quantity(offer, quantity)  # should not raise

    @pytest.mark.parametrize("quantity", [0, -1])
    def test_raise_if_zero_or_negative_on_single(self, quantity):
        offer = offers_factories.OfferFactory()

        with pytest.raises(exceptions.QuantityIsInvalid) as error:
            validation.check_quantity(offer, 0)
        assert error.value.errors["quantity"] == ["Vous ne pouvez réserver qu'une place pour cette offre."]

    @pytest.mark.parametrize("quantity", [0, -1])
    def test_raise_if_zero_or_negative_on_duo(self, quantity):
        offer = offers_factories.OfferFactory(isDuo=True)

        with pytest.raises(exceptions.QuantityIsInvalid) as error:
            validation.check_quantity(offer, 0)
        assert error.value.errors["quantity"] == ["Vous devez réserver une place ou deux dans le cas d'une offre DUO."]

    def test_raise_if_more_than_one_on_single(self):
        offer = offers_factories.OfferFactory()

        with pytest.raises(exceptions.QuantityIsInvalid) as error:
            validation.check_quantity(offer, 2)
        assert error.value.errors["quantity"] == ["Vous ne pouvez réserver qu'une place pour cette offre."]

    def test_raise_if_more_than_two_on_duo(self):
        offer = offers_factories.OfferFactory(isDuo=True)

        with pytest.raises(exceptions.QuantityIsInvalid) as error:
            validation.check_quantity(offer, 3)
        assert error.value.errors["quantity"] == ["Vous devez réserver une place ou deux dans le cas d'une offre DUO."]


@pytest.mark.usefixtures("db_session")
class CheckStockIsBookableTest:
    booking_quantity = 1

    def test_dont_raise_if_bookable(self):
        stock = offers_factories.StockFactory()
        validation.check_stock_is_bookable(stock, self.booking_quantity)  # should not raise

    def test_raise_if_not_bookable(self):
        yesterday = datetime.now() - timedelta(days=1)
        stock = offers_factories.StockFactory(bookingLimitDatetime=yesterday)

        with pytest.raises(exceptions.StockIsNotBookable) as error:
            validation.check_stock_is_bookable(stock, self.booking_quantity)
        assert error.value.errors == {"stock": ["Ce stock n'est pas réservable"]}

    def test_raise_if_duo_not_bookable(self):
        stock_quantity = 1
        booking_quantity = 2
        offer = offers_factories.OfferFactory(isDuo=True)
        stock = offers_factories.StockFactory(offer=offer, quantity=stock_quantity)

        with pytest.raises(exceptions.StockIsNotBookable) as error:
            validation.check_stock_is_bookable(stock, booking_quantity)
        assert error.value.errors == {"stock": ["Ce stock n'est pas réservable"]}


@pytest.mark.usefixtures("db_session")
class CheckExpenseLimitsDepositVersion1Test:
    def _get_beneficiary(self):
        return users_factories.BeneficiaryGrant18Factory(deposit__version=1)

    def test_physical_limit(self):
        beneficiary = self._get_beneficiary()
        offer = offers_factories.OfferFactory(product__subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        factories.BookingFactory(user=beneficiary, stock__price=190, stock__offer=offer)

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

        with pytest.raises(exceptions.PhysicalExpenseLimitHasBeenReached) as error:
            validation.check_expenses_limits(beneficiary, 11, offer)
        assert error.value.errors["global"] == [
            "Le plafond de 200 € pour les biens culturels ne vous permet pas de réserver cette offre."
        ]

    def test_physical_limit_on_uncapped_type(self):
        beneficiary = self._get_beneficiary()
        offer = offers_factories.OfferFactory(product__subcategoryId=subcategories.SEANCE_CINE.id)
        factories.BookingFactory(user=beneficiary, stock__price=190, stock__offer=offer)

        # should not raise because SEANCE_CINE is not capped
        validation.check_expenses_limits(beneficiary, 11, offer)

    def test_digital_limit(self):
        beneficiary = self._get_beneficiary()
        product = offers_factories.DigitalProductFactory(subcategoryId=subcategories.VOD.id)
        offer = offers_factories.OfferFactory(product=product)
        factories.BookingFactory(
            user=beneficiary,
            stock__price=190,
            stock__offer=offer,
        )

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

        with pytest.raises(exceptions.DigitalExpenseLimitHasBeenReached) as error:
            validation.check_expenses_limits(beneficiary, 11, offer)
        assert error.value.errors["global"] == [
            "Le plafond de 200 € pour les offres numériques ne vous permet pas de réserver cette offre."
        ]

    def test_digital_limit_on_uncapped_type(self):
        beneficiary = self._get_beneficiary()
        product = offers_factories.DigitalProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        offer = offers_factories.OfferFactory(product=product)
        factories.BookingFactory(user=beneficiary, stock__price=190, stock__offer=offer)

        # should not raise because OEUVRE_ART is not capped
        validation.check_expenses_limits(beneficiary, 11, offer)

    def test_global_limit(self):
        beneficiary = self._get_beneficiary()
        factories.BookingFactory(user=beneficiary, stock__price=490)
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.EVENEMENT_MUSIQUE.id)

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

        with pytest.raises(exceptions.UserHasInsufficientFunds) as error:
            validation.check_expenses_limits(beneficiary, 11, offer)
        assert error.value.errors["insufficientFunds"] == [
            "Le solde de votre pass est insuffisant pour réserver cette offre."
        ]


@pytest.mark.usefixtures("db_session")
class CheckExpenseLimitsDepositVersion2Test:
    def _get_beneficiary(self, **kwargs):
        return users_factories.BeneficiaryGrant18Factory(deposit__version=2, **kwargs)

    def test_raise_if_deposit_expired(self):
        yesterday = datetime.now() - timedelta(days=1)
        beneficiary = self._get_beneficiary(deposit__expirationDate=yesterday)
        offer = offers_factories.OfferFactory(product__subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        with pytest.raises(exceptions.UserHasInsufficientFunds):
            validation.check_expenses_limits(beneficiary, 10, offer)

    def test_physical_limit(self):
        beneficiary = self._get_beneficiary()
        offer = offers_factories.OfferFactory(product__subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        factories.BookingFactory(user=beneficiary, stock__price=290, stock__offer=offer)

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

    def test_digital_limit(self):
        beneficiary = self._get_beneficiary()
        product = offers_factories.DigitalProductFactory(subcategoryId=subcategories.VOD.id)
        offer = offers_factories.OfferFactory(product=product)
        factories.BookingFactory(
            user=beneficiary,
            stock__price=90,
            stock__offer=offer,
        )

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

        with pytest.raises(exceptions.DigitalExpenseLimitHasBeenReached) as error:
            validation.check_expenses_limits(beneficiary, 11, offer)
        assert error.value.errors["global"] == [
            "Le plafond de 100 € pour les offres numériques ne vous permet pas de réserver cette offre."
        ]

    def test_digital_limit_on_uncapped_type(self):
        beneficiary = self._get_beneficiary()
        product = offers_factories.DigitalProductFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        offer = offers_factories.OfferFactory(product=product)
        factories.BookingFactory(user=beneficiary, stock__price=190, stock__offer=offer)

        # should not raise because OEUVRE_ART is not capped
        validation.check_expenses_limits(beneficiary, 11, offer)

    def test_global_limit(self):
        beneficiary = self._get_beneficiary()
        factories.BookingFactory(user=beneficiary, stock__price=290)
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.CARTE_CINE_ILLIMITE.id)

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

        with pytest.raises(exceptions.UserHasInsufficientFunds) as error:
            validation.check_expenses_limits(beneficiary, 11, offer)
        assert error.value.errors["insufficientFunds"] == [
            "Le solde de votre pass est insuffisant pour réserver cette offre."
        ]


@pytest.mark.usefixtures("db_session")
class InsufficientFundsSQLCheckTest:
    def _expire_deposit(self, user):
        deposit = user.deposits[0]
        deposit.expirationDate = datetime.now() - timedelta(days=1)
        repository.save(deposit)

    def test_insufficient_funds_when_user_has_negative_deposit(self):
        # The user once booked.
        booking = factories.BookingFactory(user__deposit__version=1)
        user = booking.user
        assert user.wallet_balance == 490

        # But now their deposit expired.
        self._expire_deposit(user)

        # They are not allowed to book non-free offers anymore.
        with pytest.raises(sqlalchemy.exc.InternalError) as exc:
            factories.BookingFactory(user=user)
            assert "insufficientFunds" in exc.args[0]

    def test_user_can_cancel_even_if_expired_deposit(self):
        # The user once booked.
        booking = factories.BookingFactory()
        user = booking.user
        booking_to_cancel = factories.BookingFactory(user=user)

        # But now their deposit expired.
        self._expire_deposit(user)

        # They should be able to cancel their booking.
        api.cancel_booking_by_beneficiary(user, booking_to_cancel)
        assert booking_to_cancel.isCancelled
        assert booking_to_cancel.status is BookingStatus.CANCELLED

    def test_user_can_book_a_free_offer_even_if_expired_deposit(self):
        # The user once booked.
        booking = factories.BookingFactory()
        user = booking.user

        # But now their deposit expired.
        self._expire_deposit(user)

        # They should be able to book free offers
        stock = offers_factories.StockFactory(price=0)
        api.book_offer(user, stock.id, quantity=1)
        assert models.Booking.query.filter_by(user=user).count() == 2

    def test_cannot_change_quantity_with_expired_deposit(self):
        # The user once booked.
        booking = factories.BookingFactory(quantity=10)
        user = booking.user

        # But now their deposit expired.
        self._expire_deposit(user)

        # The backend should not do that, but if it does, the database
        # should prevent it.
        booking.quantity += 10
        with pytest.raises(sqlalchemy.exc.InternalError) as exc:
            db.session.add(booking)
            db.session.flush()
            assert "insufficientFunds" in exc.args[0]

    def test_cannot_change_amount_with_expired_deposit(self):
        # The user once booked.
        booking = factories.BookingFactory(amount=10)
        user = booking.user

        # But now their deposit expired.
        self._expire_deposit(user)

        # The backend should not do that, but if it does, the database
        # should prevent it.
        booking.amount += 10
        with pytest.raises(sqlalchemy.exc.InternalError) as exc:
            db.session.add(booking)
            db.session.flush()
            assert "insufficientFunds" in exc.args[0]

    def test_cannot_uncancel_with_expired_deposit(self):
        # The user once booked and cancelled their booking.
        booking = factories.CancelledBookingFactory()
        user = booking.user

        # But now their deposit expired.
        self._expire_deposit(user)

        # The backend should not do that, but if it does, the database
        # should prevent it.
        booking.uncancel_booking_set_used()
        with pytest.raises(sqlalchemy.exc.InternalError) as exc:
            db.session.add(booking)
            db.session.flush()
            assert "insufficientFunds" in exc.args[0]


@pytest.mark.usefixtures("db_session")
class CheckIsUsableTest:
    def should_raise_if_used(self):
        booking = factories.UsedBookingFactory()
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_is_usable(booking)
        assert exc.value.errors["booking"] == ["Cette réservation a déjà été validée"]

    def should_raise_if_cancelled(self):
        booking = factories.CancelledBookingFactory()
        with pytest.raises(api_errors.ForbiddenError) as exc:
            validation.check_is_usable(booking)
        assert exc.value.errors["booking"] == ["Cette réservation a été annulée"]

    def should_raises_forbidden_error_if_payement_exists(self, app):
        booking = factories.UsedBookingFactory()
        payments_factories.PaymentFactory(booking=booking)
        with pytest.raises(api_errors.ForbiddenError) as exc:
            validation.check_is_usable(booking)
        assert exc.value.errors["payment"] == ["Cette réservation a été remboursée"]

    def should_pass_if_no_beginning_datetime(self):
        booking = factories.BookingFactory(stock__beginningDatetime=None)
        validation.check_is_usable(booking)

    def should_pass_when_event_begins_in_less_than_48_hours(self):
        soon = datetime.utcnow() + timedelta(hours=48)
        booking = factories.BookingFactory(stock__beginningDatetime=soon)
        validation.check_is_usable(booking)

    def should_pass_when_event_begins_in_more_than_72_hours_and_booking_created_more_than_48_hours_ago(self):
        next_week = datetime.utcnow() + timedelta(weeks=1)
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        booking = factories.BookingFactory(stock__beginningDatetime=next_week, dateCreated=three_days_ago)
        validation.check_is_usable(booking)

    @freeze_time("2020-10-15 09:00:00")
    def should_not_validate_when_event_booking_not_confirmed(self):
        # Given
        next_week = datetime.utcnow() + timedelta(weeks=1)
        one_day_before = datetime.utcnow() - timedelta(days=1)
        booking = factories.BookingFactory(dateCreated=one_day_before, stock__beginningDatetime=next_week)

        # When
        with pytest.raises(api_errors.ForbiddenError) as exception:
            validation.check_is_usable(booking)

        # Then
        assert exception.value.errors["booking"] == [
            "Cette réservation a été effectuée le 14/10/2020 à 11:00. Veuillez "
            "attendre jusqu’au 16/10/2020 à 11:00 pour valider la contremarque."
        ]

    @freeze_time("2020-10-15 09:00:00")
    def should_use_timezone_of_venue_departmentCode(self):
        # Given
        next_week = datetime.utcnow() + timedelta(weeks=1)
        one_day_before = datetime.utcnow() - timedelta(days=1)

        booking = factories.BookingFactory(
            dateCreated=one_day_before, stock__beginningDatetime=next_week, stock__offer__venue__postalCode="97300"
        )

        # When
        with pytest.raises(api_errors.ForbiddenError) as exception:
            validation.check_is_usable(booking)

        # Then
        assert exception.value.errors["booking"] == [
            "Cette réservation a été effectuée le 14/10/2020 à 06:00. Veuillez "
            "attendre jusqu’au 16/10/2020 à 06:00 pour valider la contremarque."
        ]


@pytest.mark.usefixtures("db_session")
class CheckBeneficiaryCanCancelBookingTest:
    def test_can_cancel(self):
        booking = factories.BookingFactory()
        validation.check_beneficiary_can_cancel_booking(booking.user, booking)  # should not raise

    def test_can_cancel_if_event_is_in_a_long_time(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=10),
        )
        validation.check_beneficiary_can_cancel_booking(booking.user, booking)  # should not raise

    def test_raise_if_not_the_benficiary(self):
        booking = factories.BookingFactory()
        other_user = users_factories.UserFactory()
        with pytest.raises(exceptions.BookingDoesntExist):
            validation.check_beneficiary_can_cancel_booking(other_user, booking)

    def test_raise_if_already_used(self):
        booking = factories.UsedBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)

    def test_raise_if_event_too_close(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=1),
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_booked_long_ago(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=10),
            dateCreated=datetime.utcnow() - timedelta(days=2),
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]

    def test_raise_if_event_too_close_and_booked_long_ago(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=1),
            dateCreated=datetime.utcnow() - timedelta(days=2),
        )
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 48h avant le début de l'événement"
        ]


@pytest.mark.usefixtures("db_session")
class CheckOffererCanCancelBookingTest:
    def test_can_cancel(self):
        booking = factories.BookingFactory()
        validation.check_booking_can_be_cancelled(booking)  # should not raise

    def test_raise_if_already_cancelled(self):
        booking = factories.CancelledBookingFactory()
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_booking_can_be_cancelled(booking)
        assert exc.value.errors["global"] == ["Cette contremarque a déjà été annulée"]

    def test_raise_if_already_used(self):
        booking = factories.UsedBookingFactory()
        with pytest.raises(api_errors.ForbiddenError) as exc:
            validation.check_booking_can_be_cancelled(booking)
        assert exc.value.errors["global"] == ["Impossible d'annuler une réservation consommée"]


@pytest.mark.usefixtures("db_session")
class CheckCanBeMarkAsUnusedTest:
    def test_should_raises_resource_gone_error_if_not_used(self, app):
        booking = factories.BookingFactory(isUsed=False)
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_can_be_mark_as_unused(booking)
        assert exc.value.errors["booking"] == ["Cette réservation n'a pas encore été validée"]

    def test_should_raises_forbidden_error_if_cancelled(self, app):
        booking = factories.CancelledBookingFactory()
        with pytest.raises(api_errors.ForbiddenError) as exc:
            validation.check_can_be_mark_as_unused(booking)
        assert exc.value.errors["booking"] == ["Cette réservation a été annulée"]

    def test_should_raises_resource_gone_error_if_payement_exists(self, app):
        booking = payments_factories.PaymentFactory().booking
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_can_be_mark_as_unused(booking)
        assert exc.value.errors["payment"] == ["Le remboursement est en cours de traitement"]
