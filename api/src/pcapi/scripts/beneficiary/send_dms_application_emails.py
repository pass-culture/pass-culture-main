import logging
import typing

from pcapi.core.mails.transactional.users.subscription_document_error import (
    send_subscription_document_error_email_to_user_list,
)
from pcapi.core.users.models import User
from pcapi.models.beneficiary_import import BeneficiaryImport


logger = logging.getLogger(__name__)


def get_users_from_applications(application_ids: list[int], source: str) -> typing.Iterable[User]:
    return (
        User.query.join(BeneficiaryImport)
        .filter(BeneficiaryImport.applicationId.in_(application_ids))
        .filter(BeneficiaryImport.source == source)
    )


def run(application_ids: list[int], source: str) -> typing.Iterable[User]:
    users = get_users_from_applications(application_ids, source)
    if not send_subscription_document_error_email_to_user_list(users, code="unread-mrz-document"):
        logger.warning("Could not send dms application emails")
    return users
