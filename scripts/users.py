import csv
import re
from datetime import datetime
from typing import List, Set

from domain.password import generate_reset_token
from models import User, Booking, Stock, PcObject
from repository.stock_queries import find_online_activation_stock
from repository.user_queries import find_user_by_email
from utils.logger import logger
from utils.token import random_token

CHUNK_SIZE = 100
THIRTY_DAYS = 30 * 24


def setup_users(csv_rows: List[List[str]], stock: Stock, existing_tokens: Set[str],
                find_user_query=find_user_by_email) -> List[Booking]:
    bookings = []

    for row in csv_rows:
        user = find_user_query(row[3])
        if not user:
            user = User()

        filled_user = fill_user_from(row, user)

        token = random_token()
        while token in existing_tokens:
            token = random_token()
        existing_tokens.add(token)

        booking = create_activation_booking_for(filled_user, stock, token)
        bookings.append(booking)

    return bookings


def create_activation_booking_for(user: User, stock: Stock, token: str) -> Booking:
    booking = Booking()
    booking.stock = stock
    booking.user = user
    booking.quantity = 1
    booking.amount = 0
    booking.dateCreated = datetime.utcnow()
    booking.isCancelled = False
    booking.isUsed = False
    booking.token = token
    return booking


def fill_user_from(csv_row: List[str], user: User) -> User:
    user.lastName = csv_row[1]
    user.firstName = csv_row[2].split(' ')[0]
    user.publicName = '%s %s.' % (user.firstName, csv_row[1][:1].upper())
    user.email = csv_row[3]
    user.phoneNumber = ''.join(filter(lambda d: d in '+1234567890', csv_row[4]))
    user.departementCode = re.search('\((.*?)\)$', csv_row[5]).group()[1:-1]
    user.postalCode = csv_row[6]
    user.canBookFreeOffers = False
    user.password = random_token(length=12).encode('utf-8')
    generate_reset_token(user, validity_duration_hours=THIRTY_DAYS)

    return user


def run(csv_file_path: str) -> None:
    logger.info('[START] Création des utilisateurs avec contremarques d\'activation')

    csv_reader = csv.reader(open(csv_file_path))
    chunk = []
    total = 0
    stock = find_online_activation_stock()
    existing_tokens = set()

    if not stock:
        logger.error('No activation stock found')
    else:
        for line in csv_reader:
            if line[0] == 'id':
                continue

            chunk.append(line)

            if len(chunk) >= CHUNK_SIZE:
                save_in_database(chunk, stock, total, existing_tokens)
                total += len(chunk)
                chunk = []

        total += len(chunk)
        save_in_database(chunk, stock, total, existing_tokens)

    logger.info('[END] Création des utilisateurs avec contremarques d\'activation : %s' % total)


def save_in_database(chunk, stock, total, existing_tokens):
    bookings = setup_users(chunk, stock, existing_tokens)
    PcObject.check_and_save(*bookings)
    logger.info('Enregistrement de %s comptes utilisateur | %s' % (CHUNK_SIZE, total))
