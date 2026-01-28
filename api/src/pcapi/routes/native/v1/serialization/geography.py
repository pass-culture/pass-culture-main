from pydantic import BaseModel as BaseModelV2

from pcapi.routes.serialization import HttpBodyModel


class InseeCountry(BaseModelV2):
    cog: int  # code officiel géographique
    libcog: str  # libellé cog


class InseeCountries(HttpBodyModel):
    countries: list[InseeCountry]
