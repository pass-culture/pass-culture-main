from typing import Callable, Dict

from domain.expenses import is_eligible_to_physical_offers_capping, is_eligible_to_digital_offers_capping
from models import Offer, Booking, ApiErrors
from models.stock import Stock
from models.user import User
from repository import booking_queries, stock_queries


def check_offer_already_booked(offer: Offer, user: User):
    is_offer_already_booked_by_user = booking_queries.is_offer_already_booked_by_user(user, offer)
    if is_offer_already_booked_by_user:
        offer_is_already_booked = OfferIsAlreadyBooked()
        offer_is_already_booked.add_error('offerId', "Cette offre a déja été reservée par l'utilisateur")
        raise offer_is_already_booked


def check_existing_stock(stock: Stock) -> None:
    if stock is None:
        stock_id_doesnt_exist = StockIdDoesntExist()
        stock_id_doesnt_exist.add_error('stockId', 'stockId ne correspond à aucun stock')
        raise stock_id_doesnt_exist


def check_quantity_is_valid(quantity: int, stock: Stock) -> None:
    offer_is_duo = stock.offer.isDuo
    is_valid_quantity_for_duo_offer = (quantity in (1, 2) and offer_is_duo)
    is_valid_quantity_for_solo_offer = (quantity == 1 and not offer_is_duo)

    if not is_valid_quantity_for_duo_offer and not is_valid_quantity_for_solo_offer:
        quantity_is_invalid = QuantityIsInvalid()
        quantity_is_invalid.add_error('quantity', "Vous devez réserver une place ou deux dans le cas d'une offre DUO.")
        raise quantity_is_invalid


def check_stock_is_bookable(stock: Stock):
    if not stock.isBookable:
        stock_is_not_bookable = StockIsNotBookable()
        stock_is_not_bookable.add_error('stock', "Ce stock n'est pas réservable")
        raise stock_is_not_bookable


def check_expenses_limits(expenses: Dict, booking: Booking,
                          find_stock: Callable[..., Stock] = stock_queries.find_stock_by_id) -> None:
    stock = find_stock(booking.stockId)
    offer = stock.offer

    expense_limit_has_been_reached = ExpenseLimitHasBeenReached()

    if is_eligible_to_physical_offers_capping(offer):
        if (expenses['physical']['actual'] + booking.value) > expenses['physical']['max']:
            expense_limit_has_been_reached.add_error(
                'global',
                'Le plafond de %s € pour les biens culturels ne vous permet pas ' \
                'de réserver cette offre.' % expenses['physical']['max']
            )
            raise expense_limit_has_been_reached

    if is_eligible_to_digital_offers_capping(offer):
        if (expenses['digital']['actual'] + booking.value) > expenses['digital']['max']:
            expense_limit_has_been_reached.add_error(
                'global',
                'Le plafond de %s € pour les offres numériques ne vous permet pas ' \
                'de réserver cette offre.' % expenses['digital']['max']
            )
        raise expense_limit_has_been_reached


def check_can_book_free_offer(stock: Stock, user: User):
    if not user.canBookFreeOffers and stock.price == 0:
        cannot_book_free_offers_errors = CannotBookFreeOffers()
        cannot_book_free_offers_errors.add_error('cannotBookFreeOffers',
                             'Votre compte ne vous permet pas de faire de réservation.')
        raise cannot_book_free_offers_errors


class ClientError(Exception):
    def __init__(self, errors: dict = None):
        self.errors = errors if errors else {}

    def add_error(self, field, error):
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]


class OfferIsAlreadyBooked(ClientError):
    pass


class StockIdDoesntExist(ClientError):
    pass


class QuantityIsInvalid(ClientError):
    pass


class StockIsNotBookable(ClientError):
    pass


class ExpenseLimitHasBeenReached(ClientError):
    pass


class CannotBookFreeOffers(ClientError):
    pass
