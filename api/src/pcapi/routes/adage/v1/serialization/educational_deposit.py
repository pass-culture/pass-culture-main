from pcapi.core.educational.repository import EducationalDepositNamedTuple
from pcapi.routes.adage.v1.serialization.config import AdageBaseResponseModel


class EducationalDepositResponse(AdageBaseResponseModel):
    uai: str
    deposit: float
    isFinal: bool


class EducationalDepositsResponse(AdageBaseResponseModel):
    deposits: list[EducationalDepositResponse]

    class Config:
        title = "List of deposit"


def serialize_educational_deposits(
    educational_deposits: list[EducationalDepositNamedTuple],
) -> list[EducationalDepositResponse]:
    serialized_educational_deposit = []
    for educational_deposit in educational_deposits:
        serialized_educational_deposit.append(serialize_educational_deposit(educational_deposit))
    return serialized_educational_deposit


def serialize_educational_deposit(educational_deposit: EducationalDepositNamedTuple) -> EducationalDepositResponse:
    return EducationalDepositResponse(
        deposit=float(educational_deposit[0]),
        uai=educational_deposit[1],
        isFinal=educational_deposit[2],
    )
