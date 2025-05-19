import itertools
import typing
from dataclasses import dataclass
from dataclasses import field
from enum import Enum

from pcapi.core.categories import pro_categories
from pcapi.core.categories.genres.book import BOOK_MACRO_SECTIONS
from pcapi.core.categories.genres.book import BOOK_TYPES
from pcapi.core.categories.genres.book import BookType
from pcapi.core.categories.genres.movie import MOVIE_TYPES
from pcapi.core.categories.genres.movie import MovieType
from pcapi.core.categories.genres.music import MUSIC_TYPES
from pcapi.core.categories.genres.music import MusicType
from pcapi.core.categories.genres.show import SHOW_TYPES
from pcapi.core.categories.genres.show import SHOW_TYPES_LABEL_BY_CODE
from pcapi.core.categories.genres.show import ShowType


class OnlineOfflinePlatformChoices(Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ONLINE_OR_OFFLINE = "ONLINE_OR_OFFLINE"


class HomepageLabels(Enum):
    BEAUX_ARTS = "Beaux-Arts"
    CARTE_JEUNES = "Carte jeunes"
    CINEMA = "Cinéma"
    CONCERT = "Concert"
    COURS = "Cours"
    FESTIVAL = "Festival"
    FILMS = "Films"
    INSTRUMENT = "Instrument"
    JEUX = "Jeux"
    LIVRES = "Livres"
    MEDIAS = "Médias"
    MUSEE = "Musée"
    MUSIQUE = "Musique"
    NONE = None
    PLATEFORME = "Plateforme"
    RENCONTRES = "Rencontres"
    SPECTACLES = "Spectacles"
    STAGE_ATELIER = "Stage, atelier"
    VISITES = "Visites"


class ReimbursementRuleChoices(Enum):
    STANDARD = "STANDARD"
    NOT_REIMBURSED = "NOT_REIMBURSED"
    BOOK = "BOOK"


class ExtraDataFieldEnum(Enum):
    AUTHOR = "author"
    EAN = "ean"
    MUSIC_SUB_TYPE = "musicSubType"
    MUSIC_TYPE = "musicType"
    PERFORMER = "performer"
    SHOW_SUB_TYPE = "showSubType"
    SHOW_TYPE = "showType"
    SPEAKER = "speaker"
    STAGE_DIRECTOR = "stageDirector"
    VISA = "visa"
    GTL_ID = "gtl_id"


@dataclass
class FieldCondition:
    is_required_in_external_form: bool = False
    is_required_in_internal_form: bool = False


class EacFormat(Enum):
    ATELIER_DE_PRATIQUE = "Atelier de pratique"
    CONCERT = "Concert"
    CONFERENCE_RENCONTRE = "Conférence, rencontre"
    FESTIVAL_SALON_CONGRES = "Festival, salon, congrès"
    PROJECTION_AUDIOVISUELLE = "Projection audiovisuelle"
    REPRESENTATION = "Représentation"
    VISITE_GUIDEE = "Visite guidée"
    VISITE_LIBRE = "Visite libre"


@dataclass(frozen=True)
class Subcategory:
    id: str
    category: pro_categories.Category
    pro_label: str
    app_label: str
    homepage_label_name: str
    is_event: bool
    conditional_fields: dict[str, FieldCondition]
    can_expire: bool
    # the booking amount will be substracted from physical cap
    is_physical_deposit: bool
    # the booking amount will be substracted from digital cap
    is_digital_deposit: bool
    online_offline_platform: str
    reimbursement_rule: str
    can_be_duo: bool
    can_have_opening_hours: bool = False
    # used by pc pro to build dropdown of subcategories during offer creation
    is_selectable: bool = True
    is_bookable_by_underage_when_free: bool = True
    is_bookable_by_underage_when_not_free: bool = True
    can_be_withdrawable: bool = False
    formats: typing.Sequence[EacFormat] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.homepage_label_name not in [h.name for h in HomepageLabels]:
            raise ValueError("homepage_label_name can only be one of HomepageLabels")
        if self.online_offline_platform not in [o.value for o in OnlineOfflinePlatformChoices]:
            raise ValueError("online_offline_platform can only be one of OnlineOfflinePlatformChoices")
        if self.reimbursement_rule not in [r.value for r in ReimbursementRuleChoices]:
            raise ValueError("reimbursement_rule can only be one of ReimbursementRuleChoices")

    @property
    def category_id(self) -> str:
        return self.category.id

    @property
    def is_offline_only(self) -> bool:
        return self.online_offline_platform == OnlineOfflinePlatformChoices.OFFLINE.value

    @property
    def is_online_only(self) -> bool:
        return self.online_offline_platform == OnlineOfflinePlatformChoices.ONLINE.value


@dataclass
class GenreTypeContent:
    name: str  # name used to index (Algolia)
    value: str  # value to display


class GenreType(Enum):
    BOOK = "BOOK"
    MUSIC = "MUSIC"
    SHOW = "SHOW"
    MOVIE = "MOVIE"

    @property
    def values(self) -> list[GenreTypeContent]:
        return {
            type(self).BOOK.name: self.book_values(),
            type(self).MUSIC.name: self.music_values(),
            type(self).SHOW.name: self.show_values(),
            type(self).MOVIE.name: self.movie_values(),
        }[self.name]

    @property
    def trees(self) -> list[BookType] | list[MovieType] | list[MusicType] | list[ShowType]:
        return {
            type(self).BOOK.name: BOOK_TYPES,
            type(self).MUSIC.name: MUSIC_TYPES,
            type(self).SHOW.name: SHOW_TYPES,
            type(self).MOVIE.name: MOVIE_TYPES,
        }[self.name]  # type: ignore[return-value]

    def book_values(self) -> list[GenreTypeContent]:
        return [GenreTypeContent(name=value, value=value) for value in sorted(BOOK_MACRO_SECTIONS)]

    def music_values(self) -> list[GenreTypeContent]:
        values = [GenreTypeContent(name=music_type.name, value=music_type.label) for music_type in MUSIC_TYPES]
        return sorted(values, key=lambda x: x.name)

    def show_values(self) -> list[GenreTypeContent]:
        return [GenreTypeContent(name=value, value=value) for value in sorted(SHOW_TYPES_LABEL_BY_CODE.values())]

    def movie_values(self) -> list[GenreTypeContent]:
        values = [GenreTypeContent(name=movie_type.name, value=movie_type.label) for movie_type in MOVIE_TYPES]
        return sorted(values, key=lambda x: x.value)


class SearchNode:
    def __init__(
        self,
        label: str,
        *,
        children: list["SearchNode"] | None = None,
        search_value: str | None = None,
        gtls: list[str] | None = None,
        included_subcategories: list[str] | None = None,
    ) -> None:
        self.included_subcategories = included_subcategories or []
        self.label = label
        self.gtls = gtls
        self.children = children or []
        self.search_value = search_value
        self.positions: dict[str, int] = {}
        self.parents: list["SearchNode"] = []

        for child in self.children:
            child.parents.append(self)
            if self.search_value:
                child.positions[self.search_value] = self.children.index(child)

        _register_node(self)

    @property
    def name(self) -> str:  # For retro-compatibility with route /subcategories_v2
        return self.search_value or self.label

    @property
    def value(self) -> str:  # For retro-compatibility with route /subcategories_v2
        return self.label


class SearchGroup(SearchNode):
    search_filter: str = "searchGroups"


class NativeCategory(SearchNode):
    search_filter: str = "nativeCategoryId"

    def __init__(self, *args: typing.Any, genre_type: GenreType | None = None, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.genre_type = genre_type


class BookGenre(SearchNode): ...


class MovieGenre(SearchNode):
    search_filter: str = "movieGenres"


class MusicGenre(SearchNode):
    search_filter: str = "musicType"


class ShowGenre(SearchNode):
    search_filter: str = "showType"


search_nodes: dict[str, list["SearchNode"]] = {}


def _register_node(obj: "SearchNode") -> None:
    class_name = obj.__class__.__name__
    if class_name not in search_nodes:
        search_nodes[class_name] = []

    search_nodes[class_name].append(obj)


def get_all_instances() -> list["SearchNode"]:
    return list(itertools.chain(*search_nodes.values()))


def get_search_groups() -> list["SearchNode"]:
    return search_nodes.get("SearchGroup", [])


def get_native_categories() -> list["SearchNode"]:
    return search_nodes.get("NativeCategory", [])
