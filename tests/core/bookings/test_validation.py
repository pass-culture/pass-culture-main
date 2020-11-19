from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import exceptions
from pcapi.core.bookings import factories
from pcapi.core.bookings import validation
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import ApiErrors
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.models import api_errors
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class CheckCanBookFreeOfferTest:
    def test_dont_raise(self):
        user = users_factories.UserFactory(canBookFreeOffers=True)
        stock = offers_factories.StockFactory()
        validation.check_can_book_free_offer(user, stock)  # should not raise

    @pytest.mark.usefixtures("db_session")
    def test_should_raise_exception_when_user_cannot_book_a_free_offer(self, app):
        user = users_factories.UserFactory(canBookFreeOffers=False)
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
        booking = factories.BookingFactory(isCancelled=True)
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
    def test_dont_raise_if_bookable(self):
        stock = offers_factories.StockFactory()
        validation.check_stock_is_bookable(stock)  # should not raise

    def test_raise_if_not_bookable(self):
        yesterday = datetime.now() - timedelta(days=1)
        stock = offers_factories.StockFactory(bookingLimitDatetime=yesterday)

        with pytest.raises(exceptions.StockIsNotBookable) as error:
            validation.check_stock_is_bookable(stock)
        assert error.value.errors == {"stock": ["Ce stock n'est pas réservable"]}


@pytest.mark.usefixtures("db_session")
class CheckExpenseLimitsTest:
    def test_physical_limit(self):
        offer = offers_factories.OfferFactory(product__type=str(ThingType.AUDIOVISUEL))
        expenses = {
            "all": {"max": 500, "actual": 200},
            "physical": {"max": 200, "actual": 0},
            "digital": {"max": 300, "actual": 0},
        }

        validation.check_expenses_limits(expenses, 11, offer)  # should not raise

        expenses["physical"]["actual"] = 190

        with pytest.raises(exceptions.PhysicalExpenseLimitHasBeenReached) as error:
            validation.check_expenses_limits(expenses, 11, offer)
        assert error.value.errors["global"] == [
            "Le plafond de 200 € pour les biens culturels ne vous permet pas de réserver cette offre."
        ]

    def test_digital_limit(self):
        offer = offers_factories.OfferFactory(
            product__type=str(ThingType.JEUX_VIDEO),
            product__url="http://www.example.com/my-game",
        )
        expenses = {
            "all": {"max": 500, "actual": 200},
            "physical": {"max": 300, "actual": 0},
            "digital": {"max": 200, "actual": 0},
        }

        validation.check_expenses_limits(expenses, 11, offer)  # should not raise

        expenses["digital"]["actual"] = 190

        with pytest.raises(exceptions.DigitalExpenseLimitHasBeenReached) as error:
            validation.check_expenses_limits(expenses, 11, offer)
        assert error.value.errors["global"] == [
            "Le plafond de 200 € pour les offres numériques ne vous permet pas de réserver cette offre."
        ]

    def test_global_limit(self):
        expenses = {
            "all": {"max": 500, "actual": 0},
            "physical": {"max": 300, "actual": 0},
            "digital": {"max": 200, "actual": 0},
        }
        offer = offers_factories.OfferFactory()

        validation.check_expenses_limits(expenses, 11, offer)  # should not raise

        expenses["all"]["actual"] = 490

        with pytest.raises(exceptions.UserHasInsufficientFunds) as error:
            validation.check_expenses_limits(expenses, 11, offer)
        assert error.value.errors["insufficientFunds"] == [
            "Le solde de votre pass est insuffisant pour réserver cette offre."
        ]


@pytest.mark.usefixtures("db_session")
class CheckIsUsableTest:
    def should_raise_if_used(self):
        booking = factories.BookingFactory(isUsed=True)
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_is_usable(booking)
        assert exc.value.errors["booking"] == ["Cette réservation a déjà été validée"]

    def should_raise_if_cancelled(self):
        booking = factories.BookingFactory(isCancelled=True)
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_is_usable(booking)
        assert exc.value.errors["booking"] == ["Cette réservation a été annulée"]

    def should_pass_if_no_beginning_datetime(self):
        booking = factories.BookingFactory(stock__beginningDatetime=None)
        validation.check_is_usable(booking)

    def should_pass_when_event_begins_in_less_than_72_hours(self):
        soon = datetime.utcnow() + timedelta(hours=72)
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
            "Cette réservation a été effectuée le 14/10/2020 à 09:00. Veuillez "
            "attendre jusqu’au 16/10/2020 à 09:00 pour valider la contremarque."
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
        booking = factories.BookingFactory(isUsed=True)
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
            "réservée et moins de 72h avant le début de l'événement"
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
            "réservée et moins de 72h avant le début de l'événement"
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
            "réservée et moins de 72h avant le début de l'événement"
        ]


# TODO(fseguin, 2020-11-09): cleanup when all past event bookings have a confirmationDate
@pytest.mark.usefixtures("db_session")
class CheckBeneficiaryCanCancelBookingNoConfirmationDateTest:
    def test_can_cancel(self):
        booking = factories.BookingFactory()
        booking.confirmationDate = None
        db.session.add(booking)
        db.session.commit()
        validation.check_beneficiary_can_cancel_booking(booking.user, booking)  # should not raise

    def test_can_cancel_if_event_is_in_a_long_time(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=10),
        )
        booking.confirmationDate = None
        db.session.add(booking)
        db.session.commit()
        validation.check_beneficiary_can_cancel_booking(booking.user, booking)  # should not raise

    def test_raise_if_not_the_beneficiary(self):
        booking = factories.BookingFactory()
        other_user = users_factories.UserFactory()
        with pytest.raises(exceptions.BookingDoesntExist):
            validation.check_beneficiary_can_cancel_booking(other_user, booking)

    def test_raise_if_already_used(self):
        booking = factories.BookingFactory(isUsed=True)
        booking.confirmationDate = None
        db.session.add(booking)
        db.session.commit()
        with pytest.raises(exceptions.BookingIsAlreadyUsed):
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)

    def test_raise_if_event_too_close(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=1),
        )
        booking.confirmationDate = None
        db.session.add(booking)
        db.session.commit()
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 72h avant le début de l'événement"
        ]

    def test_raise_if_booked_long_ago(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=10),
            dateCreated=datetime.utcnow() - timedelta(days=2),
        )
        booking.confirmationDate = None
        db.session.add(booking)
        db.session.commit()
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 72h avant le début de l'événement"
        ]

    def test_raise_if_event_too_close_and_booked_long_ago(self):
        booking = factories.BookingFactory(
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=1),
            dateCreated=datetime.utcnow() - timedelta(days=2),
        )
        booking.confirmationDate = None
        db.session.add(booking)
        db.session.commit()
        with pytest.raises(exceptions.CannotCancelConfirmedBooking) as exc:
            validation.check_beneficiary_can_cancel_booking(booking.user, booking)
        assert exc.value.errors["booking"] == [
            "Impossible d'annuler une réservation plus de 48h après l'avoir "
            "réservée et moins de 72h avant le début de l'événement"
        ]


@pytest.mark.usefixtures("db_session")
class CheckOffererCanCancelBookingTest:
    def test_can_cancel(self):
        booking = factories.BookingFactory()
        validation.check_offerer_can_cancel_booking(booking)  # should not raise

    def test_raise_if_already_cancelled(self):
        booking = factories.BookingFactory(isCancelled=True)
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_offerer_can_cancel_booking(booking)
        assert exc.value.errors["global"] == ["Cette contremarque a déjà été annulée"]

    def test_raise_if_already_used(self):
        booking = factories.BookingFactory(isUsed=True)
        with pytest.raises(api_errors.ForbiddenError) as exc:
            validation.check_offerer_can_cancel_booking(booking)
        assert exc.value.errors["global"] == ["Impossible d'annuler une réservation consommée"]


@pytest.mark.usefixtures("db_session")
class CheckActivationBookingCanBeKeptTest:
    def test_should_raise_an_error_when_booking_has_an_event_activation_type(self):
        booking = factories.BookingFactory(stock__offer__type=str(EventType.ACTIVATION))
        with pytest.raises(ApiErrors) as exc:
            validation.check_is_not_activation_booking(booking)
        assert exc.value.errors["booking"] == ["Impossible d'annuler une offre d'activation"]

    def test_should_raise_an_error_when_booking_has_a_thing_activation_type(self):
        booking = factories.BookingFactory(stock__offer__type=str(EventType.ACTIVATION))
        with pytest.raises(ApiErrors) as exc:
            validation.check_is_not_activation_booking(booking)
        assert exc.value.errors["booking"] == ["Impossible d'annuler une offre d'activation"]

    def test_should_not_raise_when_booking_is_not_an_activation(self):
        booking = factories.BookingFactory(stock__offer__type=str(EventType.JEUX))
        validation.check_is_not_activation_booking(booking)  # should not raise


@pytest.mark.usefixtures("db_session")
class CheckCanBeMarkAsUnused:
    def test_raises_resource_gone_error_if_not_used(self, app):
        booking = factories.BookingFactory(isUsed=False)
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_can_be_mark_as_unused(booking)
        assert exc.value.errors["booking"] == ["Cette réservation n'a pas encore été validée"]

    def test_raises_resource_gone_error_if_validated_and_cancelled(self, app):
        booking = factories.BookingFactory(isUsed=True, isCancelled=True)
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_can_be_mark_as_unused(booking)
        assert exc.value.errors["booking"] == ["Cette réservation a été annulée"]

    def test_raises_resource_gone_error_if_payement_exists(self, app):
        booking = factories.BookingFactory(isUsed=True)
        payments_factories.PaymentFactory(booking=booking)
        with pytest.raises(api_errors.ResourceGoneError) as exc:
            validation.check_can_be_mark_as_unused(booking)
        assert exc.value.errors["payment"] == ["Le remboursement est en cours de traitement"]

    def test_dont_raise_if_stock_beginning_datetime_in_more_than_72_hours(self):
        booking = factories.BookingFactory(
            isUsed=True,
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=4),
        )
        validation.check_booking_token_is_keepable(booking)  # should not raise

    def test_dont_raise_if_stock_beginning_datetime_in_less_than_72_hours(self):
        booking = factories.BookingFactory(
            isUsed=True,
            stock__beginningDatetime=datetime.utcnow() + timedelta(days=2),
        )
        validation.check_booking_token_is_keepable(booking)  # should not raise

    def test_does_not_raise_error_if_not_cancelled_but_used_and_no_beginning_datetime(self):
        booking = factories.BookingFactory(
            isUsed=True,
            stock__beginningDatetime=None,
        )
        validation.check_booking_token_is_keepable(booking)  # should not raise
