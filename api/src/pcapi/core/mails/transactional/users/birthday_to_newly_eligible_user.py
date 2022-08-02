from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models


def get_birthday_age_18_to_newly_eligible_user_email_data() -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(template=TransactionalEmail.BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER.value)


def send_birthday_age_18_email_to_newly_eligible_user(user: users_models.User) -> bool:
    data = get_birthday_age_18_to_newly_eligible_user_email_data()
    return mails.send(recipients=[user.email], data=data)
