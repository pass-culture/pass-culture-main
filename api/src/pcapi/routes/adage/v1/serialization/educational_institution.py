import typing

from pydantic.v1.fields import Field

from pcapi.core.educational import schemas


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import EducationalDeposit


class EducationalInstitutionDepositResponse(schemas.AdageBaseResponseModel):
    credit: float = Field(description="Total credit granted to the educational institution")
    isFinal: bool = Field(description="Flag to know if the credit has been approved and is now final")
    period: schemas.EducationalDepositPeriodResponse = Field(description="Period of this deposit")


def serialize_deposit(deposit: "EducationalDeposit") -> EducationalInstitutionDepositResponse:
    return EducationalInstitutionDepositResponse(
        credit=float(deposit.amount),
        isFinal=deposit.isFinal,
        period=schemas.EducationalDepositPeriodResponse(start=deposit.period.lower, end=deposit.period.upper),
    )


class EducationalInstitutionResponse(schemas.AdageBaseResponseModel):
    prebookings: list[schemas.EducationalBookingResponse]
    deposits: list[EducationalInstitutionDepositResponse]

    class Config:
        title = "School response model"
