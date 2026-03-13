import enum

import pydantic

from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel


class LinkVenueToPricingPointBodyModel(BaseModel):
    pricingPointId: int

    class Config:
        extra = "forbid"


class GetVenuePricingPointResponseModel(HttpBodyModel):
    id: int
    siret: str
    # TODO: publicName ou public_name ?
    venue_name: str = pydantic.Field(alias="publicName")


class SimplifiedBankAccountStatus(enum.Enum):
    PENDING = "pending"
    VALID = "valid"
    PENDING_CORRECTIONS = "pending_corrections"


def parse_bank_account_status(bank_account: finance_models.BankAccount | None) -> SimplifiedBankAccountStatus | None:
    status_enum = finance_models.BankAccountApplicationStatus

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
