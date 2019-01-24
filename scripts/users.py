import re
from datetime import datetime
from typing import List

from domain.password import generate_reset_token
from models import User, Booking, Stock
from utils.token import random_token

THIRTY_DAYS = 30 * 24


def create_activation_booking_for(user: User, stock: Stock) -> Booking:
    booking = Booking()
    booking.stock = stock
    booking.user = user
    booking.quantity = 1
    booking.dateCreated = datetime.utcnow()
    booking.isCancelled = False
    booking.isUsed = False
    booking.token = random_token()
    return booking


def fill_user_from(csv_row: List[str], user: User = None) -> User:
    if user is None:
        user = User()

    user.lastName = csv_row[1]
    user.firstName = csv_row[2]
    user.email = csv_row[3]
    user.phoneNumber = csv_row[4]
    user.departementCode = re.search('\((.*?)\)$', csv_row[5]).group()[1:-1]
    user.postalCode = csv_row[6]
    user.canBookFreeOffers = False
    user.password = ''
    generate_reset_token(user, validity_duration_hours=THIRTY_DAYS)

    return user
