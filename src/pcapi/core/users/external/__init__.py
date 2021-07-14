from pcapi.core.users.models import User

from .sendinblue import update_contact_attributes as update_sendinblue_user


def update_external_user(user: User):
    update_sendinblue_user(user)
