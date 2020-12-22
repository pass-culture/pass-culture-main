import csv
from io import StringIO
from typing import Iterable

from pcapi.core.payments import api as payments_api
from pcapi.domain.password import generate_reset_token
from pcapi.domain.password import random_password
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.scripts.beneficiary import THIRTY_DAYS_IN_HOURS


IMPORT_STATUS_MODIFICATION_RULE = (
    "Seuls les dossiers au statut DUPLICATE peuvent être modifiés (aux statuts REJECTED ou RETRY uniquement)"
)


class ActivationUser:
    CSV_HEADER = [
        "Prénom",
        "Nom",
        "Email",
        "Contremarque d'activation",
    ]

    def __init__(self, booking):
        self.first_name = booking.user.firstName
        self.last_name = booking.user.lastName
        self.email = booking.user.email
        self.token = booking.token

    def as_csv_row(self):
        return [self.first_name, self.last_name, self.email, self.token]


def generate_activation_users_csv(activation_users: Iterable[ActivationUser]) -> str:
    output = StringIO()
    csv_lines = [user.as_csv_row() for user in activation_users]
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(ActivationUser.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def create_beneficiary_from_application(application_detail: dict) -> UserSQLEntity:
    beneficiary = UserSQLEntity()
    beneficiary.lastName = application_detail["last_name"]
    beneficiary.firstName = application_detail["first_name"]
    beneficiary.publicName = "%s %s" % (application_detail["first_name"], application_detail["last_name"])
    beneficiary.email = application_detail["email"]
    beneficiary.phoneNumber = application_detail["phone"]
    beneficiary.departementCode = application_detail["department"]
    beneficiary.postalCode = application_detail["postal_code"]
    beneficiary.dateOfBirth = application_detail["birth_date"]
    beneficiary.civility = application_detail["civility"]
    beneficiary.activity = application_detail["activity"]
    beneficiary.isBeneficiary = True
    beneficiary.isAdmin = False
    beneficiary.password = random_password()
    beneficiary.hasSeenTutorials = False
    generate_reset_token(beneficiary, validity_duration_hours=THIRTY_DAYS_IN_HOURS)

    application_id = application_detail["application_id"]
    deposit = payments_api.create_deposit(beneficiary, f"démarches simplifiées dossier [{application_id}]")
    beneficiary.deposits = [deposit]

    return beneficiary


def is_import_status_change_allowed(current_status: ImportStatus, new_status: ImportStatus) -> bool:
    if current_status == ImportStatus.DUPLICATE:
        if new_status in (ImportStatus.REJECTED, ImportStatus.RETRY):
            return True
    return False
