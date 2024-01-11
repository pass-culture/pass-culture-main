from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.domain.book_types import BookType
from pcapi.domain.movie_types import MovieType
from pcapi.domain.music_types import MusicType
from pcapi.domain.show_types import ShowType
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class SubcategoryResponseModelv2(BaseModel):
    id: subcategories_v2.SubcategoryIdEnumv2
    category_id: categories.CategoryIdEnum
    native_category_id: subcategories_v2.NativeCategoryIdEnumv2
    app_label: str
    search_group_name: subcategories_v2.SearchGroupNameEnumv2
    homepage_label_name: subcategories_v2.HomepageLabelNameEnumv2
    is_event: bool
    online_offline_platform: subcategories_v2.OnlineOfflinePlatformChoicesEnumv2

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SearchGroupResponseModelv2(BaseModel):
    name: subcategories_v2.SearchGroupNameEnumv2
    value: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class HomepageLabelResponseModelv2(BaseModel):
    name: subcategories_v2.HomepageLabelNameEnumv2
    value: str | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class NativeCategoryResponseModelv2(BaseModel):
    name: subcategories_v2.NativeCategoryIdEnumv2
    value: str | None
    genre_type: subcategories_v2.GenreType | None

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
    name: subcategories_v2.GenreType
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
