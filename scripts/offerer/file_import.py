from builtins import Exception

import csv

from datetime import datetime
from typing import List, Iterable, Callable

from models import Offerer, PcObject, User, UserOfferer, Venue
from models.user_offerer import RightsType
from domain.password import random_password, generate_reset_token
from repository.offerer_queries import find_by_siren
from repository.user_queries import find_user_by_email
from repository.user_offerer_queries import find_one_or_none_by_user_id_and_offerer_id
from repository.venue_queries import find_by_managing_offerer_id
from utils.logger import logger

USER_LAST_NAME_COLUMN_INDEX = 0
USER_FIRST_NAME_COLUMN_INDEX = 1
USER_EMAIL_COLUMN_INDEX = 2
USER_DEPARTMENT_CODE_COLUMN_INDEX = 3
OFFERER_SIREN_COLUMN_INDEX = 4
OFFERER_POSTAL_CODE_COLUMN_INDEX = 5
OFFERER_CITY_COLUMN_INDEX = 6
OFFERER_NAME_COLUMN_INDEX = 7

THIRTY_DAYS_IN_HOURS = 30 * 24

class UserNotCreatedException(Exception):
    pass

class OffererNotCreatedException(Exception):
    pass

def split_rows_with_no_duplicated_emails(csv_reader: Iterable) \
        -> List[List[List[str]]]:
    rows = []
    existing_emails = set()

    for line in csv_reader:
        if _is_header_or_blank_line(line):
            continue

        email = line[USER_EMAIL_COLUMN_INDEX]

        if email not in existing_emails:
            rows.append(line)
            existing_emails.add(email)

    logger.info('Lecture des lignes CSV (%s) terminée\n' % len(rows))
    return rows

def create_activated_user_offerer(
        csv_row: List[str],
        find_user: Callable = find_user_by_email,
        find_offerer: Callable = find_by_siren,
        find_user_offerer: Callable = find_one_or_none_by_user_id_and_offerer_id,
) -> List[UserOfferer]:
    user = find_user(csv_row[USER_EMAIL_COLUMN_INDEX])
    if not user:
        user = User()
    filled_user = fill_user_from(csv_row, user)
    PcObject.save(filled_user)

    offerer = find_offerer(csv_row[OFFERER_SIREN_COLUMN_INDEX])
    if not offerer:
        offerer = Offerer()

    filled_offerer = fill_offerer_from(csv_row, offerer)
    PcObject.save(filled_offerer)

    virtual_venue = find_by_managing_offerer_id(filled_offerer.id)
    if not virtual_venue:
        filled_virtual_venue = fill_virtual_venue_from(csv_row, filled_offerer, Venue())
        PcObject.save(filled_virtual_venue)

    user_offerer = find_user_offerer(filled_user.id, filled_offerer.id)
    if not user_offerer:
        filled_user_offerer = fill_user_offerer_from(UserOfferer(), filled_user, filled_offerer)
        PcObject.save(filled_user_offerer)
        return filled_user_offerer
    else:
        return None

def fill_virtual_venue_from(csv_row: List[str], offerer: Offerer, venue: Venue) -> Venue:
    venue.bookingEmail = csv_row[USER_EMAIL_COLUMN_INDEX]
    venue.name = csv_row[OFFERER_NAME_COLUMN_INDEX]
    venue.managingOfferer = offerer
    venue.isVirtual = True
    return venue

def fill_user_offerer_from(
        user_offerer: UserOfferer,
        created_user: User,
        created_offerer: Offerer
) -> UserOfferer:
    if created_user.id is None: raise UserNotCreatedException()
    if created_offerer.id is None: raise OffererNotCreatedException()

    user_offerer.userId = created_user.id
    user_offerer.offererId = created_offerer.id
    user_offerer.rights = RightsType.editor
    return user_offerer

def fill_user_from(csv_row: List[str], user: User) -> User:
    user.lastName = csv_row[USER_LAST_NAME_COLUMN_INDEX]
    user.firstName = csv_row[USER_FIRST_NAME_COLUMN_INDEX].split(' ')[0]
    user.publicName = '%s %s' % (user.firstName, user.lastName)
    user.email = csv_row[USER_EMAIL_COLUMN_INDEX]
    user.departementCode = csv_row[USER_DEPARTMENT_CODE_COLUMN_INDEX]
    user.canBookFreeOffers = False
    user.password = random_password()
    generate_reset_token(user, validity_duration_hours=THIRTY_DAYS_IN_HOURS)
    return user

def fill_offerer_from(csv_row: List[str], offerer: Offerer) -> Offerer:
    offerer.siren = csv_row[OFFERER_SIREN_COLUMN_INDEX]
    offerer.name = csv_row[OFFERER_NAME_COLUMN_INDEX]
    offerer.thumbCount = 0
    offerer.postalCode = csv_row[OFFERER_POSTAL_CODE_COLUMN_INDEX]
    offerer.city = csv_row[OFFERER_CITY_COLUMN_INDEX]
    offerer.dateCreated = datetime.utcnow()
    return offerer

def run(csv_file_path: str) -> None:
    logger.info(
        '-------------------------------------------------------------------------------')
    logger.info(
        '[START] Création des structures avec leur lieu')
    logger.info(
        '-------------------------------------------------------------------------------\n')

    logger.info('[STEP 1] Lecture du fichier CSV')
    csv_file = open(csv_file_path)
    csv_reader = csv.reader(csv_file)
    rows = split_rows_with_no_duplicated_emails(csv_reader)

    logger.info(
        '[STEP 2] Enregistrement des structures et lieux')
    user_offerers = []
    for row in rows:
        user_offerer = create_activated_user_offerer(row)
        if user_offerer:
            user_offerers.append(user_offerer)
            logger.info('Enregistrement de %s comptes pro | %s' %
                        (len(rows), len(user_offerers)))
    logger.info('Enregistrement des comptes pro terminé\n')

    logger.info('[STEP 3] Décompte des objets')
    logger.info('Users offerers en BDD -> %s' % UserOfferer.query.count())
    logger.info('Users offerers créés ou mis à jour -> %s' % len(user_offerers))

    logger.info(
        '-------------------------------------------------------------------------------')
    logger.info(
        '[END] Création des structures avec leur lieu : %s' % len(user_offerers))
    logger.info(
        '-------------------------------------------------------------------------------')

def _is_header_or_blank_line(line: str) -> bool:
    return not line or not line[0] or line[0].lower() == 'nom'
