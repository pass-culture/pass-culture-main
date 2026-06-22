from pydantic import RootModel

from pcapi.routes.serialization import HttpBodyModel


class GetAdditionalFeeType(HttpBodyModel):
    name: str


class GetAdditionalFeeTypes(RootModel):
    root: list[GetAdditionalFeeType]
