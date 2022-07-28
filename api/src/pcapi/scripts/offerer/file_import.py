import csv
from datetime import datetime
import logging

from pcapi.core.offerers.api import create_digital_venue
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.offerers.repository import find_offerer_by_siren
from pcapi.core.offerers.repository import find_venue_by_managing_offerer_id
from pcapi.core.users.api import fulfill_account_password
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.core.users.utils import sanitize_email
from pcapi.repository import repository


logger = logging.getLogger(__name__)


USER_LAST_NAME_COLUMN_INDEX = 0
USER_FIRST_NAME_COLUMN_INDEX = 1
USER_EMAIL_COLUMN_INDEX = 2
USER_DEPARTMENT_CODE_COLUMN_INDEX = 3
OFFERER_SIREN_COLUMN_INDEX = 4
OFFERER_POSTAL_CODE_COLUMN_INDEX = 5
OFFERER_CITY_COLUMN_INDEX = 6
OFFERER_NAME_COLUMN_INDEX = 7


class UserNotCreatedException(Exception):
    pass


class OffererNotCreatedException(Exception):
    pass


def iterate_rows_for_user_offerers(csv_rows: list[list[str]]) -> list:
    user_offerers = []
    for row in csv_rows:
        if _is_header_or_blank_line(row):  # type: ignore [arg-type]
            continue

        user_offerer = create_activated_user_offerer(row)
        if user_offerer:
            user_offerers.append(user_offerer)
            logger.info("Enregistrement de %s comptes pro", len(user_offerers))
    return user_offerers


def create_activated_user_offerer(csv_row: list[str]) -> UserOfferer:
    user = find_user_by_email(csv_row[USER_EMAIL_COLUMN_INDEX])
    if not user:
        user = User()
    filled_user = fill_user_from(csv_row, user)
    repository.save(filled_user)

    offerer = find_offerer_by_siren(csv_row[OFFERER_SIREN_COLUMN_INDEX])
    if not offerer:
        offerer = Offerer()

    filled_offerer = fill_offerer_from(csv_row, offerer)
    repository.save(filled_offerer)

    virtual_venue = find_venue_by_managing_offerer_id(filled_offerer.id)
    if not virtual_venue:
        filled_virtual_venue = create_digital_venue(offerer)
        repository.save(filled_virtual_venue)

    user_offerer = UserOfferer.query.filter_by(userId=filled_user.id, offererId=filled_offerer.id).one_or_none()
    if not user_offerer:
        filled_user_offerer = fill_user_offerer_from(UserOfferer(), filled_user, filled_offerer)
        repository.save(filled_user_offerer)
        return filled_user_offerer
    return None  # type: ignore [return-value]


def fill_user_offerer_from(user_offerer: UserOfferer, created_user: User, created_offerer: Offerer) -> UserOfferer:
    if created_user.id is None:
        raise UserNotCreatedException()
    if created_offerer.id is None:
        raise OffererNotCreatedException()

    user_offerer.user = created_user
    user_offerer.offerer = created_offerer
    return user_offerer


def fill_user_from(csv_row: list[str], user: User) -> User:
    user.lastName = csv_row[USER_LAST_NAME_COLUMN_INDEX]
    user.firstName = csv_row[USER_FIRST_NAME_COLUMN_INDEX].split(" ")[0]
    user.publicName = "%s %s" % (user.firstName, user.lastName)
    user.email = sanitize_email(csv_row[USER_EMAIL_COLUMN_INDEX])
    user.departementCode = csv_row[USER_DEPARTMENT_CODE_COLUMN_INDEX]
    user.remove_beneficiary_role()
    user.add_pro_role()

    fulfill_account_password(user)
    return user


def fill_offerer_from(csv_row: list[str], offerer: Offerer) -> Offerer:
    offerer.siren = csv_row[OFFERER_SIREN_COLUMN_INDEX]
    offerer.name = csv_row[OFFERER_NAME_COLUMN_INDEX]
    offerer.thumbCount = 0  # type: ignore [assignment]
    offerer.postalCode = csv_row[OFFERER_POSTAL_CODE_COLUMN_INDEX]  # type: ignore [assignment]
    offerer.city = csv_row[OFFERER_CITY_COLUMN_INDEX]  # type: ignore [assignment]
    offerer.dateCreated = datetime.utcnow()
    return offerer


def run(csv_file_path: str) -> None:
    logger.info("-------------------------------------------------------------------------------")
    logger.info("[START] Création des structures avec leur lieu")
    logger.info("-------------------------------------------------------------------------------\n")

    logger.info("[STEP 1] Lecture du fichier CSV")
    with open(csv_file_path, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)

        logger.info("[STEP 2] Enregistrement des structures et lieux")
        user_offerers = iterate_rows_for_user_offerers(csv_reader)  # type: ignore [arg-type]
    logger.info("Enregistrement des comptes pro terminé\n")

    logger.info("[STEP 3] Décompte des objets")
    logger.info("Users offerers en BDD -> %s", UserOfferer.query.count())
    logger.info("Users offerers créés ou mis à jour -> %s", len(user_offerers))

    logger.info("-------------------------------------------------------------------------------")
    logger.info("[END] Création des structures avec leur lieu : %s", len(user_offerers))
    logger.info("-------------------------------------------------------------------------------")


def _is_header_or_blank_line(line: str) -> bool:
    return not line or not line[0] or line[0].lower() == "nom"
