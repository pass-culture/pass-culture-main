from pcapi.core.categories import categories
from pcapi.core.categories import subcategories


def get_educational_categories() -> dict:
    educational_subcategories = [
        subcategory for subcategory in subcategories.ALL_SUBCATEGORIES if subcategory.can_be_educational
    ]
    educational_categories_ids = list(set(subcategory.category.id for subcategory in educational_subcategories))
    educational_categories = [
        category for category in categories.ALL_CATEGORIES if category.id in educational_categories_ids
    ]

    return {"subcategories": educational_subcategories, "categories": educational_categories}
