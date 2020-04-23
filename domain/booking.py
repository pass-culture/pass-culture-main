from typing import Callable, Dict

from domain.expenses import is_eligible_to_physical_offers_capping, is_eligible_to_digital_offers_capping
from domain.stock.stock import Stock
from domain.stock.stock_exceptions import StockDoesntExist
from models import Offer, Booking
from models.user import UserSQLEntity
from repository import booking_queries, stock_queries


def check_offer_already_booked(offer: Offer, user: UserSQLEntity):
    is_offer_already_booked_by_user = booking_queries.is_offer_already_booked_by_user(user, offer)
    if is_offer_already_booked_by_user:
        offer_is_already_booked = OfferIsAlreadyBooked()
        raise offer_is_already_booked


def check_existing_stock(stock: Stock) -> None:
    if stock is None:
        stock_id_doesnt_exist = StockDoesntExist()
        raise stock_id_doesnt_exist


def check_quantity_is_valid(quantity: int, offer_is_duo: bool) -> None:
    if offer_is_duo and quantity not in (1, 2):
        quantity_is_invalid = QuantityIsInvalid("Vous devez réserver une place ou deux dans le cas d'une offre DUO.")
        raise quantity_is_invalid

    if not offer_is_duo and quantity != 1:
        quantity_is_invalid = QuantityIsInvalid("Vous ne pouvez réserver qu'une place pour cette offre.")
        raise quantity_is_invalid


def check_stock_is_bookable(stock: Stock):
    if not stock.is_bookable():
        stock_is_not_bookable = StockIsNotBookable()
        raise stock_is_not_bookable


def check_expenses_limits(expenses: Dict, booking: Booking,
                          find_stock: Callable[..., Stock] = stock_queries.find_stock_by_id) -> None:
    stock = find_stock(booking.stockId)
    offer = stock.offer

    if (expenses['all']['actual'] + booking.value) > expenses['all']['max']:
        raise UserHasInsufficientFunds()

    if is_eligible_to_physical_offers_capping(offer):
        if (expenses['physical']['actual'] + booking.value) > expenses['physical']['max']:
            raise PhysicalExpenseLimitHasBeenReached(expenses['physical']['max'])

    if is_eligible_to_digital_offers_capping(offer):
        if (expenses['digital']['actual'] + booking.value) > expenses['digital']['max']:
            raise DigitalExpenseLimitHasBeenReached(expenses['digital']['max'])


def check_can_book_free_offer(user: UserSQLEntity, stock: Stock):
    if not user.canBookFreeOffers and stock.price == 0:
        raise CannotBookFreeOffers()


class ClientError(Exception):
    def __init__(self, field: str, error: str):
        self.errors = {field: [error]}

    def add_error(self, field, error):
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]


class OfferIsAlreadyBooked(ClientError):
    def __init__(self):
        super().__init__('offerId', "Cette offre a déja été reservée par l'utilisateur")


class QuantityIsInvalid(ClientError):
    def __init__(self, message: str):
        super().__init__('quantity', message)


class StockIsNotBookable(ClientError):
    def __init__(self):
        super().__init__('stock', "Ce stock n'est pas réservable")


class PhysicalExpenseLimitHasBeenReached(ClientError):
    def __init__(self, celling_amount):
        super().__init__(
            'global',
            f"Le plafond de {celling_amount} € pour les biens culturels ne vous permet pas " \
            "de réserver cette offre.")


class DigitalExpenseLimitHasBeenReached(ClientError):
    def __init__(self, celling_amount):
        super().__init__('global',
                         f"Le plafond de {celling_amount} € pour les offres numériques ne vous permet pas " \
                         "de réserver cette offre.")


class CannotBookFreeOffers(ClientError):
    def __init__(self):
        super().__init__('cannotBookFreeOffers', 'Votre compte ne vous permet pas de faire de réservation.')


class UserHasInsufficientFunds(ClientError):
    def __init__(self):
        super().__init__('insufficientFunds', 'Le solde de votre pass est insuffisant pour réserver cette offre.')
