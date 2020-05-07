from typing import Dict, Callable

from domain.booking.booking import Booking
from domain.booking.booking_exceptions import StockIsNotBookable, UserHasInsufficientFunds, \
    PhysicalExpenseLimitHasBeenReached, DigitalExpenseLimitHasBeenReached, CannotBookFreeOffers
from domain.expenses import is_eligible_to_physical_offers_capping, is_eligible_to_digital_offers_capping
from domain.stock.stock import Stock
from domain.stock.stock_exceptions import StockDoesntExist
from domain.user.user import User
from repository import stock_queries


def check_existing_stock(stock: Stock) -> None:
    if stock is None:
        stock_id_doesnt_exist = StockDoesntExist()
        raise stock_id_doesnt_exist


def check_stock_is_bookable(stock: Stock):
    if not stock.is_bookable():
        stock_is_not_bookable = StockIsNotBookable()
        raise stock_is_not_bookable


def check_expenses_limits(expenses: Dict, booking: Booking) -> None:
    stock = booking.stock
    offer = stock.offer

    if (expenses['all']['actual'] + booking.total_amount()) > expenses['all']['max']:
        raise UserHasInsufficientFunds()

    if is_eligible_to_physical_offers_capping(offer):
        if (expenses['physical']['actual'] + booking.total_amount()) > expenses['physical']['max']:
            raise PhysicalExpenseLimitHasBeenReached(expenses['physical']['max'])

    if is_eligible_to_digital_offers_capping(offer):
        if (expenses['digital']['actual'] + booking.total_amount()) > expenses['digital']['max']:
            raise DigitalExpenseLimitHasBeenReached(expenses['digital']['max'])


def check_can_book_free_offer(user: User, stock: Stock):
    if not user.can_book_free_offers and stock.price == 0:
        raise CannotBookFreeOffers()
