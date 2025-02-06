from dataclasses import dataclass
from dataclasses import field
from enum import Enum
import typing
import uuid

from pcapi.core.categories import categories
from pcapi.domain.book_types import BOOK_MACRO_SECTIONS
from pcapi.domain.book_types import BOOK_TYPES
from pcapi.domain.book_types import BookType
from pcapi.domain.movie_types import MOVIE_TYPES
from pcapi.domain.movie_types import MovieType
from pcapi.domain.music_types import MUSIC_TYPES
from pcapi.domain.music_types import MusicType
from pcapi.domain.show_types import SHOW_TYPES
from pcapi.domain.show_types import SHOW_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import ShowType


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
        }[
            self.name
        ]  # type: ignore[return-value]

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
        parents: list[str] | None = None,
        technical_name: str | None = None,
        gtls: list[str] | None = None,
        positions: dict[str, int] | None = None,
    ) -> None:
        self.id = technical_name or str(uuid.uuid4())
        self.label = label
        self.gtls = gtls
        self.parents = parents or []
        self.positions = positions

    @property
    def search_value(self) -> str | None:
        return None


class SearchGroup(SearchNode):
    search_filter: str = "searchGroups"

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> "SearchGroup":
        obj = super().__new__(cls)
        if "instances" not in cls.__dict__:
            cls.instances = []

        cls.instances.append(obj)
        return obj

    @property
    def search_value(self) -> str | None:
        return self.id

    @property
    def name(self) -> str:  # For retro-compatibility with route /subcategories_v2
        return self.id

    @property
    def value(self) -> str:  # For retro-compatibility with route /subcategories_v2
        return self.label


class NativeCategory(SearchNode):
    search_filter: str = "nativeCategoryId"

    def __new__(cls, *args: typing.Any, **kwargs: typing.Any) -> "NativeCategory":
        obj = super().__new__(cls)
        if "instances" not in cls.__dict__:
            cls.instances = []

        cls.instances.append(obj)
        return obj

    def __init__(self, *args: typing.Any, genre_type: GenreType | None = None, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.genre_type = genre_type

    @property
    def search_value(self) -> str | None:
        return self.id

    @property
    def name(self) -> str:  # For retro-compatibility with route /subcategories_v2
        return self.id

    @property
    def value(self) -> str:  # For retro-compatibility with route /subcategories_v2
        return self.label


class BookGenre(SearchNode): ...


class MovieGenre(SearchNode):
    search_filter: str = "movieGenres"

    @property
    def search_value(self) -> str | None:
        return self.id


class MusicGenre(SearchNode):
    search_filter: str = "musicType"

    @property
    def search_value(self) -> str | None:
        return self.label


class ShowGenre(SearchNode):
    search_filter: str = "showType"

    @property
    def search_value(self) -> str | None:
        return self.label


def get_book_nodes() -> list[BookGenre]:
    nodes = []
    for book_type in BOOK_TYPES:
        parent = BookGenre(
            label=book_type.label,
            technical_name=book_type.label,
            gtls=[gtl.code for gtl in book_type.gtls],
            parents=[NATIVE_CATEGORY_LIVRES_PAPIER.id],
            positions={NATIVE_CATEGORY_LIVRES_PAPIER.id: book_type.position},
        )
        nodes.append(parent)
        for book_subtype in book_type.children:
            child = BookGenre(
                label=book_subtype.label,
                gtls=[gtl.code for gtl in book_subtype.gtls],
                parents=[parent.id],
                positions={parent.id: book_subtype.position},
            )
            nodes.append(child)

    return nodes


def get_movie_nodes() -> list[MovieGenre]:
    return [
        MovieGenre(
            label=movie_type.label,
            technical_name=movie_type.name,
            parents=[NATIVE_CATEGORY_SEANCES_DE_CINEMA.id],
        )
        for movie_type in MOVIE_TYPES
    ]


def get_music_nodes() -> list[MusicGenre]:
    return [
        MusicGenre(
            label=music_type.label,
            technical_name=music_type.name,
            parents=[
                NATIVE_CATEGORY_CD.id,
                NATIVE_CATEGORY_CONCERTS_EN_LIGNE.id,
                NATIVE_CATEGORY_CONCERTS_EVENEMENTS.id,
                NATIVE_CATEGORY_FESTIVALS.id,
                NATIVE_CATEGORY_MUSIQUE_EN_LIGNE.id,
                NATIVE_CATEGORY_VINYLES.id,
            ],
        )
        for music_type in MUSIC_TYPES
    ]


def get_show_nodes() -> list[ShowGenre]:
    return [
        ShowGenre(
            label=show_type.label,
            parents=[
                NATIVE_CATEGORY_ABONNEMENTS_SPECTACLE.id,
                NATIVE_CATEGORY_SPECTACLES_ENREGISTRES.id,
                NATIVE_CATEGORY_SPECTACLES_REPRESENTATIONS.id,
            ],
        )
        for show_type in SHOW_TYPES
    ]


# region SearchGroup
SEARCH_NODES_ROOT = SearchNode(label="Root")
SEARCH_GROUP_ARTS_LOISIRS_CREATIFS = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="ARTS_LOISIRS_CREATIFS",
    label="Arts & loisirs créatifs",
    positions={SEARCH_NODES_ROOT.id: 7},
)
SEARCH_GROUP_CARTES_JEUNES = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="CARTES_JEUNES",
    label="Cartes jeunes",
    positions={SEARCH_NODES_ROOT.id: 13},
)
# FIXME (thconte, 2024-10-15): Delete this SearchGroup once app's minimal version has bumped
SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="CD_VINYLE_MUSIQUE_EN_LIGNE",
    label="CD, vinyles, musique en ligne",
    positions={SEARCH_NODES_ROOT.id: 6},
)
SEARCH_GROUP_CONCERTS_FESTIVALS = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="CONCERTS_FESTIVALS",
    label="Concerts & festivals",
    positions={SEARCH_NODES_ROOT.id: 1},
)
SEARCH_GROUP_EVENEMENTS_EN_LIGNE = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="EVENEMENTS_EN_LIGNE",
    label="Évènements en ligne",
    positions={SEARCH_NODES_ROOT.id: 15},
)
# FIXME (thconte, 2024-10-03): Delete this SearchGroup once app's minimal version has bumped
SEARCH_GROUP_FILMS_SERIES_CINEMA = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="FILMS_SERIES_CINEMA",
    label="Cinéma, films et séries",
    positions={SEARCH_NODES_ROOT.id: 2},
)
SEARCH_GROUP_CINEMA = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="CINEMA",
    label="Cinéma",
    positions={SEARCH_NODES_ROOT.id: 2},
)
SEARCH_GROUP_FILMS_DOCUMENTAIRES_SERIES = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="FILMS_DOCUMENTAIRES_SERIES",
    label="Films, séries et documentaires",
    positions={SEARCH_NODES_ROOT.id: 3},
)
# FIXME (thconte, 2024-10-15): Delete this SearchGroup once app's minimal version has bumped
SEARCH_GROUP_INSTRUMENTS = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="INSTRUMENTS",
    label="Instruments de musique",
    positions={SEARCH_NODES_ROOT.id: 11},
)
SEARCH_GROUP_JEUX_JEUX_VIDEOS = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="JEUX_JEUX_VIDEOS",
    label="Jeux & jeux vidéos",
    positions={SEARCH_NODES_ROOT.id: 10},
)
SEARCH_GROUP_LIVRES = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="LIVRES",
    label="Livres",
    positions={SEARCH_NODES_ROOT.id: 4},
)
SEARCH_GROUP_MEDIA_PRESSE = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="MEDIA_PRESSE",
    label="Médias & presse",
    positions={SEARCH_NODES_ROOT.id: 12},
)
SEARCH_GROUP_MUSEES_VISITES_CULTURELLES = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="MUSEES_VISITES_CULTURELLES",
    label="Musées & visites culturelles",
    positions={SEARCH_NODES_ROOT.id: 9},
)
SEARCH_GROUP_MUSIQUE = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="MUSIQUE",
    label="Musique",
    positions={SEARCH_NODES_ROOT.id: 5},
)
SEARCH_GROUP_NONE = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="NONE",
    label="None",
)
SEARCH_GROUP_RENCONTRES_CONFERENCES = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="RENCONTRES_CONFERENCES",
    label="Conférences & rencontres",
    positions={SEARCH_NODES_ROOT.id: 14},
)
SEARCH_GROUP_SPECTACLES = SearchGroup(
    parents=[SEARCH_NODES_ROOT.id],
    technical_name="SPECTACLES",
    label="Spectacles",
    positions={SEARCH_NODES_ROOT.id: 8},
)
# endregion

# region NativeCategory
NATIVE_CATEGORY_ABO_PLATEFORME_VIDEO = NativeCategory(
    technical_name="ABO_PLATEFORME_VIDEO",
    label="Abonnements streaming",
    parents=[SEARCH_GROUP_FILMS_SERIES_CINEMA.id, SEARCH_GROUP_FILMS_DOCUMENTAIRES_SERIES.id],
)
NATIVE_CATEGORY_ABONNEMENTS_MUSEE = NativeCategory(
    technical_name="ABONNEMENTS_MUSEE",
    label="Abonnements musée",
    parents=[SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id],
)
NATIVE_CATEGORY_ABONNEMENTS_SPECTACLE = NativeCategory(
    technical_name="ABONNEMENTS_SPECTACLE",
    label="Abonnements spectacle",
    parents=[SEARCH_GROUP_SPECTACLES.id],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_ACHAT_LOCATION_INSTRUMENT = NativeCategory(
    technical_name="ACHAT_LOCATION_INSTRUMENT",
    label="Achat et location d'instruments",
    parents=[SEARCH_GROUP_INSTRUMENTS.id, SEARCH_GROUP_MUSIQUE.id],
    positions={SEARCH_GROUP_MUSIQUE.id: 6},
)
NATIVE_CATEGORY_ARTS_VISUELS = NativeCategory(
    technical_name="ARTS_VISUELS",
    label="Arts visuels",
    parents=[SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id],
)
NATIVE_CATEGORY_AUTRES_MEDIAS = NativeCategory(
    technical_name="AUTRES_MEDIAS",
    label="Autres médias",
    parents=[SEARCH_GROUP_MEDIA_PRESSE.id],
)
NATIVE_CATEGORY_BIBLIOTHEQUE_MEDIATHEQUE = NativeCategory(
    technical_name="BIBLIOTHEQUE_MEDIATHEQUE",
    label="Abonnements aux médiathèques et bibliothèques",
    parents=[SEARCH_GROUP_LIVRES.id],
)
NATIVE_CATEGORY_CARTES_CINEMA = NativeCategory(
    technical_name="CARTES_CINEMA",
    label="Cartes cinéma",
    parents=[SEARCH_GROUP_FILMS_SERIES_CINEMA.id, SEARCH_GROUP_CINEMA.id],
    positions={SEARCH_GROUP_CINEMA.id: 2},
)
NATIVE_CATEGORY_CD = NativeCategory(
    technical_name="CD",
    label="CDs",
    parents=[SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE.id, SEARCH_GROUP_MUSIQUE.id],
    genre_type=GenreType.MUSIC,
    positions={SEARCH_GROUP_MUSIQUE.id: 4},
)
NATIVE_CATEGORY_CONCERTS_EN_LIGNE = NativeCategory(
    technical_name="CONCERTS_EN_LIGNE",
    label="Concerts en ligne",
    parents=[SEARCH_GROUP_EVENEMENTS_EN_LIGNE.id],
    genre_type=GenreType.MUSIC,
)
NATIVE_CATEGORY_CONCERTS_EVENEMENTS = NativeCategory(
    technical_name="CONCERTS_EVENEMENTS",
    label="Concerts",
    parents=[SEARCH_GROUP_CONCERTS_FESTIVALS.id, SEARCH_GROUP_MUSIQUE.id],
    genre_type=GenreType.MUSIC,
    positions={SEARCH_GROUP_MUSIQUE.id: 2},
)
NATIVE_CATEGORY_CONCOURS = NativeCategory(
    technical_name="CONCOURS",
    label="Concours",
    parents=[SEARCH_GROUP_JEUX_JEUX_VIDEOS.id],
)
NATIVE_CATEGORY_CONFERENCES = NativeCategory(
    technical_name="CONFERENCES",
    label="Conférences",
    parents=[SEARCH_GROUP_RENCONTRES_CONFERENCES.id],
)
NATIVE_CATEGORY_DEPRECIEE = NativeCategory(
    technical_name="DEPRECIEE",
    label="Dépréciée",
    parents=[],
)
NATIVE_CATEGORY_DVD_BLU_RAY = NativeCategory(
    technical_name="DVD_BLU_RAY",
    label="DVD, Blu-Ray",
    parents=[SEARCH_GROUP_FILMS_SERIES_CINEMA.id, SEARCH_GROUP_FILMS_DOCUMENTAIRES_SERIES.id],
)
NATIVE_CATEGORY_ESCAPE_GAMES = NativeCategory(
    technical_name="ESCAPE_GAMES",
    label="Escape games",
    parents=[SEARCH_GROUP_JEUX_JEUX_VIDEOS.id],
)
NATIVE_CATEGORY_EVENEMENTS_CINEMA = NativeCategory(
    technical_name="EVENEMENTS_CINEMA",
    label="Evènements cinéma",
    parents=[SEARCH_GROUP_FILMS_SERIES_CINEMA.id, SEARCH_GROUP_CINEMA.id],
    positions={SEARCH_GROUP_CINEMA.id: 3},
)
NATIVE_CATEGORY_EVENEMENTS_PATRIMOINE = NativeCategory(
    technical_name="EVENEMENTS_PATRIMOINE",
    label="Evènements patrimoine",
    parents=[SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id],
)
NATIVE_CATEGORY_FESTIVALS = NativeCategory(
    technical_name="FESTIVALS",
    label="Festivals",
    parents=[SEARCH_GROUP_CONCERTS_FESTIVALS.id, SEARCH_GROUP_MUSIQUE.id],
    genre_type=GenreType.MUSIC,
    positions={SEARCH_GROUP_MUSIQUE.id: 3},
)
NATIVE_CATEGORY_FESTIVAL_DU_LIVRE = NativeCategory(
    technical_name="FESTIVAL_DU_LIVRE",
    label="Évènements autour du livre",
    parents=[SEARCH_GROUP_LIVRES.id],
)
NATIVE_CATEGORY_JEUX_EN_LIGNE = NativeCategory(
    technical_name="JEUX_EN_LIGNE",
    label="Jeux en ligne",
    parents=[SEARCH_GROUP_JEUX_JEUX_VIDEOS.id],
)
NATIVE_CATEGORY_JEUX_PHYSIQUES = NativeCategory(
    technical_name="JEUX_PHYSIQUES",
    label="Jeux physiques",
    parents=[],
)
NATIVE_CATEGORY_LIVRES_AUDIO_PHYSIQUES = NativeCategory(
    technical_name="LIVRES_AUDIO_PHYSIQUES",
    label="Livres audio",
    parents=[SEARCH_GROUP_LIVRES.id],
)
NATIVE_CATEGORY_LIVRES_NUMERIQUE_ET_AUDIO = NativeCategory(
    technical_name="LIVRES_NUMERIQUE_ET_AUDIO",
    label="E-books",
    parents=[SEARCH_GROUP_LIVRES.id],
)
NATIVE_CATEGORY_LIVRES_PAPIER = NativeCategory(
    technical_name="LIVRES_PAPIER",
    label="Livres papier",
    parents=[SEARCH_GROUP_LIVRES.id],
    genre_type=GenreType.BOOK,
)
NATIVE_CATEGORY_LUDOTHEQUE = NativeCategory(
    technical_name="LUDOTHEQUE",
    label="Ludothèque",
    parents=[SEARCH_GROUP_JEUX_JEUX_VIDEOS.id],
)
NATIVE_CATEGORY_MATERIELS_CREATIFS = NativeCategory(
    technical_name="MATERIELS_CREATIFS",
    label="Matériels créatifs",
    parents=[SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id],
)
NATIVE_CATEGORY_MUSIQUE_EN_LIGNE = NativeCategory(
    technical_name="MUSIQUE_EN_LIGNE",
    label="Musique en ligne",
    parents=[SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE.id, SEARCH_GROUP_MUSIQUE.id],
    genre_type=GenreType.MUSIC,
    positions={SEARCH_GROUP_MUSIQUE.id: 1},
)
NATIVE_CATEGORY_NONE = NativeCategory(technical_name="NATIVE_CATEGORY_NONE", label="None", parents=[])
NATIVE_CATEGORY_PARTITIONS_DE_MUSIQUE = NativeCategory(
    technical_name="PARTITIONS_DE_MUSIQUE",
    label="Partitions de musique",
    parents=[SEARCH_GROUP_INSTRUMENTS.id, SEARCH_GROUP_MUSIQUE.id],
    positions={SEARCH_GROUP_MUSIQUE.id: 7},
)
NATIVE_CATEGORY_PODCAST = NativeCategory(
    technical_name="PODCAST",
    label="Podcast",
    parents=[SEARCH_GROUP_MEDIA_PRESSE.id],
)
NATIVE_CATEGORY_PRATIQUES_ET_ATELIERS_ARTISTIQUES = NativeCategory(
    technical_name="PRATIQUES_ET_ATELIERS_ARTISTIQUES",
    label="Pratiques & ateliers artistiques",
    parents=[SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id],
)
NATIVE_CATEGORY_PRATIQUE_ARTISTIQUE_EN_LIGNE = NativeCategory(
    technical_name="PRATIQUE_ARTISTIQUE_EN_LIGNE",
    label="Pratique artistique en ligne",
    parents=[
        SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
        SEARCH_GROUP_EVENEMENTS_EN_LIGNE.id,
    ],
)
NATIVE_CATEGORY_PRESSE_EN_LIGNE = NativeCategory(
    technical_name="PRESSE_EN_LIGNE",
    label="Presse en ligne",
    parents=[SEARCH_GROUP_MEDIA_PRESSE.id],
)
NATIVE_CATEGORY_RENCONTRES = NativeCategory(
    technical_name="RENCONTRES",
    label="Rencontres",
    parents=[SEARCH_GROUP_RENCONTRES_CONFERENCES.id],
)
NATIVE_CATEGORY_RENCONTRES_EN_LIGNE = NativeCategory(
    technical_name="RENCONTRES_EN_LIGNE",
    label="Rencontres en ligne",
    parents=[
        SEARCH_GROUP_EVENEMENTS_EN_LIGNE.id,
        SEARCH_GROUP_RENCONTRES_CONFERENCES.id,
    ],
)
NATIVE_CATEGORY_RENCONTRES_EVENEMENTS = NativeCategory(
    technical_name="RENCONTRES_EVENEMENTS",
    label="Rencontres évènements",
    parents=[SEARCH_GROUP_JEUX_JEUX_VIDEOS.id],
)
NATIVE_CATEGORY_SALONS_ET_METIERS = NativeCategory(
    technical_name="SALONS_ET_METIERS",
    label="Salons & métiers",
    parents=[SEARCH_GROUP_RENCONTRES_CONFERENCES.id],
)
NATIVE_CATEGORY_SEANCES_DE_CINEMA = NativeCategory(
    technical_name="SEANCES_DE_CINEMA",
    label="Films à l'affiche",
    parents=[SEARCH_GROUP_FILMS_SERIES_CINEMA.id, SEARCH_GROUP_CINEMA.id],
    positions={SEARCH_GROUP_CINEMA.id: 1},
    genre_type=GenreType.MOVIE,
)
NATIVE_CATEGORY_SPECTACLES_ENREGISTRES = NativeCategory(
    technical_name="SPECTACLES_ENREGISTRES",
    label="Spectacles enregistrés",
    parents=[SEARCH_GROUP_SPECTACLES.id],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_SPECTACLES_REPRESENTATIONS = NativeCategory(
    technical_name="SPECTACLES_REPRESENTATIONS",
    label="Spectacles & représentations",
    parents=[SEARCH_GROUP_SPECTACLES.id],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_VIDEOS_ET_DOCUMENTAIRES = NativeCategory(
    technical_name="VIDEOS_ET_DOCUMENTAIRES",
    label="Vidéos et documentaires",
    parents=[SEARCH_GROUP_FILMS_SERIES_CINEMA.id, SEARCH_GROUP_FILMS_DOCUMENTAIRES_SERIES.id],
)
NATIVE_CATEGORY_VINYLES = NativeCategory(
    technical_name="VINYLES",
    label="Vinyles",
    parents=[SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE.id, SEARCH_GROUP_MUSIQUE.id],
    genre_type=GenreType.MUSIC,
    positions={SEARCH_GROUP_MUSIQUE.id: 5},
)
NATIVE_CATEGORY_VISITES_CULTURELLES = NativeCategory(
    technical_name="VISITES_CULTURELLES",
    label="Visites culturelles",
    parents=[SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id],
)
NATIVE_CATEGORY_VISITES_CULTURELLES_EN_LIGNE = NativeCategory(
    technical_name="VISITES_CULTURELLES_EN_LIGNE",
    label="Visites culturelles en ligne",
    parents=[SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id],
)
# endregion

SEARCH_GROUPS: list[SearchGroup] = list(SearchGroup.instances)
NATIVE_CATEGORIES: list[NativeCategory] = list(NativeCategory.instances)
BOOK_GENRES: list[BookGenre] = get_book_nodes()
MOVIE_GENRES: list[MovieGenre] = get_movie_nodes()
MUSIC_GENRES: list[MusicGenre] = get_music_nodes()
SHOW_GENRES: list[ShowGenre] = get_show_nodes()

SEARCH_NODES = SEARCH_GROUPS + NATIVE_CATEGORIES + BOOK_GENRES + MOVIE_GENRES + MUSIC_GENRES + SHOW_GENRES


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
    category: categories.Category
    native_category: NativeCategory
    pro_label: str
    app_label: str
    search_group_name: str
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
    can_be_educational: bool
    # used by pc pro to build dropdown of subcategories during offer creation
    is_selectable: bool = True
    is_bookable_by_underage_when_free: bool = True
    is_bookable_by_underage_when_not_free: bool = True
    can_be_withdrawable: bool = False
    formats: typing.Sequence[EacFormat] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.search_group_name not in [s.id for s in SEARCH_GROUPS]:
            raise ValueError("search_group_name can only be one of SearchGroups")
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
    def native_category_id(self) -> str:
        return self.native_category.id

    @property
    def is_offline_only(self) -> bool:
        return self.online_offline_platform == OnlineOfflinePlatformChoices.OFFLINE.value

    @property
    def is_online_only(self) -> bool:
        return self.online_offline_platform == OnlineOfflinePlatformChoices.ONLINE.value


# region Subcategories declarations
# region FILM
SUPPORT_PHYSIQUE_FILM = Subcategory(
    id="SUPPORT_PHYSIQUE_FILM",
    category=categories.FILM,
    native_category=NATIVE_CATEGORY_DVD_BLU_RAY,
    pro_label="Support physique (DVD, Blu-ray...)",
    app_label="Support physique (DVD, Blu-ray...)",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
ABO_MEDIATHEQUE = Subcategory(
    id="ABO_MEDIATHEQUE",
    category=categories.FILM,
    native_category=NATIVE_CATEGORY_BIBLIOTHEQUE_MEDIATHEQUE,
    pro_label="Abonnement médiathèque",
    app_label="Abonnement médiathèque",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
VOD = Subcategory(
    id="VOD",
    category=categories.FILM,
    native_category=NATIVE_CATEGORY_VIDEOS_ET_DOCUMENTAIRES,
    pro_label="Vidéo à la demande",
    app_label="Vidéo à la demande",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
ABO_PLATEFORME_VIDEO = Subcategory(
    id="ABO_PLATEFORME_VIDEO",
    category=categories.FILM,
    native_category=NATIVE_CATEGORY_ABO_PLATEFORME_VIDEO,
    pro_label="Abonnement plateforme streaming",
    app_label="Abonnement plateforme streaming",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
AUTRE_SUPPORT_NUMERIQUE = Subcategory(
    id="AUTRE_SUPPORT_NUMERIQUE",
    category=categories.FILM,
    native_category=NATIVE_CATEGORY_VIDEOS_ET_DOCUMENTAIRES,
    pro_label="Autre support numérique",
    app_label="Autre support numérique",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# region CINEMA
CARTE_CINE_MULTISEANCES = Subcategory(
    id="CARTE_CINE_MULTISEANCES",
    category=categories.CINEMA,
    native_category=NATIVE_CATEGORY_CARTES_CINEMA,
    pro_label="Carte cinéma multi-séances",
    app_label="Carte cinéma multi-séances",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
CARTE_CINE_ILLIMITE = Subcategory(
    id="CARTE_CINE_ILLIMITE",
    category=categories.CINEMA,
    native_category=NATIVE_CATEGORY_CARTES_CINEMA,
    pro_label="Carte cinéma illimité",
    app_label="Carte cinéma illimité",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
SEANCE_CINE = Subcategory(
    id="SEANCE_CINE",
    category=categories.CINEMA,
    native_category=NATIVE_CATEGORY_SEANCES_DE_CINEMA,
    pro_label="Séance de cinéma",
    app_label="Séance de cinéma",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
)
EVENEMENT_CINE = Subcategory(
    id="EVENEMENT_CINE",
    category=categories.CINEMA,
    native_category=NATIVE_CATEGORY_EVENEMENTS_CINEMA,
    pro_label="Évènement cinématographique",
    app_label="Évènement cinéma",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
)
FESTIVAL_CINE = Subcategory(
    id="FESTIVAL_CINE",
    category=categories.CINEMA,
    native_category=NATIVE_CATEGORY_EVENEMENTS_CINEMA,
    pro_label="Festival de cinéma",
    app_label="Festival de cinéma",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES, EacFormat.PROJECTION_AUDIOVISUELLE],
)
CINE_VENTE_DISTANCE = Subcategory(
    id="CINE_VENTE_DISTANCE",
    category=categories.CINEMA,
    native_category=NATIVE_CATEGORY_CARTES_CINEMA,
    pro_label="Cinéma vente à distance",
    app_label="Cinéma",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)

CINE_PLEIN_AIR = Subcategory(
    id="CINE_PLEIN_AIR",
    category=categories.CINEMA,
    native_category=NATIVE_CATEGORY_SEANCES_DE_CINEMA,
    pro_label="Cinéma plein air",
    app_label="Cinéma plein air",
    search_group_name=SEARCH_GROUP_FILMS_SERIES_CINEMA.id,
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
)

# endregion
# region CONFERENCE

CONFERENCE = Subcategory(
    id="CONFERENCE",
    category=categories.CONFERENCE_RENCONTRE,
    native_category=NATIVE_CATEGORY_CONFERENCES,
    pro_label="Conférence",
    app_label="Conférence",
    search_group_name=SEARCH_GROUP_RENCONTRES_CONFERENCES.id,
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.CONFERENCE_RENCONTRE],
)
RENCONTRE = Subcategory(
    id="RENCONTRE",
    category=categories.CONFERENCE_RENCONTRE,
    native_category=NATIVE_CATEGORY_RENCONTRES,
    pro_label="Rencontre",
    app_label="Rencontre",
    search_group_name=SEARCH_GROUP_RENCONTRES_CONFERENCES.id,
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.CONFERENCE_RENCONTRE],
)
DECOUVERTE_METIERS = Subcategory(
    id="DECOUVERTE_METIERS",
    category=categories.CONFERENCE_RENCONTRE,
    native_category=NATIVE_CATEGORY_SALONS_ET_METIERS,
    pro_label="Découverte des métiers",
    app_label="Découverte des métiers",
    search_group_name=SEARCH_GROUP_RENCONTRES_CONFERENCES.id,
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_selectable=False,
)
SALON = Subcategory(
    id="SALON",
    category=categories.CONFERENCE_RENCONTRE,
    native_category=NATIVE_CATEGORY_SALONS_ET_METIERS,
    pro_label="Salon, Convention",
    app_label="Salon, Convention",
    search_group_name=SEARCH_GROUP_RENCONTRES_CONFERENCES.id,
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES],
)
RENCONTRE_EN_LIGNE = Subcategory(
    id="RENCONTRE_EN_LIGNE",
    category=categories.CONFERENCE_RENCONTRE,
    native_category=NATIVE_CATEGORY_RENCONTRES_EN_LIGNE,
    pro_label="Rencontre en ligne",
    app_label="Rencontre en ligne",
    search_group_name=SEARCH_GROUP_RENCONTRES_CONFERENCES.id,
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
    formats=[EacFormat.CONFERENCE_RENCONTRE],
)
# endregion
# region JEU
CONCOURS = Subcategory(
    id="CONCOURS",
    category=categories.JEU,
    native_category=NATIVE_CATEGORY_CONCOURS,
    pro_label="Concours - jeux",
    app_label="Concours - jeux",
    search_group_name=SEARCH_GROUP_JEUX_JEUX_VIDEOS.id,
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
RENCONTRE_JEU = Subcategory(
    id="RENCONTRE_JEU",
    category=categories.JEU,
    native_category=NATIVE_CATEGORY_RENCONTRES_EVENEMENTS,
    pro_label="Rencontres - jeux",
    app_label="Rencontres - jeux",
    search_group_name=SEARCH_GROUP_JEUX_JEUX_VIDEOS.id,
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
ESCAPE_GAME = Subcategory(
    id="ESCAPE_GAME",
    category=categories.JEU,
    native_category=NATIVE_CATEGORY_ESCAPE_GAMES,
    pro_label="Escape game",
    app_label="Escape game",
    search_group_name=SEARCH_GROUP_JEUX_JEUX_VIDEOS.id,
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
EVENEMENT_JEU = Subcategory(
    id="EVENEMENT_JEU",
    category=categories.JEU,
    native_category=NATIVE_CATEGORY_RENCONTRES_EVENEMENTS,
    pro_label="Évènements - jeux",
    app_label="Évènements - jeux",
    search_group_name=SEARCH_GROUP_JEUX_JEUX_VIDEOS.id,
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
JEU_EN_LIGNE = Subcategory(
    id="JEU_EN_LIGNE",
    category=categories.JEU,
    native_category=NATIVE_CATEGORY_JEUX_EN_LIGNE,
    pro_label="Jeux en ligne",
    app_label="Jeux en ligne",
    search_group_name=SEARCH_GROUP_JEUX_JEUX_VIDEOS.id,
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
ABO_JEU_VIDEO = Subcategory(
    id="ABO_JEU_VIDEO",
    category=categories.JEU,
    native_category=NATIVE_CATEGORY_JEUX_EN_LIGNE,
    pro_label="Abonnement jeux vidéos",
    app_label="Abonnement jeux vidéos",
    search_group_name=SEARCH_GROUP_JEUX_JEUX_VIDEOS.id,
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
ABO_LUDOTHEQUE = Subcategory(
    id="ABO_LUDOTHEQUE",
    category=categories.JEU,
    native_category=NATIVE_CATEGORY_LUDOTHEQUE,
    pro_label="Abonnement ludothèque",
    app_label="Abonnement ludothèque",
    search_group_name=SEARCH_GROUP_JEUX_JEUX_VIDEOS.id,
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_selectable=False,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# region LIVRE

LIVRE_PAPIER = Subcategory(
    id="LIVRE_PAPIER",
    category=categories.LIVRE,
    native_category=NATIVE_CATEGORY_LIVRES_PAPIER,
    pro_label="Livre papier",
    app_label="Livre",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.BOOK.value,
)
LIVRE_NUMERIQUE = Subcategory(
    id="LIVRE_NUMERIQUE",
    category=categories.LIVRE,
    native_category=NATIVE_CATEGORY_LIVRES_NUMERIQUE_ET_AUDIO,
    pro_label="Livre numérique, e-book",
    app_label="Livre numérique, e-book",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.BOOK.value,
    is_bookable_by_underage_when_not_free=True,
)
TELECHARGEMENT_LIVRE_AUDIO = Subcategory(
    id="TELECHARGEMENT_LIVRE_AUDIO",
    category=categories.LIVRE,
    native_category=NATIVE_CATEGORY_LIVRES_NUMERIQUE_ET_AUDIO,
    pro_label="Livre audio à télécharger",
    app_label="Livre audio à télécharger",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
LIVRE_AUDIO_PHYSIQUE = Subcategory(
    id="LIVRE_AUDIO_PHYSIQUE",
    category=categories.LIVRE,
    native_category=NATIVE_CATEGORY_LIVRES_AUDIO_PHYSIQUES,
    pro_label="Livre audio sur support physique",
    app_label="Livre audio sur support physique",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)
ABO_BIBLIOTHEQUE = Subcategory(
    id="ABO_BIBLIOTHEQUE",
    category=categories.LIVRE,
    native_category=NATIVE_CATEGORY_BIBLIOTHEQUE_MEDIATHEQUE,
    pro_label="Abonnement (bibliothèques, médiathèques...)",
    app_label="Abonnement (bibliothèques, médiathèques...)",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
ABO_LIVRE_NUMERIQUE = Subcategory(
    id="ABO_LIVRE_NUMERIQUE",
    category=categories.LIVRE,
    native_category=NATIVE_CATEGORY_LIVRES_NUMERIQUE_ET_AUDIO,
    pro_label="Abonnement livres numériques",
    app_label="Abonnement livres numériques",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.BOOK.value,
    is_bookable_by_underage_when_not_free=True,
)
FESTIVAL_LIVRE = Subcategory(
    id="FESTIVAL_LIVRE",
    category=categories.LIVRE,
    native_category=NATIVE_CATEGORY_FESTIVAL_DU_LIVRE,
    pro_label="Festival et salon du livre",
    app_label="Festival et salon du livre",
    search_group_name=SEARCH_GROUP_LIVRES.id,
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
CARTE_JEUNES = Subcategory(
    id="CARTE_JEUNES",
    category=categories.CARTE_JEUNES,
    native_category=NATIVE_CATEGORY_NONE,
    pro_label="Carte jeunes",
    app_label="Carte jeunes",
    search_group_name=SEARCH_GROUP_CARTES_JEUNES.id,
    homepage_label_name=HomepageLabels.CARTE_JEUNES.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)
# endregion
# region VISITE

CARTE_MUSEE = Subcategory(
    id="CARTE_MUSEE",
    category=categories.MUSEE,
    native_category=NATIVE_CATEGORY_ABONNEMENTS_MUSEE,
    pro_label="Abonnement musée, carte ou pass",
    app_label="Abonnement musée, carte ou pass",
    search_group_name=SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id,
    homepage_label_name=HomepageLabels.MUSEE.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=True,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)

VISITE = Subcategory(
    id="VISITE",
    category=categories.MUSEE,
    native_category=NATIVE_CATEGORY_VISITES_CULTURELLES,
    pro_label="Visite",
    app_label="Visite",
    search_group_name=SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id,
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.VISITE_LIBRE],
)
VISITE_GUIDEE = Subcategory(
    id="VISITE_GUIDEE",
    category=categories.MUSEE,
    native_category=NATIVE_CATEGORY_VISITES_CULTURELLES,
    pro_label="Visite guidée",
    app_label="Visite guidée",
    search_group_name=SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id,
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.VISITE_GUIDEE],
)
EVENEMENT_PATRIMOINE = Subcategory(
    id="EVENEMENT_PATRIMOINE",
    category=categories.MUSEE,
    native_category=NATIVE_CATEGORY_EVENEMENTS_PATRIMOINE,
    pro_label="Évènement et atelier patrimoine",
    app_label="Évènement et atelier patrimoine",
    search_group_name=SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id,
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
VISITE_VIRTUELLE = Subcategory(
    id="VISITE_VIRTUELLE",
    category=categories.MUSEE,
    native_category=NATIVE_CATEGORY_VISITES_CULTURELLES_EN_LIGNE,
    pro_label="Visite virtuelle",
    app_label="Visite virtuelle",
    search_group_name=SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id,
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
MUSEE_VENTE_DISTANCE = Subcategory(
    id="MUSEE_VENTE_DISTANCE",
    category=categories.MUSEE,
    native_category=NATIVE_CATEGORY_VISITES_CULTURELLES,
    pro_label="Musée vente à distance",
    app_label="Musée vente à distance",
    search_group_name=SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id,
    homepage_label_name=HomepageLabels.MUSEE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)
FESTIVAL_ART_VISUEL = Subcategory(
    id="FESTIVAL_ART_VISUEL",
    category=categories.MUSEE,
    native_category=NATIVE_CATEGORY_ARTS_VISUELS,
    pro_label="Festival d'arts visuels / arts numériques",
    app_label="Festival d'arts visuels / arts numériques",
    search_group_name=SEARCH_GROUP_MUSEES_VISITES_CULTURELLES.id,
    homepage_label_name=HomepageLabels.FESTIVAL.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES],
)
# endregion
# region MUSIQUE_LIVE

CONCERT = Subcategory(
    id="CONCERT",
    category=categories.MUSIQUE_LIVE,
    native_category=NATIVE_CATEGORY_CONCERTS_EVENEMENTS,
    pro_label="Concert",
    app_label="Concert",
    search_group_name=SEARCH_GROUP_CONCERTS_FESTIVALS.id,
    homepage_label_name=HomepageLabels.CONCERT.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.CONCERT],
)
EVENEMENT_MUSIQUE = Subcategory(
    id="EVENEMENT_MUSIQUE",
    category=categories.MUSIQUE_LIVE,
    native_category=NATIVE_CATEGORY_CONCERTS_EVENEMENTS,
    pro_label="Autre type d'évènement musical",
    app_label="Autre type d'évènement musical",
    search_group_name=SEARCH_GROUP_CONCERTS_FESTIVALS.id,
    homepage_label_name=HomepageLabels.CONCERT.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.CONCERT],
)
LIVESTREAM_MUSIQUE = Subcategory(
    id="LIVESTREAM_MUSIQUE",
    category=categories.MUSIQUE_LIVE,
    native_category=NATIVE_CATEGORY_CONCERTS_EN_LIGNE,
    pro_label="Livestream musical",
    app_label="Livestream musical",
    search_group_name=SEARCH_GROUP_EVENEMENTS_EN_LIGNE.id,
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=False,
)
ABO_CONCERT = Subcategory(
    id="ABO_CONCERT",
    category=categories.MUSIQUE_LIVE,
    native_category=NATIVE_CATEGORY_CONCERTS_EVENEMENTS,
    pro_label="Abonnement concert",
    app_label="Abonnement concert",
    search_group_name=SEARCH_GROUP_CONCERTS_FESTIVALS.id,
    homepage_label_name=HomepageLabels.CONCERT.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
FESTIVAL_MUSIQUE = Subcategory(
    id="FESTIVAL_MUSIQUE",
    category=categories.MUSIQUE_LIVE,
    native_category=NATIVE_CATEGORY_FESTIVALS,
    pro_label="Festival de musique",
    app_label="Festival de musique",
    search_group_name=SEARCH_GROUP_CONCERTS_FESTIVALS.id,
    homepage_label_name=HomepageLabels.FESTIVAL.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES, EacFormat.CONCERT],
)
# endregion
# region MUSIQUE_ENREGISTREE
SUPPORT_PHYSIQUE_MUSIQUE_CD = Subcategory(
    id="SUPPORT_PHYSIQUE_MUSIQUE_CD",
    category=categories.MUSIQUE_ENREGISTREE,
    native_category=NATIVE_CATEGORY_CD,
    pro_label="CD",
    app_label="CD",
    search_group_name=SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE.id,
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
SUPPORT_PHYSIQUE_MUSIQUE_VINYLE = Subcategory(
    id="SUPPORT_PHYSIQUE_MUSIQUE_VINYLE",
    category=categories.MUSIQUE_ENREGISTREE,
    native_category=NATIVE_CATEGORY_VINYLES,
    pro_label="Vinyles et autres supports",
    app_label="Vinyles et autres supports",
    search_group_name=SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE.id,
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
TELECHARGEMENT_MUSIQUE = Subcategory(
    id="TELECHARGEMENT_MUSIQUE",
    category=categories.MUSIQUE_ENREGISTREE,
    native_category=NATIVE_CATEGORY_MUSIQUE_EN_LIGNE,
    pro_label="Téléchargement de musique",
    app_label="Téléchargement de musique",
    search_group_name=SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE.id,
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
ABO_PLATEFORME_MUSIQUE = Subcategory(
    id="ABO_PLATEFORME_MUSIQUE",
    category=categories.MUSIQUE_ENREGISTREE,
    native_category=NATIVE_CATEGORY_MUSIQUE_EN_LIGNE,
    pro_label="Abonnement plateforme musicale",
    app_label="Abonnement plateforme musicale",
    search_group_name=SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE.id,
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
CAPTATION_MUSIQUE = Subcategory(
    id="CAPTATION_MUSIQUE",
    category=categories.MUSIQUE_ENREGISTREE,
    native_category=NATIVE_CATEGORY_PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Captation musicale",
    app_label="Captation musicale",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
)

# endregion
# region PRATIQUE
SEANCE_ESSAI_PRATIQUE_ART = Subcategory(
    id="SEANCE_ESSAI_PRATIQUE_ART",
    category=categories.PRATIQUE_ART,
    native_category=NATIVE_CATEGORY_PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Séance d'essai",
    app_label="Séance d'essai",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.STAGE_ATELIER.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=True,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
ATELIER_PRATIQUE_ART = Subcategory(
    id="ATELIER_PRATIQUE_ART",
    category=categories.PRATIQUE_ART,
    native_category=NATIVE_CATEGORY_PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Atelier, stage de pratique artistique",
    app_label="Atelier, stage de pratique artistique",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.STAGE_ATELIER.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
ABO_PRATIQUE_ART = Subcategory(
    id="ABO_PRATIQUE_ART",
    category=categories.PRATIQUE_ART,
    native_category=NATIVE_CATEGORY_PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Abonnement pratique artistique",
    app_label="Abonnement pratique artistique",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.COURS.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
PRATIQUE_ART_VENTE_DISTANCE = Subcategory(
    id="PRATIQUE_ART_VENTE_DISTANCE",
    category=categories.PRATIQUE_ART,
    native_category=NATIVE_CATEGORY_PRATIQUE_ARTISTIQUE_EN_LIGNE,
    pro_label="Pratique artistique - vente à distance",
    app_label="Pratique artistique - vente à distance",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.COURS.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
PLATEFORME_PRATIQUE_ARTISTIQUE = Subcategory(
    id="PLATEFORME_PRATIQUE_ARTISTIQUE",
    category=categories.PRATIQUE_ART,
    native_category=NATIVE_CATEGORY_PRATIQUE_ARTISTIQUE_EN_LIGNE,
    pro_label="Pratique artistique - plateforme en ligne",
    app_label="Plateforme de pratique artistique",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.PLATEFORME.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
LIVESTREAM_PRATIQUE_ARTISTIQUE = Subcategory(
    id="LIVESTREAM_PRATIQUE_ARTISTIQUE",
    category=categories.PRATIQUE_ART,
    native_category=NATIVE_CATEGORY_PRATIQUE_ARTISTIQUE_EN_LIGNE,
    pro_label="Pratique artistique - livestream",
    app_label="Pratique artistique - livestream",
    search_group_name=SEARCH_GROUP_EVENEMENTS_EN_LIGNE.id,
    homepage_label_name=HomepageLabels.COURS.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# region MEDIAS
ABO_PRESSE_EN_LIGNE = Subcategory(
    id="ABO_PRESSE_EN_LIGNE",
    category=categories.MEDIA,
    native_category=NATIVE_CATEGORY_PRESSE_EN_LIGNE,
    pro_label="Abonnement presse en ligne",
    app_label="Abonnement presse en ligne",
    search_group_name=SEARCH_GROUP_MEDIA_PRESSE.id,
    homepage_label_name=HomepageLabels.MEDIAS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
PODCAST = Subcategory(
    id="PODCAST",
    category=categories.MEDIA,
    native_category=NATIVE_CATEGORY_PODCAST,
    pro_label="Podcast",
    app_label="Podcast",
    search_group_name=SEARCH_GROUP_MEDIA_PRESSE.id,
    homepage_label_name=HomepageLabels.MEDIAS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
APP_CULTURELLE = Subcategory(
    id="APP_CULTURELLE",
    category=categories.MEDIA,
    native_category=NATIVE_CATEGORY_AUTRES_MEDIAS,
    pro_label="Application culturelle",
    app_label="Application culturelle",
    search_group_name=SEARCH_GROUP_MEDIA_PRESSE.id,
    homepage_label_name=HomepageLabels.MEDIAS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
# endregion
# region SPECTACLE
SPECTACLE_REPRESENTATION = Subcategory(
    id="SPECTACLE_REPRESENTATION",
    category=categories.SPECTACLE,
    native_category=NATIVE_CATEGORY_SPECTACLES_REPRESENTATIONS,
    pro_label="Spectacle, représentation",
    app_label="Spectacle, représentation",
    search_group_name=SEARCH_GROUP_SPECTACLES.id,
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.REPRESENTATION],
)
SPECTACLE_ENREGISTRE = Subcategory(
    id="SPECTACLE_ENREGISTRE",
    category=categories.SPECTACLE,
    native_category=NATIVE_CATEGORY_SPECTACLES_ENREGISTRES,
    pro_label="Spectacle enregistré",
    app_label="Spectacle enregistré",
    search_group_name=SEARCH_GROUP_SPECTACLES.id,
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
LIVESTREAM_EVENEMENT = Subcategory(
    id="LIVESTREAM_EVENEMENT",
    category=categories.SPECTACLE,
    native_category=NATIVE_CATEGORY_RENCONTRES_EN_LIGNE,
    pro_label="Livestream d'évènement",
    app_label="Livestream d'évènement",
    search_group_name=SEARCH_GROUP_EVENEMENTS_EN_LIGNE.id,
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=False,
)
FESTIVAL_SPECTACLE = Subcategory(
    id="FESTIVAL_SPECTACLE",
    category=categories.SPECTACLE,
    native_category=NATIVE_CATEGORY_SPECTACLES_REPRESENTATIONS,
    pro_label="Festival de spectacle vivant",
    app_label="Festival de spectacle vivant",
    search_group_name=SEARCH_GROUP_SPECTACLES.id,
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES, EacFormat.REPRESENTATION],
)
ABO_SPECTACLE = Subcategory(
    id="ABO_SPECTACLE",
    category=categories.SPECTACLE,
    native_category=NATIVE_CATEGORY_ABONNEMENTS_SPECTACLE,
    pro_label="Abonnement spectacle",
    app_label="Abonnement spectacle",
    search_group_name=SEARCH_GROUP_SPECTACLES.id,
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
SPECTACLE_VENTE_DISTANCE = Subcategory(
    id="SPECTACLE_VENTE_DISTANCE",
    category=categories.SPECTACLE,
    native_category=NATIVE_CATEGORY_SPECTACLES_REPRESENTATIONS,
    pro_label="Spectacle vivant - vente à distance",
    app_label="Spectacle vivant - vente à distance",
    search_group_name=SEARCH_GROUP_SPECTACLES.id,
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
# endregion
# region INSTRUMENT
ACHAT_INSTRUMENT = Subcategory(
    id="ACHAT_INSTRUMENT",
    category=categories.INSTRUMENT,
    native_category=NATIVE_CATEGORY_ACHAT_LOCATION_INSTRUMENT,
    pro_label="Achat instrument",
    app_label="Achat instrument",
    search_group_name=SEARCH_GROUP_INSTRUMENTS.id,
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
BON_ACHAT_INSTRUMENT = Subcategory(
    id="BON_ACHAT_INSTRUMENT",
    pro_label="Bon d'achat instrument",
    category=categories.INSTRUMENT,
    native_category=NATIVE_CATEGORY_ACHAT_LOCATION_INSTRUMENT,
    app_label="Bon d'achat instrument",
    search_group_name=SEARCH_GROUP_INSTRUMENTS.id,
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_selectable=False,
)
LOCATION_INSTRUMENT = Subcategory(
    id="LOCATION_INSTRUMENT",
    category=categories.INSTRUMENT,
    native_category=NATIVE_CATEGORY_ACHAT_LOCATION_INSTRUMENT,
    pro_label="Location instrument",
    app_label="Location instrument",
    search_group_name=SEARCH_GROUP_INSTRUMENTS.id,
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
PARTITION = Subcategory(
    id="PARTITION",
    category=categories.INSTRUMENT,
    native_category=NATIVE_CATEGORY_PARTITIONS_DE_MUSIQUE,
    pro_label="Partition",
    app_label="Partition",
    search_group_name=SEARCH_GROUP_INSTRUMENTS.id,
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
# endregion
# region BEAUX_ARTS
MATERIEL_ART_CREATIF = Subcategory(
    id="MATERIEL_ART_CREATIF",
    category=categories.BEAUX_ARTS,
    native_category=NATIVE_CATEGORY_MATERIELS_CREATIFS,
    pro_label="Matériel arts créatifs",
    app_label="Matériel arts créatifs",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.BEAUX_ARTS.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
# endregion
# region TECHNICAL
ACTIVATION_EVENT = Subcategory(
    id="ACTIVATION_EVENT",
    category=categories.TECHNIQUE,
    pro_label="Catégorie technique d'évènement d'activation ",
    app_label="Catégorie technique d'évènement d'activation ",
    search_group_name=SEARCH_GROUP_NONE.id,
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_not_free=False,
    native_category=NATIVE_CATEGORY_DEPRECIEE,
)
ACTIVATION_THING = Subcategory(
    id="ACTIVATION_THING",
    category=categories.TECHNIQUE,
    pro_label="Catégorie technique de thing d'activation",
    app_label="Catégorie technique de thing d'activation",
    search_group_name=SEARCH_GROUP_NONE.id,
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_not_free=False,
    native_category=NATIVE_CATEGORY_DEPRECIEE,
)
JEU_SUPPORT_PHYSIQUE = Subcategory(
    id="JEU_SUPPORT_PHYSIQUE",
    category=categories.TECHNIQUE,
    native_category=NATIVE_CATEGORY_JEUX_PHYSIQUES,
    pro_label="Catégorie technique Jeu support physique",
    app_label="Catégorie technique Jeu support physique",
    search_group_name=SEARCH_GROUP_NONE.id,
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
OEUVRE_ART = Subcategory(
    id="OEUVRE_ART",
    category=categories.TECHNIQUE,
    native_category=NATIVE_CATEGORY_ARTS_VISUELS,
    pro_label="Catégorie technique d'oeuvre d'art",
    app_label="Catégorie technique d'oeuvre d'art",
    search_group_name=SEARCH_GROUP_ARTS_LOISIRS_CREATIFS.id,
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# endregion

ALL_SUBCATEGORIES = (
    ABO_BIBLIOTHEQUE,
    ABO_CONCERT,
    ABO_JEU_VIDEO,
    ABO_LIVRE_NUMERIQUE,
    ABO_LUDOTHEQUE,
    ABO_MEDIATHEQUE,
    ABO_PLATEFORME_MUSIQUE,
    ABO_PLATEFORME_VIDEO,
    ABO_PRATIQUE_ART,
    ABO_PRESSE_EN_LIGNE,
    ABO_SPECTACLE,
    ACHAT_INSTRUMENT,
    ACTIVATION_EVENT,
    ACTIVATION_THING,
    APP_CULTURELLE,
    ATELIER_PRATIQUE_ART,
    AUTRE_SUPPORT_NUMERIQUE,
    BON_ACHAT_INSTRUMENT,
    CAPTATION_MUSIQUE,
    CARTE_CINE_ILLIMITE,
    CARTE_CINE_MULTISEANCES,
    CARTE_JEUNES,
    CARTE_MUSEE,
    CINE_PLEIN_AIR,
    CINE_VENTE_DISTANCE,
    CONCERT,
    CONCOURS,
    CONFERENCE,
    DECOUVERTE_METIERS,
    ESCAPE_GAME,
    EVENEMENT_CINE,
    EVENEMENT_JEU,
    EVENEMENT_MUSIQUE,
    EVENEMENT_PATRIMOINE,
    FESTIVAL_ART_VISUEL,
    FESTIVAL_CINE,
    FESTIVAL_LIVRE,
    FESTIVAL_MUSIQUE,
    FESTIVAL_SPECTACLE,
    JEU_EN_LIGNE,
    JEU_SUPPORT_PHYSIQUE,
    LIVESTREAM_EVENEMENT,
    LIVESTREAM_MUSIQUE,
    LIVESTREAM_PRATIQUE_ARTISTIQUE,
    LIVRE_AUDIO_PHYSIQUE,
    LIVRE_NUMERIQUE,
    LIVRE_PAPIER,
    LOCATION_INSTRUMENT,
    MATERIEL_ART_CREATIF,
    MUSEE_VENTE_DISTANCE,
    OEUVRE_ART,
    PARTITION,
    PLATEFORME_PRATIQUE_ARTISTIQUE,
    PRATIQUE_ART_VENTE_DISTANCE,
    PODCAST,
    RENCONTRE_EN_LIGNE,
    RENCONTRE_JEU,
    RENCONTRE,
    SALON,
    SEANCE_CINE,
    SEANCE_ESSAI_PRATIQUE_ART,
    SPECTACLE_ENREGISTRE,
    SPECTACLE_REPRESENTATION,
    SPECTACLE_VENTE_DISTANCE,
    SUPPORT_PHYSIQUE_FILM,
    SUPPORT_PHYSIQUE_MUSIQUE_CD,
    SUPPORT_PHYSIQUE_MUSIQUE_VINYLE,
    TELECHARGEMENT_LIVRE_AUDIO,
    TELECHARGEMENT_MUSIQUE,
    VISITE_GUIDEE,
    VISITE_VIRTUELLE,
    VISITE,
    VOD,
)
ALL_SUBCATEGORIES_DICT = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES}
PERMANENT_SUBCATEGORIES = {
    subcategory.id: subcategory
    for subcategory in ALL_SUBCATEGORIES
    if not subcategory.can_expire and not subcategory.is_event
}
EXPIRABLE_SUBCATEGORIES = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_expire}
EVENT_SUBCATEGORIES = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.is_event}
ACTIVATION_SUBCATEGORIES = (ACTIVATION_EVENT.id, ACTIVATION_THING.id)
BOOK_WITH_EAN = (LIVRE_PAPIER.id, LIVRE_AUDIO_PHYSIQUE.id, LIVRE_NUMERIQUE.id)

COLLECTIVE_SUBCATEGORIES = {
    subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_be_educational
}

WITHDRAWABLE_SUBCATEGORIES = {
    subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_be_withdrawable
}

MUSIC_SUBCATEGORIES = {
    subcategory.id: subcategory
    for subcategory in ALL_SUBCATEGORIES
    if subcategory.category in [categories.MUSIQUE_LIVE, categories.MUSIQUE_ENREGISTREE]
}

# WARNING: You will need to regenerate offer_music_subcategory_with_gtl_id_substr_idx when adding a subcategory to MUSIC_TITELIVE_SEARCH_SUBCATEGORY_IDS
MUSIC_TITELIVE_SUBCATEGORY_SEARCH_IDS = {
    subcategory.id for subcategory in [SUPPORT_PHYSIQUE_MUSIQUE_CD, SUPPORT_PHYSIQUE_MUSIQUE_VINYLE]
}


assert set(subcategory.id for subcategory in ALL_SUBCATEGORIES) == set(
    subcategory.id for subcategory in locals().values() if isinstance(subcategory, Subcategory)
)


SubcategoryIdEnumv2 = Enum("SubcategoryIdEnumv2", {subcategory.id: subcategory.id for subcategory in ALL_SUBCATEGORIES})  # type: ignore[misc]
SubcategoryProLabelEnumv2 = Enum("SubcategoryProLabelEnumv2", {subcategory.id: subcategory.pro_label for subcategory in ALL_SUBCATEGORIES})  # type: ignore[misc]
SearchGroupNameEnumv2 = Enum(  # type: ignore[misc]
    "SearchGroupNameEnumv2",
    {search_group_name: search_group_name for search_group_name in [c.id for c in SEARCH_GROUPS]},
)
HomepageLabelNameEnumv2 = Enum(  # type: ignore[misc]
    "(HomepageLabelNameEnumv2",
    {homepage_label_name: homepage_label_name for homepage_label_name in [h.name for h in HomepageLabels]},
)
OnlineOfflinePlatformChoicesEnumv2 = Enum(  # type: ignore[misc]
    "OnlineOfflinePlatformChoicesEnumv2",
    {choice: choice for choice in [c.value for c in OnlineOfflinePlatformChoices]},
)
NativeCategoryIdEnumv2 = Enum(  # type: ignore[misc]
    "NativeCategoryIdEnumv2",
    {native_category.id: native_category.id for native_category in NativeCategory.instances},
)

# Support for old enum names serializers
# TODO: remove when old enum names are not used in the app anymore, and after a forced update
# Jira: https://passculture.atlassian.net/browse/PC-25049
SubcategoryIdEnum = Enum("SubcategoryIdEnum", {subcategory.id: subcategory.id for subcategory in ALL_SUBCATEGORIES})  # type: ignore[misc]
