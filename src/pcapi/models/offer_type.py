# TODO: remove when native app is force updated to v156+

from enum import Enum

from pcapi.core.categories import subcategories


class CategoryType(Enum):
    EVENT = "Event"
    THING = "Thing"


def _make_app_label_list_from_search_group(search_group_name: str):
    return [
        subcategory.app_label
        for subcategory in subcategories.ALL_SUBCATEGORIES
        if subcategory.search_group_name == search_group_name
    ]


class Category(Enum):
    CINEMA = _make_app_label_list_from_search_group(subcategories.SearchGroups.CINEMA.name)
    CONFERENCE = _make_app_label_list_from_search_group(subcategories.SearchGroups.CONFERENCE.name)
    FILM = _make_app_label_list_from_search_group(subcategories.SearchGroups.FILM.name)
    INSTRUMENT = _make_app_label_list_from_search_group(subcategories.SearchGroups.INSTRUMENT.name)
    JEUX_VIDEO = _make_app_label_list_from_search_group(subcategories.SearchGroups.JEU.name)
    LECON = _make_app_label_list_from_search_group(subcategories.SearchGroups.COURS.name)
    LIVRE = _make_app_label_list_from_search_group(subcategories.SearchGroups.LIVRE.name)
    MATERIEL_ART_CREA = _make_app_label_list_from_search_group(subcategories.SearchGroups.MATERIEL.name)
    MUSIQUE = _make_app_label_list_from_search_group(subcategories.SearchGroups.MUSIQUE.name)
    PRESSE = _make_app_label_list_from_search_group(subcategories.SearchGroups.PRESSE.name)
    SPECTACLE = _make_app_label_list_from_search_group(subcategories.SearchGroups.SPECTACLE.name)
    VISITE = _make_app_label_list_from_search_group(subcategories.SearchGroups.VISITE.name)


CategoryNameEnum = Enum("CategoryNameEnum", {category.name: category.name for category in list(Category)})

CATEGORIES_LABEL_DICT = {label: category.name for category in list(Category) for label in category.value}
