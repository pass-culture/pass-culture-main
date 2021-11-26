import typing

from pcapi.core.users.models import User
from pcapi.domain import user_emails
from pcapi.models.beneficiary_import import BeneficiaryImport


def get_users_from_applications(application_ids: list[int], source: str) -> typing.Iterable[User]:
    return (
        User.query.join(BeneficiaryImport)
        .filter(BeneficiaryImport.applicationId.in_(application_ids))
        .filter(BeneficiaryImport.source == source)
    )


def run(application_ids: list[int], source: str) -> typing.Iterable[User]:
    users = get_users_from_applications(application_ids, source)
    user_emails.send_dms_application_emails(users)
    return users
