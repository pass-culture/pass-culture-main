import enum

from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models


class SimplifiedBankAccountStatus(enum.Enum):
    PENDING = "pending"
    VALID = "valid"
    PENDING_CORRECTIONS = "pending_corrections"


def parse_venue_bank_account_status(venue: offerers_models.Venue) -> SimplifiedBankAccountStatus | None:
    status_enum = finance_models.BankAccountApplicationStatus
    bank_account = venue.current_bank_account

    # TODO(jbaudet - 10/2025): move this code to a more
    # appropriate api/repository/models module once offerers
    # have been replaced by venues. These rules come from the
    # `get_offerer_and_extradata` function.
    if not bank_account or not bank_account.isActive:
        return None

    match bank_account.status:
        case status_enum.ACCEPTED:
            return SimplifiedBankAccountStatus.VALID
        case status_enum.DRAFT | status_enum.ON_GOING:
            return SimplifiedBankAccountStatus.PENDING
        case status_enum.WITH_PENDING_CORRECTIONS:
            return SimplifiedBankAccountStatus.PENDING_CORRECTIONS
        case _:
            return None
