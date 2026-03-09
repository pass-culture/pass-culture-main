from pcapi.core.categories import models as categories_models
from pcapi.core.categories import subcategories
from pcapi.core.categories.app_search_tree import NATIVE_CATEGORIES
from pcapi.core.categories.app_search_tree import SEARCH_GROUPS
from pcapi.core.categories.genres.book import BookType
from pcapi.core.categories.genres.movie import MovieType
from pcapi.core.categories.genres.music import MusicType
from pcapi.core.categories.genres.show import ShowType
from pcapi.routes.serialization import HttpBodyModel


class SubcategoryResponseModelv2(HttpBodyModel):
    id: str
    category_id: str
    native_category_id: str | None = None
    app_label: str
    search_group_name: str
    homepage_label_name: str
    is_event: bool
    online_offline_platform: subcategories.OnlineOfflinePlatformChoicesEnum

    @classmethod
    def build(cls, subcategory: subcategories.Subcategory) -> "SubcategoryResponseModelv2":
        # A subcategory can be associated to more than one search group.
        # We keep it like this for backward compatibility.
        # This is sufficient for the app the behave correctly.
        search_group_name = next(
            search_group.search_value
            for search_group in SEARCH_GROUPS
            if subcategory.id in search_group.included_subcategories
        )
        # A subcategory can be associated to more than one native category.
        # We keep it like this for backward compatibility.
        # This is sufficient for the app the behave correctly.
        native_category_id = next(
            (
                native_category.search_value
                for native_category in NATIVE_CATEGORIES
                if subcategory.id in native_category.included_subcategories
            ),
            None,
        )
        return cls(
            id=subcategory.id,
            category_id=subcategory.category_id,
            native_category_id=native_category_id,
            app_label=subcategory.app_label,
            search_group_name=search_group_name,
            homepage_label_name=subcategory.homepage_label_name,
            is_event=subcategory.is_event,
            online_offline_platform=subcategory.online_offline_platform,
        )


class SearchGroupResponseModelv2(HttpBodyModel):
    name: str
    value: str | None = None


class HomepageLabelResponseModelv2(HttpBodyModel):
    name: str
    value: str | None = None


class NativeCategoryResponseModelv2(HttpBodyModel):
    name: str
    value: str | None = None
    genre_type: categories_models.GenreType | None = None
    parents: list[str]
    positions: dict[str, int] | None = None

    @classmethod
    def build(cls, nativeCategory: categories_models.SearchNode) -> "NativeCategoryResponseModelv2":
        parents = [parent.name for parent in nativeCategory.parents]
        return cls(
            name=nativeCategory.name,
            value=nativeCategory.value,
            genre_type=getattr(nativeCategory, "genre_type", None),
            parents=parents,
            positions=None if "LIVRES" in parents else nativeCategory.positions,
        )


class GenreTypeContentModel(HttpBodyModel):
    name: str
    value: str


class GenreTypeModel(HttpBodyModel):
    name: categories_models.GenreType
    values: list[GenreTypeContentModel]
    trees: list[BookType] | list[MusicType] | list[ShowType] | list[MovieType]


class SubcategoriesResponseModelv2(HttpBodyModel):
    subcategories: list[SubcategoryResponseModelv2]
    searchGroups: list[SearchGroupResponseModelv2]
    homepageLabels: list[HomepageLabelResponseModelv2]
    nativeCategories: list[NativeCategoryResponseModelv2]
    genreTypes: list[GenreTypeModel]


class CategoryResponseModel(HttpBodyModel):
    label: str
    parents: list[str]
    gtls: list[str] | None = None
    positions: dict[str, int] | None = None
    search_filter: str | None = None
    search_value: str | None = None

    @classmethod
    def build(cls, nativeCategory: categories_models.SearchNode) -> "CategoryResponseModel":
        parents = [parent.name for parent in nativeCategory.parents]
        return cls(
            label=nativeCategory.label,
            parents=parents,
            gtls=nativeCategory.gtls,
            positions=None if "LIVRES" in parents else nativeCategory.positions,
            search_filter=getattr(nativeCategory, "search_filter", None),
            search_value=nativeCategory.search_value,
        )


class CategoriesResponseModel(HttpBodyModel):
    categories: list[CategoryResponseModel]
