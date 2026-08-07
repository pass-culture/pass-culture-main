import datetime
import typing

from pydantic.v1.fields import Field

from pcapi.core.educational import schemas


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import EducationalDeposit


# use EducationalDepositPeriodResponseV2 in serialization.educational_deposit when migrating to pydantic v2
class EducationalDepositPeriodResponse(schemas.AdageBaseResponseModel):
    start: datetime.datetime
    end: datetime.datetime


class EducationalInstitutionDepositResponse(schemas.AdageBaseResponseModel):
    credit: float = Field(description="Total credit granted to the educational institution")
    isFinal: bool = Field(description="Flag to know if the credit has been approved and is now final")
    period: EducationalDepositPeriodResponse = Field(description="Period of this deposit")

    @classmethod
    def build(cls, deposit: "EducationalDeposit") -> typing.Self:
        return cls(
            credit=float(deposit.amount),
            isFinal=deposit.isFinal,
            period=EducationalDepositPeriodResponse(start=deposit.period.lower, end=deposit.period.upper),
        )


class EducationalInstitutionResponse(schemas.AdageBaseResponseModel):
    prebookings: list[schemas.EducationalBookingResponse]
    deposits: list[EducationalInstitutionDepositResponse]

    class Config:
        title = "School response model"
