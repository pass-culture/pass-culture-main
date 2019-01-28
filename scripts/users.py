import csv
import re
from datetime import datetime
from typing import List

from domain.password import generate_reset_token
from models import User, Booking, Stock, PcObject
from repository.stock_queries import find_online_activation_stock
from repository.user_queries import find_user_by_email
from utils.logger import logger
from utils.token import random_token

CHUNK_SIZE = 500
THIRTY_DAYS = 30 * 24


def setup_users(csv_rows: List[List[str]], stock: Stock, find_user_query=find_user_by_email) -> List[Booking]:
    bookings = []

    for row in csv_rows:
        existing_user = find_user_query(row[3])
        filled_user = fill_user_from(row, existing_user)
        booking = create_activation_booking_for(filled_user, stock)
        bookings.append(booking)

    return bookings


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


def fill_user_from(csv_row: List[str], user: User) -> User:
    if user is None:
        user = User()
    print(csv_row)
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


def run(csv_file_path: str) -> None:
    logger.info('[START] Création des utilisateurs avec contremarques d\'activation')

    csv_reader = csv.reader(open(csv_file_path))

    chunk = []
    total = 0
    stock = find_online_activation_stock()

    if not stock:
        logger.error('No activation stock found')
    else:
        for line in csv_reader:
            if (line[0] == 'id'):
                continue

            chunk.append(line)

            if len(chunk) >= CHUNK_SIZE or not next(csv_reader):
                bookings = setup_users(chunk, stock)
                PcObject.check_and_save(*bookings)
                logger.info('Enregistrement de 500 comptes utilisateur')
                total += len(chunk)
                chunk = []

    logger.info('[END] Création des utilisateurs avec contremarques d\'activation : %s' % total)

run('data.csv')