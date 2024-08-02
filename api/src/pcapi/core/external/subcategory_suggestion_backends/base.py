import pydantic.v1 as pydantic_v1

from pcapi.core.offerers.models import Venue
from pcapi.routes.serialization import BaseModel


class SubcategoryProbability(BaseModel):
    subcategory: str
    probability: float


class MostProbableSubcategories(BaseModel):
    most_probable_subcategories: list[SubcategoryProbability]

    @pydantic_v1.validator("most_probable_subcategories", pre=True)
    # Sort subcategories by desc probability
    def sort_subcategories(cls, values: dict) -> dict:
        if isinstance(values, list):
            return sorted(values, key=lambda x: x["probability"], reverse=True)
        return values


class BaseBackend:
    def get_most_probable_subcategories(
        self, offer_name: str, offer_description: str | None = None, venue: Venue | None = None
    ) -> MostProbableSubcategories:
        raise NotImplementedError()
