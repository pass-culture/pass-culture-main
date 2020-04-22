from typing import Callable, Dict

from domain.expenses import is_eligible_to_physical_offers_capping, is_eligible_to_digital_offers_capping
from models import Offer, Booking
from models.stock import Stock
from models.user import User
from repository import booking_queries, stock_queries


def check_offer_already_booked(offer: Offer, user: User):
    is_offer_already_booked_by_user = booking_queries.is_offer_already_booked_by_user(user, offer)
    if is_offer_already_booked_by_user:
        offer_is_already_booked = OfferIsAlreadyBooked('offerId', "Cette offre a déja été reservée par l'utilisateur")
        raise offer_is_already_booked


def check_existing_stock(stock: Stock) -> None:
    if stock is None:
        stock_id_doesnt_exist = StockDoesntExist('stockId', 'stockId ne correspond à aucun stock')
        raise stock_id_doesnt_exist


def check_quantity_is_valid(quantity: int, offer_is_duo: bool) -> None:
    if offer_is_duo and quantity not in (1, 2):
        quantity_is_invalid = QuantityIsInvalid('quantity',
                                                "Vous devez réserver une place ou deux dans le cas d'une offre DUO.")
        raise quantity_is_invalid

    if not offer_is_duo and quantity != 1:
        quantity_is_invalid = QuantityIsInvalid('quantity', "Vous ne pouvez réserver qu'une place pour cette offre.")
        raise quantity_is_invalid


def check_stock_is_bookable(stock: Stock):
    if not stock.isBookable:
        stock_is_not_bookable = StockIsNotBookable('stock', "Ce stock n'est pas réservable")
        raise stock_is_not_bookable


def check_expenses_limits(expenses: Dict, booking: Booking,
                          find_stock: Callable[..., Stock] = stock_queries.find_stock_by_id) -> None:
    stock = find_stock(booking.stockId)
    offer = stock.offer

    if (expenses['all']['actual'] + booking.value) > expenses['all']['max']:
        raise UserHasInsufficientFunds('insufficientFunds',
                                       'Le solde de votre pass est insuffisant pour réserver cette offre.')

    if is_eligible_to_physical_offers_capping(offer):
        if (expenses['physical']['actual'] + booking.value) > expenses['physical']['max']:
            raise PhysicalExpenseLimitHasBeenReached(
                'global',
                f"Le plafond de {expenses['physical']['max']} € pour les biens culturels ne vous permet pas " \
                "de réserver cette offre."
            )

    if is_eligible_to_digital_offers_capping(offer):
        if (expenses['digital']['actual'] + booking.value) > expenses['digital']['max']:
            raise DigitalExpenseLimitHasBeenReached(
                'global',
                f"Le plafond de {expenses['digital']['max']} € pour les offres numériques ne vous permet pas " \
                "de réserver cette offre."
            )


def check_can_book_free_offer(user: User, stock: Stock):
    if not user.canBookFreeOffers and stock.price == 0:
        raise CannotBookFreeOffers('cannotBookFreeOffers',
                                   'Votre compte ne vous permet pas de faire de réservation.')


class ClientError(Exception):
    def __init__(self, field: str, error: str):
        self.errors = {field: [error]}

    def add_error(self, field, error):
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]


class OfferIsAlreadyBooked(ClientError):
    pass


class StockDoesntExist(ClientError):
    pass


class QuantityIsInvalid(ClientError):
    pass


class StockIsNotBookable(ClientError):
    pass


class PhysicalExpenseLimitHasBeenReached(ClientError):
    pass


class DigitalExpenseLimitHasBeenReached(ClientError):
    pass


class CannotBookFreeOffers(ClientError):
    pass


class UserHasInsufficientFunds(ClientError):
    pass
