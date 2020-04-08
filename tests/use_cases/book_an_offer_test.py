import pytest

from domain.booking import StockDoesntExist, OfferIsAlreadyBooked, CannotBookFreeOffers, StockIsNotBookable, \
    UserHasInsufficientFunds, PhysicalExpenseLimitHasBeenReached, QuantityIsInvalid
from models import Booking
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_deposit, create_offerer, create_venue, \
    create_booking, create_stock, create_recommendation
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from use_cases.book_an_offer import book_an_offer, BookingInformation


class BookAnOfferTest:
    @clean_database
    def test_user_can_book_an_offer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=50, quantity=1, offer=offer)
        create_booking(user=user, stock=stock, venue=venue, is_cancelled=True)
        create_deposit(user, amount=50)
        repository.save(user, stock)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1
        )

        # When
        booking = book_an_offer(booking_information)

        # Then
        assert booking == Booking.query.filter(Booking.isCancelled == False).one()

    @clean_database
    def test_should_return_failure_when_stock_id_does_not_match_any_existing_stock(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        booking = create_booking(user=user, stock=stock, is_cancelled=False)
        create_deposit(user)
        repository.save(booking, user)
        non_existing_stock_id = 666

        booking_information = BookingInformation(
            non_existing_stock_id,
            user.id,
            booking.quantity,
            None
        )

        # When
        with pytest.raises(StockDoesntExist) as error:
            book_an_offer(booking_information)

        # Then
        assert error.value.errors == {'stockId': ["stockId ne correspond à aucun stock"]}

    @clean_database
    def test_should_return_failure_when_offer_already_booked_by_user(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        booking = create_booking(user=user, stock=stock1, is_cancelled=False)
        create_deposit(user)
        repository.save(stock2, booking)

        booking_information = BookingInformation(
            stock2.id,
            user.id,
            booking.quantity,
            None
        )

        # When
        with pytest.raises(OfferIsAlreadyBooked) as error:
            book_an_offer(booking_information)

        # Then
        assert error.value.errors == {'offerId': ["Cette offre a déja été reservée par l'utilisateur"]}

    @clean_database
    def test_should_return_failure_when_user_cannot_book_free_offers_and_offer_is_free(self, app):
        # Given
        user = create_user(can_book_free_offers=False)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        recommendation = create_recommendation(offer, user)
        repository.save(stock, recommendation)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1,
            recommendation.id
        )

        # When
        with pytest.raises(CannotBookFreeOffers) as error:
            book_an_offer(booking_information)

        # Then
        assert error.value.errors == {'cannotBookFreeOffers': ["Votre compte ne vous permet"
                                                               " pas de faire de réservation."]}

    @clean_database
    def test_should_return_failure_when_stock_is_not_bookable(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_offer = create_offer_with_thing_product(venue, is_active=False)
        stock = create_stock(offer=thing_offer)
        repository.save(stock, user)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1
        )

        # When
        with pytest.raises(StockIsNotBookable) as error:
            book_an_offer(booking_information)

        # Then
        assert error.value.errors == {'stock': ["Ce stock n'est pas réservable"]}

    @clean_database
    def test_should_return_failure_when_user_has_not_enough_credit(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=600, offer=offer)
        repository.save(user, stock)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1
        )

        # When
        with pytest.raises(UserHasInsufficientFunds) as error:
            book_an_offer(booking_information)

        # Then
        assert error.value.errors == \
               {'insufficientFunds':
                   [
                       'Le solde de votre pass est insuffisant'
                       ' pour réserver cette offre.']
               }

    @clean_database
    def test_should_return_failure_when_public_credit_and_limit_of_physical_thing_reached(self, app):
        # Given
        user = create_user()
        create_deposit(user)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        booked_stock = create_stock(offer=offer, price=190)
        booking = create_booking(user=user, stock=booked_stock)
        stock = create_stock(offer=offer2, price=12)
        repository.save(booking, stock)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1
        )

        # When
        with pytest.raises(PhysicalExpenseLimitHasBeenReached) as error:
            book_an_offer(booking_information)

        # Then
        assert error.value.errors == \
               {'global':
                   [
                       'Le plafond de 200 € pour les biens culturels'
                       ' ne vous permet pas de réserver cette offre.'
                   ]
               }

    @clean_database
    def test_should_return_failure_when_quantity_is_not_valid_for_duo_offer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, is_duo=True)
        stock = create_stock(offer=offer)
        repository.save(stock, user)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            -3
        )

        # When
        with pytest.raises(QuantityIsInvalid) as error:
            book_an_offer(booking_information)

        # Then
        assert error.value.errors == {'quantity':
            [
                "Vous devez réserver une place ou deux dans le cas d'une offre DUO."]}
