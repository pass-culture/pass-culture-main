import typing

from pcapi.serialization.educational.adage.shared import AdageBaseResponseModel


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import EducationalDeposit


class EducationalDepositResponse(AdageBaseResponseModel):
    uai: str
    deposit: float
    isFinal: bool


class EducationalDepositsResponse(AdageBaseResponseModel):
    deposits: list[EducationalDepositResponse]

    class Config:
        title = "List of deposit"


def serialize_educational_deposits(
    educational_deposits: list["EducationalDeposit"],
) -> list[EducationalDepositResponse]:
    return [serialize_educational_deposit(educational_deposit) for educational_deposit in educational_deposits]


def serialize_educational_deposit(educational_deposit: "EducationalDeposit") -> EducationalDepositResponse:
    return EducationalDepositResponse(
        deposit=float(educational_deposit.amount),
        uai=educational_deposit.educationalInstitution.institutionId,
        isFinal=educational_deposit.isFinal,
    )
