from datetime import timedelta
import logging
import typing

from pcapi.core import mails
from pcapi.core.users import api as users_api
from pcapi.core.users.models import User
from pcapi.emails import beneficiary_activation


logger = logging.getLogger(__name__)


def send_activation_email(user: User, reset_password_token_life_time: typing.Optional[timedelta] = None) -> bool:
    token = users_api.create_reset_password_token(user, token_life_time=reset_password_token_life_time)
    data = beneficiary_activation.get_activation_email_data(user=user, token=token)

    return mails.send(recipients=[user.email], data=data)
