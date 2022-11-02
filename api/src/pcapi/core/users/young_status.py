from datetime import datetime
import enum

import attrs

from pcapi.core.users import models


class YoungStatusType(enum.Enum):
    ELIGIBLE = "eligible"
    NON_ELIGIBLE = "non_eligible"
    BENEFICIARY = "beneficiary"
    EX_BENEFICIARY = "ex_beneficiary"
    SUSPENDED = "suspended"


@attrs.frozen
class YoungStatus:
    status_type: YoungStatusType


@attrs.frozen
class Eligible(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.ELIGIBLE


@attrs.frozen
class NonEligible(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.NON_ELIGIBLE


@attrs.frozen
class Beneficiary(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.BENEFICIARY


@attrs.frozen
class ExBeneficiary(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.EX_BENEFICIARY


@attrs.frozen
class Suspended(YoungStatus):
    status_type: YoungStatusType = YoungStatusType.SUSPENDED


def young_status(user: models.User) -> YoungStatus:
    if not user.isActive:
        return Suspended()

    if user.is_beneficiary:
        if user.deposit_expiration_date and user.deposit_expiration_date < datetime.utcnow():
            return ExBeneficiary()

        return Beneficiary()

    if user.eligibility is not None:
        return Eligible()

    return NonEligible()
