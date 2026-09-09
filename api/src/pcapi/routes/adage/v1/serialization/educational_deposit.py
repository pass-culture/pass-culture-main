import typing

import pydantic

from pcapi.core.educational import schemas
from pcapi.routes.serialization import HttpBodyModel


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import EducationalDeposit


class EducationalDepositResponse(HttpBodyModel):
    uai: str
    deposit: float
    isFinal: bool
    period: schemas.EducationalDepositPeriodResponseV2

    @classmethod
    def build(cls, educational_deposit: "EducationalDeposit") -> typing.Self:
        return cls(
            deposit=float(educational_deposit.amount),
            uai=educational_deposit.educationalInstitution.institutionId,
            isFinal=educational_deposit.isFinal,
            period=schemas.EducationalDepositPeriodResponseV2(
                start=educational_deposit.period.lower, end=educational_deposit.period.upper
            ),
        )


class EducationalDepositsResponse(HttpBodyModel):
    deposits: list[EducationalDepositResponse]

    model_config = pydantic.ConfigDict(title="List of deposit")

    @classmethod
    def build(cls, educational_deposits: list["EducationalDeposit"]) -> typing.Self:
        return cls(
            deposits=[
                EducationalDepositResponse.build(educational_deposit) for educational_deposit in educational_deposits
            ]
        )
