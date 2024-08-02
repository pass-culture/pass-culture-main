from pcapi.core.external.subcategory_suggestion_backends import fixtures
from pcapi.core.external.subcategory_suggestion_backends.base import MostProbableSubcategories
from pcapi.core.offerers.models import Venue

from .base import BaseBackend


class TestBackend(BaseBackend):
    def get_most_probable_subcategories(
        self, offer_name: str, offer_description: str | None = None, venue: Venue | None = None
    ) -> MostProbableSubcategories:
        subcategory_suggestions = fixtures.SUBCATEGORY_SUGGESTION_RANDOM_RESULT
        return MostProbableSubcategories(**subcategory_suggestions)  # type: ignore[arg-type]
