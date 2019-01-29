import csv
import re
from datetime import datetime
from typing import List, Set, Iterable

from domain.password import generate_reset_token
from models import User, Booking, Stock, PcObject
from repository.stock_queries import find_online_activation_stock
from repository.user_queries import find_user_by_email
from utils.logger import logger
from utils.token import random_token

CHUNK_SIZE = 250
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
    user.dateOfBirth = datetime.strptime(csv_row[7], "%Y-%m-%d")
    user.email = csv_row[3]
    user.phoneNumber = ''.join(filter(lambda d: d in '+1234567890', csv_row[4]))
    user.departementCode = re.search('\((.*?)\)$', csv_row[5]).group()[1:-1]
    user.postalCode = csv_row[6]
    user.canBookFreeOffers = False
    user.password = random_token(length=12).encode('utf-8')
    generate_reset_token(user, validity_duration_hours=THIRTY_DAYS)

    return user


def chunk_file(csv_reader: Iterable, chunk_size: int) -> List[List[List[str]]]:
    chunked_rows = []
    chunk = []
    existing_emails = set()
    total = 0

    for line in csv_reader:
        if line[0] == 'id':
            continue

        if line[3] not in existing_emails:
            chunk.append(line)
            existing_emails.add(line[3])

        if len(chunk) >= chunk_size:
            chunked_rows.append(chunk)
            total += len(chunk)
            chunk = []

    total += len(chunk)
    chunked_rows.append(chunk)
    logger.info('Lecture des lignes CSV (%s) terminée\n' % total)

    return chunked_rows


def run(csv_file_path: str) -> None:
    logger.info('-------------------------------------------------------------------------------')
    logger.info('[START] Création des utilisateurs avec contremarques d\'activation')
    logger.info('-------------------------------------------------------------------------------\n')

    stock = find_online_activation_stock()
    if not stock:
        logger.error('No activation stock found')
        exit(1)

    logger.info('[STEP 1] Lecture du fichier CSV')
    csv_file = open(csv_file_path)
    csv_reader = csv.reader(csv_file)
    chunked_file = chunk_file(csv_reader, CHUNK_SIZE)

    logger.info('[STEP 2] Enregistrement des comptes et contremarques d\'activation')
    existing_tokens = set()
    total = 0
    for chunk in chunked_file:
        bookings = setup_users(chunk, stock, existing_tokens)
        PcObject.check_and_save(*bookings)
        total += len(chunk)
        logger.info('Enregistrement de %s comptes utilisateur | %s' % (CHUNK_SIZE, total))
    logger.info('Enregistrement des comptes utilisateur terminé\n')

    logger.info('[STEP 3] Compte des objets')
    logger.info('Users créés -> %s' % total)
    logger.info('Users en BDD -> %s' % User.query.count())
    logger.info('Bookings créés -> %s' % len(existing_tokens))
    logger.info('Bookings en BDD -> %s\n' % Booking.query.count())

    logger.info('-------------------------------------------------------------------------------')
    logger.info('[END] Création des utilisateurs avec contremarques d\'activation : %s' % total)
    logger.info('-------------------------------------------------------------------------------')
