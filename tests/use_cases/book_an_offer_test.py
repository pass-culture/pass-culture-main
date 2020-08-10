from unittest.mock import MagicMock

import pytest

from domain.booking.booking import Booking
from domain.booking.booking_exceptions import OfferIsAlreadyBooked, CannotBookFreeOffers, StockIsNotBookable, \
    UserHasInsufficientFunds, PhysicalExpenseLimitHasBeenReached, QuantityIsInvalid
from domain.stock.stock import Stock
from domain.stock.stock_exceptions import StockDoesntExist
from infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService
from repository import repository
from infrastructure.repository.booking.booking_sql_repository import BookingSQLRepository
from infrastructure.repository.stock.stock_sql_repository import StockSQLRepository
from infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from tests.conftest import clean_database
from tests.domain_creators.generic_creators import create_domain_beneficiary
from tests.model_creators.generic_creators import create_user, create_deposit, create_offerer, create_venue, \
    create_booking, create_stock, create_recommendation
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from use_cases.book_an_offer import BookAnOffer, BookingInformation


class BookAnOfferTest:
    def setup_method(self):
        self.booking_repository = BookingSQLRepository()
        self.booking_repository.save = MagicMock()
        self.stock_repository = StockSQLRepository()
        self.user_repository = BeneficiarySQLRepository()
        self.stock_repository.find_stock_by_id = MagicMock()
        self.user_repository.find_user_by_id = MagicMock()
        self.notification_service = MailjetNotificationService()
        self.notification_service.send_booking_recap = MagicMock()
        self.notification_service.send_booking_confirmation_to_beneficiary = MagicMock()
        self.book_an_offer = BookAnOffer(booking_repository=self.booking_repository,
                                         user_repository=self.user_repository,
                                         stock_repository=self.stock_repository,
                                         notification_service=self.notification_service)

    @clean_database
    def test_user_can_book_an_offer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=50, quantity=1)
        create_deposit(user, amount=50)
        repository.save(user, stock)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            stock.quantity
        )
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            offer=offer,
            price=50
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock

        # When
        self.book_an_offer.execute(booking_information=booking_information)

        # Then
        self.booking_repository.save.assert_called_once()
        saved_booking = self.booking_repository.save.call_args[0][0]
        assert saved_booking.stock.identifier == booking_information.stock_id
        assert saved_booking.beneficiary.identifier == booking_information.user_id
        assert saved_booking.quantity == booking_information.quantity

    @clean_database
    def test_send_a_booking_recap_email(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=50, quantity=1)
        create_deposit(user, amount=50)
        repository.save(user, stock)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            stock.quantity
        )
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            offer=offer,
            price=50
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        saved_booking = Booking(beneficiary=user, stock=stock, amount=0, quantity=1)
        self.booking_repository.save.return_value = saved_booking

        # When
        self.book_an_offer.execute(booking_information=booking_information)

        # Then
        self.notification_service.send_booking_recap.assert_called_once_with(saved_booking)

    @clean_database
    def test_send_booking_confirmation_email_to_beneficiary(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        create_deposit(user)
        repository.save(user, stock)

        booking_information = BookingInformation(
            stock_id=stock.id,
            user_id=user.id,
            quantity=1
        )
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            offer=offer,
            price=50
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        saved_booking = Booking(beneficiary=user, stock=stock, amount=0, quantity=1)
        self.booking_repository.save.return_value = saved_booking

        # When
        self.book_an_offer.execute(booking_information=booking_information)

        # Then
        self.notification_service.send_booking_confirmation_to_beneficiary.assert_called_once_with(saved_booking)

    @clean_database
    def test_return_saved_booking(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=50, quantity=1)
        create_deposit(user)
        repository.save(user, stock)

        booking_information = BookingInformation(
            stock.id,
            user.id,
            stock.quantity
        )
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            offer=offer,
            price=50)
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        saved_booking = Booking(beneficiary=user, stock=stock, amount=0, quantity=1)
        self.booking_repository.save.return_value = saved_booking

        # When
        booking = self.book_an_offer.execute(booking_information=booking_information)

        # Then
        assert booking == saved_booking

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
        self.stock_repository.find_stock_by_id.side_effect = StockDoesntExist()

        booking_information = BookingInformation(
            non_existing_stock_id,
            user.id,
            booking.quantity,
            None
        )

        # When
        with pytest.raises(StockDoesntExist) as error:
            self.book_an_offer.execute(booking_information=booking_information)

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
        expected_stock = Stock(
            identifier=stock2.id,
            quantity=1,
            price=50,
            offer=offer
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user

        booking_information = BookingInformation(
            stock2.id,
            user.id,
            booking.quantity,
            None
        )

        # When
        with pytest.raises(OfferIsAlreadyBooked) as error:
            self.book_an_offer.execute(booking_information=booking_information)

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
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            price=0,
            offer=offer
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1,
            recommendation.id
        )

        # When
        with pytest.raises(CannotBookFreeOffers) as error:
            self.book_an_offer.execute(booking_information=booking_information)

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
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            price=50,
            offer=thing_offer
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1
        )

        # When
        with pytest.raises(StockIsNotBookable) as error:
            self.book_an_offer.execute(booking_information=booking_information)

        # Then
        assert error.value.errors == {'stock': ["Ce stock n'est pas réservable"]}

    @clean_database
    def test_should_return_failure_when_user_has_not_enough_credit(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=600)
        repository.save(user, stock)
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            price=600,
            offer=offer
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1
        )

        # When
        with pytest.raises(UserHasInsufficientFunds) as error:
            self.book_an_offer.execute(booking_information=booking_information)

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
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            price=12,
            offer=offer2
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user

        booking_information = BookingInformation(
            stock.id,
            user.id,
            1
        )

        # When
        with pytest.raises(PhysicalExpenseLimitHasBeenReached) as error:
            self.book_an_offer.execute(booking_information=booking_information)

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
        expected_stock = Stock(
            identifier=stock.id,
            quantity=1,
            price=50,
            offer=offer
        )
        self.stock_repository.find_stock_by_id.return_value = expected_stock
        expected_user = create_domain_beneficiary(
            identifier=user.id,
            can_book_free_offers=user.canBookFreeOffers
        )
        self.user_repository.find_user_by_id.return_value = expected_user

        booking_information = BookingInformation(
            stock.id,
            user.id,
            -3
        )

        # When
        with pytest.raises(QuantityIsInvalid) as error:
            self.book_an_offer.execute(booking_information=booking_information)

        # Then
        assert error.value.errors == {
            'quantity': ["Vous devez réserver une place ou deux dans le cas d'une offre DUO."]
        }
