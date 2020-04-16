import csv
import os
import re
from datetime import datetime
from typing import List, Set, Iterable, Callable

import bcrypt

from domain.admin_emails import send_users_activation_report
from domain.password import generate_reset_token, random_password
from domain.user_activation import generate_activation_users_csv
from models import UserSQLEntity, Booking, StockSQLEntity
from models.booking import ActivationUser
from repository import booking_queries, repository
from repository.stock_queries import find_online_activation_stock
from repository.user_queries import find_user_by_email
from scripts.beneficiary import THIRTY_DAYS_IN_HOURS
from scripts.interact import app
from utils.logger import logger
from utils.mailing import MailServiceException, parse_email_addresses, send_raw_email
from utils.token import random_token

LAST_NAME_COLUMN_INDEX = 1
FIRST_NAME_COLUMN_INDEX = 2
EMAIL_COLUMN_INDEX = 3
PHONE_COLUMN_INDEX = 4
DEPARTMENT_COLUMN_INDEX = 5
POSTAL_CODE_COLUMN_INDEX = 6
BIRTHDATE_COLUMN_INDEX = 7
PASSWORD_INDEX = 8

CHUNK_SIZE = 250
ACTIVATION_USER_RECIPIENTS = parse_email_addresses(
    os.environ.get('ACTIVATION_USER_RECIPIENTS', None))


def create_users_with_activation_bookings(
        csv_rows: List[List[str]], stock: StockSQLEntity, existing_tokens: Set[str],
        find_user: Callable = find_user_by_email,
        find_activation_booking: Callable = booking_queries.find_user_activation_booking
) -> List[Booking]:
    bookings = []
    for row in csv_rows:
        user = find_user(row[EMAIL_COLUMN_INDEX])
        if not user:
            user = UserSQLEntity()

        filled_user = fill_user_from(row, user)

        token = random_token()
        while token in existing_tokens:
            token = random_token()

        booking = find_activation_booking(user)
        if not booking:
            booking = create_booking_for(filled_user, stock, token)

        existing_tokens.add(token)
        bookings.append(booking)

    return bookings


def create_booking_for(user: UserSQLEntity, stock: StockSQLEntity, token: str) -> Booking:
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


def fill_user_from(csv_row: List[str], user: UserSQLEntity) -> UserSQLEntity:
    user.lastName = csv_row[LAST_NAME_COLUMN_INDEX]
    user.firstName = csv_row[FIRST_NAME_COLUMN_INDEX].split(' ')[0]
    user.publicName = '%s %s' % (user.firstName, user.lastName)
    user.dateOfBirth = datetime.strptime(
        csv_row[BIRTHDATE_COLUMN_INDEX], "%Y-%m-%d")
    user.email = csv_row[EMAIL_COLUMN_INDEX]
    user.phoneNumber = ''.join(
        filter(lambda d: d in '+1234567890', csv_row[PHONE_COLUMN_INDEX]))
    user.departementCode = _extract_departement_code(
        csv_row[DEPARTMENT_COLUMN_INDEX])
    user.postalCode = csv_row[POSTAL_CODE_COLUMN_INDEX]
    user.canBookFreeOffers = False
    user.password = _get_password(csv_row)
    generate_reset_token(user, validity_duration_hours=THIRTY_DAYS_IN_HOURS)
    return user


def split_rows_in_chunks_with_no_duplicated_emails(csv_reader: Iterable, chunk_size: int) -> List[List[List[str]]]:
    chunked_rows = []
    chunk = []
    existing_emails = set()
    total = 0

    for line in csv_reader:
        if _is_header_or_blank_line(line):
            continue

        email = line[EMAIL_COLUMN_INDEX]

        if email not in existing_emails:
            chunk.append(line)
            existing_emails.add(email)

        if len(chunk) >= chunk_size:
            chunked_rows.append(chunk)
            total += len(chunk)
            chunk = []

    if chunk:
        total += len(chunk)
        chunked_rows.append(chunk)

    logger.info('Lecture des lignes CSV (%s) terminée\n' % total)
    return chunked_rows


def export_created_data(bookings: List[Booking]):
    users = map(lambda b: ActivationUser(b), bookings)
    csv = generate_activation_users_csv(users)

    try:
        with app.app_context():
            send_users_activation_report(
                csv, ACTIVATION_USER_RECIPIENTS, send_raw_email)
    except MailServiceException as e:
        logger.error(
            'Error while sending activation users report email to MailJet', e)


def run(csv_file_path: str) -> None:
    logger.info(
        '-------------------------------------------------------------------------------')
    logger.info(
        '[START] Création des utilisateurs avec contremarques d\'activation')
    logger.info(
        '-------------------------------------------------------------------------------\n')

    stock = find_online_activation_stock()
    if not stock:
        logger.error('No activation stock found')
        exit(1)

    if not ACTIVATION_USER_RECIPIENTS:
        logger.error('No recipients [ACTIVATION_USER_RECIPIENTS] found')
        exit(1)

    logger.info('[STEP 1] Lecture du fichier CSV')
    csv_file = open(csv_file_path)
    csv_reader = csv.reader(csv_file)
    chunked_file = split_rows_in_chunks_with_no_duplicated_emails(
        csv_reader, CHUNK_SIZE)

    logger.info(
        '[STEP 2] Enregistrement des comptes et contremarques d\'activation')
    existing_tokens = booking_queries.find_existing_tokens()
    all_bookings = []
    total = 0
    for chunk in chunked_file:
        bookings = create_users_with_activation_bookings(
            chunk, stock, existing_tokens)
        if bookings:
            repository.save(*bookings)
        all_bookings.extend(bookings)
        total += len(chunk)
        logger.info('Enregistrement de %s comptes utilisateur | %s' %
                    (CHUNK_SIZE, total))
    logger.info('Enregistrement des comptes utilisateur terminé\n')

    logger.info('[STEP 3] Décompte des objets')
    logger.info('Users en BDD -> %s' % UserSQLEntity.query.count())
    logger.info('Users créés ou mis à jour -> %s' % total)
    logger.info('Bookings en BDD -> %s\n' % Booking.query.count())
    logger.info('Bookings créés ou existants -> %s' % len(existing_tokens))

    logger.info('[STEP 4] Envoi des comptes créés par mail')
    export_created_data(all_bookings)

    logger.info(
        '-------------------------------------------------------------------------------')
    logger.info(
        '[END] Création des utilisateurs avec contremarques d\'activation : %s' % total)
    logger.info(
        '-------------------------------------------------------------------------------')


def _is_header_or_blank_line(line: str) -> bool:
    return not line or not line[0] or line[0] == 'id'


def _extract_departement_code(plain_department: str) -> str:
    return re.search('\((.*?)\)$', plain_department).group()[1:-1]


def _get_password(csv_row: List[List[str]]) -> str:
    has_password_in_csv = len(csv_row) - 1 == PASSWORD_INDEX
    if has_password_in_csv:
        return bcrypt.hashpw(csv_row[PASSWORD_INDEX].encode('utf-8'), bcrypt.gensalt())
    else:
        return random_password()
