import pydantic

from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class GetEducationalBookingsQueryModel(HttpQueryParamsModel):
    redactorEmail: str | None = pydantic.Field(default=None, description="Email of querying redactor")

    model_config = pydantic.ConfigDict(title="Prebookings query filters")


class GetAllBookingsPerYearQueryModel(HttpQueryParamsModel):
    page: int | None = pydantic.Field(default=None, gt=0)
    per_page: int | None = pydantic.Field(default=None, gt=0)

    model_config = pydantic.ConfigDict(alias_generator=None)


class MergeInstitutionPrebookingsModel(HttpBodyModel):
    source_uai: str
    destination_uai: str
    bookings_ids: list[int]

    model_config = pydantic.ConfigDict(alias_generator=None)
