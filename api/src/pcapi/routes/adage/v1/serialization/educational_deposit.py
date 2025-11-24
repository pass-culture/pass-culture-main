import typing

from pcapi.core.educational import schemas


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import EducationalDeposit


class EducationalDepositResponse(schemas.AdageBaseResponseModel):
    uai: str
    deposit: float
    isFinal: bool
    period: schemas.EducationalDepositPeriodResponse


class EducationalDepositsResponse(schemas.AdageBaseResponseModel):
    deposits: list[EducationalDepositResponse]

    class Config:
        title = "List of deposit"


def serialize_educational_deposits(
    educational_deposits: list["EducationalDeposit"],
) -> list[EducationalDepositResponse]:
    return [serialize_educational_deposit(educational_deposit) for educational_deposit in educational_deposits]


def serialize_educational_deposit(educational_deposit: "EducationalDeposit") -> EducationalDepositResponse:
    # TODO(jcicurel): deposit period should be non-nullable
    assert educational_deposit.period is not None

    return EducationalDepositResponse(
        deposit=float(educational_deposit.amount),
        uai=educational_deposit.educationalInstitution.institutionId,
        isFinal=educational_deposit.isFinal,
        period=schemas.EducationalDepositPeriodResponse(
            start=educational_deposit.period.lower, end=educational_deposit.period.upper
        ),
    )
