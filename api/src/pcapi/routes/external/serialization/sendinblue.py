from typing import Any

from pydantic.v1.utils import GetterDict

from pcapi import settings
from pcapi.routes.serialization import BaseModel


class RecommendedOfferGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "url":
            return f"{settings.WEBAPP_V2_URL}/offre/{self._obj.id}"

        if key == "name":
            return self._obj.name

        if key == "image":
            return self._obj.thumbUrl

        return super().get(key, default)


class RecommendedOffer(BaseModel):
    url: str
    name: str
    image: str | None

    class Config:
        orm_mode = True
        getter_dict = RecommendedOfferGetterDict


class BrevoOffersResponse(BaseModel):
    # For integration with Brevo data feeds,
    # the response root must not be a list
    offers: list[RecommendedOffer]
