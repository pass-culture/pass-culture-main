import logging

from pcapi.core import mails
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud.common import models as common_fraud_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


def send_duplicate_beneficiary_email(
    rejected_user: users_models.User,
    identity_content: common_fraud_models.IdentityCheckContent,
    is_id_piece_number_duplicate: bool = False,
) -> bool:
    if is_id_piece_number_duplicate:
        duplicate_beneficiary = fraud_api.find_duplicate_id_piece_number_user(
            identity_content.get_id_piece_number(), rejected_user.id
        )
    else:
        duplicate_beneficiary = fraud_api.find_duplicate_beneficiary(
            identity_content.get_first_name(),  # type: ignore [arg-type]
            identity_content.get_last_name(),  # type: ignore [arg-type]
            identity_content.get_married_name(),
            identity_content.get_birth_date(),  # type: ignore [arg-type]
            rejected_user.id,
        )
    if not duplicate_beneficiary:
        logger.error("No duplicate beneficiary found", extra={"user_id": rejected_user.id})
        anonymized_email = "***"
    else:
        anonymized_email = _anonymize_email(duplicate_beneficiary.email)

    return mails.send(
        recipients=[rejected_user.email],
        data=models.SendinblueTransactionalEmailData(
            template=TransactionalEmail.SUBCRIPTION_REJECTED_FOR_DUPLICATE_BENEFICIARY.value,
            params={"DUPLICATE_BENEFICIARY_EMAIL": anonymized_email},
        ),
    )


def _anonymize_email(email: str) -> str:
    try:
        name, domain = email.split("@")
    except ValueError:
        logger.exception("User email %s format is wrong", email)
        return "***"

    if len(name) > 3:
        hidden_name = name[:3]
    elif len(name) > 1:
        hidden_name = name[:1]
    else:
        hidden_name = ""

    return f"{hidden_name}***@{domain}"
