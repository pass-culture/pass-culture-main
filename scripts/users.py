import re
from typing import List

from domain.password import generate_reset_token
from models import User

THIRTY_DAYS = 30 * 24


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
