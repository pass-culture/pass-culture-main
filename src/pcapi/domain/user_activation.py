import csv
from io import StringIO
from typing import Iterable

from pcapi.domain.password import random_password, generate_reset_token
from pcapi.models.deposit import Deposit
from pcapi.models.offer_type import EventType, ThingType
from pcapi.models.api_errors import ApiErrors
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.core.bookings.models import ActivationUser
from pcapi.scripts.beneficiary import THIRTY_DAYS_IN_HOURS

IMPORT_STATUS_MODIFICATION_RULE = 'Seuls les dossiers au statut DUPLICATE peuvent être modifiés (aux statuts REJECTED ou RETRY uniquement)'


def create_initial_deposit(user_to_activate: UserSQLEntity) -> Deposit:
    existing_deposits = Deposit.query.filter_by(userId=user_to_activate.id).all()
    if existing_deposits:
        error = AlreadyActivatedException()
        error.add_error('user', 'Cet utilisateur a déjà crédité son pass Culture')
        raise error

    else:
        deposit = Deposit()
        deposit.amount = 500
        deposit.user = user_to_activate
        deposit.source = 'fichier csv'
        return deposit


def generate_activation_users_csv(activation_users: Iterable[ActivationUser]) -> str:
    output = StringIO()
    csv_lines = [user.as_csv_row() for user in activation_users]
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(ActivationUser.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def is_activation_booking(booking):
    return booking.stock.offer.type in [str(EventType.ACTIVATION), str(ThingType.ACTIVATION)]


def create_beneficiary_from_application(application_detail: dict) -> UserSQLEntity:
    beneficiary = UserSQLEntity()
    beneficiary.lastName = application_detail['last_name']
    beneficiary.firstName = application_detail['first_name']
    beneficiary.publicName = '%s %s' % (application_detail['first_name'], application_detail['last_name'])
    beneficiary.email = application_detail['email']
    beneficiary.phoneNumber = application_detail['phone']
    beneficiary.departementCode = application_detail['department']
    beneficiary.postalCode = application_detail['postal_code']
    beneficiary.dateOfBirth = application_detail['birth_date']
    beneficiary.civility = application_detail['civility']
    beneficiary.activity = application_detail['activity']
    beneficiary.canBookFreeOffers = True
    beneficiary.isAdmin = False
    beneficiary.password = random_password()
    beneficiary.hasSeenTutorials = False
    generate_reset_token(beneficiary, validity_duration_hours=THIRTY_DAYS_IN_HOURS)

    deposit = Deposit()
    deposit.amount = 500
    deposit.source = 'démarches simplifiées dossier [%s]' % application_detail['application_id']
    beneficiary.deposits = [deposit]

    return beneficiary


def is_import_status_change_allowed(current_status: ImportStatus, new_status: ImportStatus) -> bool:
    if current_status == ImportStatus.DUPLICATE:
        if new_status in (ImportStatus.REJECTED, ImportStatus.RETRY):
            return True
    return False


class AlreadyActivatedException(ApiErrors):
    pass
