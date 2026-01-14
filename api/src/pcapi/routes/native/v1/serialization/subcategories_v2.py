from typing import Any

from pydantic.v1.utils import GetterDict

from pcapi.core.categories import models as categories_models
from pcapi.core.categories import subcategories
from pcapi.core.categories.app_search_tree import NATIVE_CATEGORIES
from pcapi.core.categories.app_search_tree import SEARCH_GROUPS
from pcapi.core.categories.genres.book import BookType
from pcapi.core.categories.genres.movie import MovieType
from pcapi.core.categories.genres.music import MusicType
from pcapi.core.categories.genres.show import ShowType
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.serialization.utils import to_camel


class SubcategoryResponseGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "search_group_name":
            # A subcategory can be associated to more than one search group.
            # We keep it like this for backward compatibility.
            # This is sufficient for the app the behave correctly.
            return next(
                search_group.search_value
                for search_group in SEARCH_GROUPS
                if self._obj.id in search_group.included_subcategories
            )

        if key == "native_category_id":
            # A subcategory can be associated to more than one native category.
            # We keep it like this for backward compatibility.
            # This is sufficient for the app the behave correctly.
            return next(
                (
                    native_category.search_value
                    for native_category in NATIVE_CATEGORIES
                    if self._obj.id in native_category.included_subcategories
                ),
                None,
            )

        return super().get(key, default)


class SubcategoryResponseModelv2(BaseModel):
    id: str
    category_id: str
    native_category_id: str | None
    app_label: str
    search_group_name: str
    homepage_label_name: str
    is_event: bool
    online_offline_platform: subcategories.OnlineOfflinePlatformChoicesEnum

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        getter_dict = SubcategoryResponseGetterDict
        orm_mode = True


class SearchGroupResponseModelv2(BaseModel):
    name: str
    value: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class HomepageLabelResponseModelv2(BaseModel):
    name: str
    value: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class CategoryGetterDict(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        if key == "positions":
            return None if "LIVRES" in [parent.name for parent in self._obj.parents] else self._obj.positions

        if key == "parents":
            return [parent.name for parent in self._obj.parents]
        return super().get(key, default)


class NativeCategoryResponseModelv2(BaseModel):
    name: str
    value: str | None
    genre_type: categories_models.GenreType | None
    parents: list[str]
    positions: dict[str, int] | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        getter_dict = CategoryGetterDict
        orm_mode = True


class GenreTypeContentModel(BaseModel):
    name: str
    value: str

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class GenreTypeModel(BaseModel):
    name: categories_models.GenreType
    values: list[GenreTypeContentModel]
    trees: list[BookType] | list[MusicType] | list[ShowType] | list[MovieType]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SubcategoriesResponseModelv2(BaseModel):
    subcategories: list[SubcategoryResponseModelv2]
    searchGroups: list[SearchGroupResponseModelv2]
    homepageLabels: list[HomepageLabelResponseModelv2]
    nativeCategories: list[NativeCategoryResponseModelv2]
    genreTypes: list[GenreTypeModel]


class CategoryResponseModel(ConfiguredBaseModel):
    label: str
    parents: list[str]
    gtls: list[str] | None = None
    positions: dict[str, int] | None
    search_filter: str | None = None
    search_value: str | None = None

    class Config:
        getter_dict = CategoryGetterDict


class CategoriesResponseModel(ConfiguredBaseModel):
    categories: list[CategoryResponseModel]
