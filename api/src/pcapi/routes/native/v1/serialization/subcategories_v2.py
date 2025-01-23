from pcapi.core.categories import subcategories
from pcapi.domain.book_types import BookType
from pcapi.domain.movie_types import MovieType
from pcapi.domain.music_types import MusicType
from pcapi.domain.show_types import ShowType
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.serialization.utils import to_camel


class SubcategoryResponseModelv2(BaseModel):
    id: str
    category_id: str
    native_category_id: str
    app_label: str
    search_group_name: str
    homepage_label_name: str
    is_event: bool
    online_offline_platform: subcategories.OnlineOfflinePlatformChoicesEnumv2

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
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


class NativeCategoryResponseModelv2(BaseModel):
    name: str
    value: str | None
    genre_type: subcategories.GenreType | None
    parents: list[str]
    positions: dict[str, int] | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class GenreTypeContentModel(BaseModel):
    name: str
    value: str

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class GenreTypeModel(BaseModel):
    name: subcategories.GenreType
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
    id: str
    label: str
    parents: list[str]
    gtls: list[str] | None = None
    positions: dict[str, int] | None
    search_filter: str | None = None


class CategoriesResponseModel(ConfiguredBaseModel):
    categories: list[CategoryResponseModel]
