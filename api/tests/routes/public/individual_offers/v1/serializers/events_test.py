from pcapi.core.categories import subcategories
from pcapi.routes.public.individual_offers.v1.serializers.events import EventCategoryEnum


def test_event_category_enum_is_valid():
    assert set([member.value for member in EventCategoryEnum]) == set(list(subcategories.EVENT_SUBCATEGORIES))
