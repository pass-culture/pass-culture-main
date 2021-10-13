# TODO: remove when native app is force updated to v156+

from enum import Enum

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories


class CategoryType(Enum):
    EVENT = "Event"
    THING = "Thing"


CATEGORY_TO_APP_LABEL = {
    c.id: [s.app_label for s in subcategories.ALL_SUBCATEGORIES if s.category_id == c.id]
    for c in categories.ALL_CATEGORIES
}
Category = Enum("Category", CATEGORY_TO_APP_LABEL)


CATEGORIES_LABEL_DICT = {label: category.name for category in list(Category) for label in category.value}

CategoryNameEnum = Enum("CategoryNameEnum", {category.name: category.name for category in list(Category)})
