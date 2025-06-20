from datetime import datetime
from datetime import timedelta

import pytest
import sqlalchemy.exc

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.bookings import api
from pcapi.core.bookings import exceptions
from pcapi.core.bookings import factories
from pcapi.core.bookings import models
from pcapi.core.bookings import validation
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.finance.models import DepositType
from pcapi.models import db
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class CheckCanBookFreeOfferTest:
    def test_dont_raise(self):
        user = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory()
        validation.check_can_book_free_offer(user, stock)  # should not raise

    @pytest.mark.usefixtures("db_session")
    def test_should_raise_exception_when_user_cannot_book_a_free_offer(self):
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
        assert error.value.errors == {"offerId": ["Cette offre a déjà été réservée par l'utilisateur"]}


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
        yesterday = datetime.utcnow() - timedelta(days=1)
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
        return users_factories.BeneficiaryGrant18Factory(
            deposit__version=1, deposit__amount=500, deposit__type=DepositType.GRANT_18
        )

    def test_physical_limit(self):
        beneficiary = self._get_beneficiary()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        factories.BookingFactory(user=beneficiary, stock__price=190, stock__offer=offer)

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

        with pytest.raises(exceptions.PhysicalExpenseLimitHasBeenReached) as error:
            validation.check_expenses_limits(beneficiary, 11, offer)
        assert error.value.errors["global"] == [
            "Le plafond de 200 € pour les biens culturels ne vous permet pas de réserver cette offre."
        ]

    def test_physical_limit_on_uncapped_type(self):
        beneficiary = self._get_beneficiary()
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        factories.BookingFactory(user=beneficiary, stock__price=190, stock__offer=offer)

        # should not raise because SEANCE_CINE is not capped
        validation.check_expenses_limits(beneficiary, 11, offer)

    def test_digital_limit(self):
        beneficiary = self._get_beneficiary()
        offer = offers_factories.DigitalOfferFactory(subcategoryId=subcategories.VOD.id)
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
        offer = offers_factories.DigitalOfferFactory(subcategoryId=subcategories.OEUVRE_ART.id)
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
        return users_factories.BeneficiaryGrant18Factory(**kwargs)

    def test_raise_if_deposit_expired(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        beneficiary = self._get_beneficiary(deposit__expirationDate=yesterday)
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        with pytest.raises(exceptions.UserHasInsufficientFunds):
            validation.check_expenses_limits(beneficiary, 10, offer)

    def test_physical_limit(self):
        beneficiary = self._get_beneficiary()
        price = beneficiary.deposit.amount - 10
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        factories.BookingFactory(user=beneficiary, stock__price=price, stock__offer=offer)

        validation.check_expenses_limits(beneficiary, 10, offer)  # should not raise

    def test_digital_limit(self):
        beneficiary = self._get_beneficiary()
        offer = offers_factories.DigitalOfferFactory(subcategoryId=subcategories.VOD.id)
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
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.OEUVRE_ART.id)
        price = beneficiary.deposit.specific_caps.DIGITAL_CAP - 10
        factories.BookingFactory(user=beneficiary, stock__price=price, stock__offer=offer)

        # should not raise because OEUVRE_ART is not capped
        validation.check_expenses_limits(beneficiary, 11, offer)

    def test_global_limit(self):
        beneficiary = self._get_beneficiary()
        price = beneficiary.deposit.amount - 10
        factories.BookingFactory(user=beneficiary, stock__price=price)
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
        deposit.expirationDate = datetime.utcnow() - timedelta(days=1)
        repository.save(deposit)

    def test_insufficient_funds_when_user_has_expired_deposit(self):
        # The user once booked.
        user = users_factories.BeneficiaryGrant18Factory()
        factories.BookingFactory(user=user)

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
        assert db.session.query(models.Booking).filter(Booking.userId == user.id).count() == 2

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

        assert "insufficientFunds" in str(exc.value)

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
        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            validation.check_is_usable(booking)

    def should_raise_if_cancelled(self):
        booking = factories.CancelledBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyCancelled):
            validation.check_is_usable(booking)

    def should_raises_forbidden_error_if_reimbursed(self):
        booking = factories.ReimbursedBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyRefunded):
            validation.check_is_usable(booking)

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

    def should_not_validate_when_event_booking_not_confirmed(self):
        # Given
        next_week = datetime.utcnow() + timedelta(weeks=1)
        one_day_before = datetime.utcnow() - timedelta(days=1)
        booking = factories.BookingFactory(dateCreated=one_day_before, stock__beginningDatetime=next_week)

        # When
        with pytest.raises(exceptions.BookingIsNotConfirmed):
            validation.check_is_usable(booking)


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
            "réservée et moins de 48h avant le début de l'évènement"
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
            "réservée et moins de 48h avant le début de l'évènement"
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
            "réservée et moins de 48h avant le début de l'évènement"
        ]


@pytest.mark.usefixtures("db_session")
class CheckOffererCanCancelBookingTest:
    def test_can_cancel(self):
        booking = factories.BookingFactory()
        validation.check_booking_can_be_cancelled(booking)  # should not raise

    def test_raise_if_already_cancelled(self):
        booking = factories.CancelledBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyCancelled):
            validation.check_booking_can_be_cancelled(booking)

    def test_raise_if_already_used(self):
        booking = factories.UsedBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            validation.check_booking_can_be_cancelled(booking)


@pytest.mark.usefixtures("db_session")
class CheckCanBeMarkAsUnusedTest:
    def test_should_raise_resource_gone_error_if_not_used(self):
        booking = factories.BookingFactory()
        with pytest.raises(exceptions.BookingIsNotUsed):
            validation.check_can_be_mark_as_unused(booking)

    def test_should_raise_resource_gone_error_if_cancelled(self):
        booking = factories.CancelledBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyCancelled):
            validation.check_can_be_mark_as_unused(booking)

    def test_should_raise_resource_gone_error_if_reimbursed(self):
        booking = factories.ReimbursedBookingFactory()
        with pytest.raises(exceptions.BookingIsAlreadyRefunded):
            validation.check_can_be_mark_as_unused(booking)


@pytest.mark.usefixtures("db_session")
class CheckOfferCategoryIsBookableByUserTest:
    def test_should_raise_video_game_free(self):
        user = users_factories.UnderageBeneficiaryFactory()
        stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.ABO_JEU_VIDEO.id, price=10)

        with pytest.raises(exceptions.OfferCategoryNotBookableByUser):
            validation.check_offer_category_is_bookable_by_user(user, stock)

    def test_should_raise_video_game_not_free(self):
        user = users_factories.UnderageBeneficiaryFactory()
        stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.ABO_JEU_VIDEO.id, price=0)

        with pytest.raises(exceptions.OfferCategoryNotBookableByUser):
            validation.check_offer_category_is_bookable_by_user(user, stock)

    def test_should_not_raise_video_game_bene_18(self):
        user = users_factories.BeneficiaryGrant18Factory()
        stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.ABO_JEU_VIDEO.id)

        validation.check_offer_category_is_bookable_by_user(user, stock)

    def test_should_raise_digital(self):
        user = users_factories.UnderageBeneficiaryFactory()
        stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.VISITE_VIRTUELLE.id)

        with pytest.raises(exceptions.OfferCategoryNotBookableByUser):
            validation.check_offer_category_is_bookable_by_user(user, stock)

    def test_should_not_raise_digital_free(self):
        user = users_factories.UnderageBeneficiaryFactory()
        stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.VISITE_VIRTUELLE.id, price=0)

        validation.check_offer_category_is_bookable_by_user(user, stock)

    def test_should_not_raise_digital_press(self):
        user = users_factories.UnderageBeneficiaryFactory()
        stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.ABO_PRESSE_EN_LIGNE.id)

        validation.check_offer_category_is_bookable_by_user(user, stock)

    def test_should_not_raise_digital_audio_book(self):
        user = users_factories.UnderageBeneficiaryFactory()
        stock = offers_factories.StockFactory(offer__subcategoryId=subcategories.LIVRE_NUMERIQUE.id)

        validation.check_offer_category_is_bookable_by_user(user, stock)
