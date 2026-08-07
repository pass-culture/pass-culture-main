import datetime
import typing

import pydantic

from pcapi.routes.serialization import HttpBodyModel


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import EducationalDeposit


class EducationalDepositPeriodResponseV2(HttpBodyModel):
    start: datetime.datetime
    end: datetime.datetime


class EducationalDepositResponse(HttpBodyModel):
    uai: str
    deposit: float
    lastPeriodRemainingDeposit: float | None
    isFinal: bool
    period: EducationalDepositPeriodResponseV2

    @classmethod
    def build(cls, deposit: "EducationalDeposit") -> typing.Self:
        remaining = float(deposit.lastPeriodRemainingAmount) if deposit.lastPeriodRemainingAmount is not None else None

        return cls(
            deposit=float(deposit.amount),
            lastPeriodRemainingDeposit=remaining,
            uai=deposit.educationalInstitution.institutionId,
            isFinal=deposit.isFinal,
            period=EducationalDepositPeriodResponseV2(start=deposit.period.lower, end=deposit.period.upper),
        )


class EducationalDepositsResponse(HttpBodyModel):
    deposits: list[EducationalDepositResponse]

    model_config = pydantic.ConfigDict(title="List of deposit")
