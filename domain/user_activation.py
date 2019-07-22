import csv
from io import StringIO
from typing import Iterable
from urllib.parse import urlencode

from models import Deposit, EventType, ThingType, ApiErrors, User, ImportStatus
from models.booking import ActivationUser

IMPORT_STATUS_MODIFICATION_RULE = 'Seuls les dossiers au statut DUPLICATE peuvent être modifiés en REJECTED'


def create_initial_deposit(user_to_activate: User) -> Deposit:
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


def generate_set_password_url(app_domain: str, user: User) -> str:
    return '%s/activation/%s?%s' % (
        app_domain,
        user.resetPasswordToken,
        urlencode({'email': user.email})
    )


def check_is_activation_booking(booking):
    return booking.stock.offer.product.type in [str(EventType.ACTIVATION), str(ThingType.ACTIVATION)]


def is_import_status_change_allowed(current_status: ImportStatus, new_status: ImportStatus) -> bool:
    if current_status == ImportStatus.DUPLICATE:
        if new_status == ImportStatus.REJECTED:
            return True
    return False


class AlreadyActivatedException(ApiErrors):
    pass
