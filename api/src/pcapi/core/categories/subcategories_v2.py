from dataclasses import dataclass
from dataclasses import field
from enum import Enum
import typing

from pcapi.core.categories import categories
from pcapi.domain.book_types import BOOK_MACRO_SECTIONS
from pcapi.domain.book_types import BookType
from pcapi.domain.book_types import book_types
from pcapi.domain.movie_types import MovieType
from pcapi.domain.movie_types import movie_types
from pcapi.domain.music_types import MUSIC_TYPES_LABEL_BY_CODE
from pcapi.domain.music_types import MusicType
from pcapi.domain.music_types import music_types
from pcapi.domain.show_types import SHOW_TYPES_LABEL_BY_CODE
from pcapi.domain.show_types import ShowType
from pcapi.domain.show_types import show_types


class OnlineOfflinePlatformChoices(Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ONLINE_OR_OFFLINE = "ONLINE_OR_OFFLINE"


class SearchGroups(Enum):
    ARTS_LOISIRS_CREATIFS = "Arts & loisirs créatifs"
    CARTES_JEUNES = "Cartes jeunes"
    CD_VINYLE_MUSIQUE_EN_LIGNE = "CD, vinyles, musique en ligne"
    CONCERTS_FESTIVALS = "Concerts & festivals"
    EVENEMENTS_EN_LIGNE = "Évènements en ligne"
    FILMS_SERIES_CINEMA = "Cinéma, films et séries"
    INSTRUMENTS = "Instruments de musique"
    JEUX_JEUX_VIDEOS = "Jeux & jeux vidéos"
    LIVRES = "Livres"
    MEDIA_PRESSE = "Médias & presse"
    MUSEES_VISITES_CULTURELLES = "Musées & visites culturelles"
    NONE = None
    RENCONTRES_CONFERENCES = "Conférences & rencontres"
    SPECTACLES = "Spectacles"


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
    VISITES = "Visites"


class ReimbursementRuleChoices(Enum):
    STANDARD = "STANDARD"
    NOT_REIMBURSED = "NOT_REIMBURSED"
    BOOK = "BOOK"


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
            type(self).BOOK.name: book_types,
            type(self).MUSIC.name: music_types,
            type(self).SHOW.name: show_types,
            type(self).MOVIE.name: movie_types,
        }[
            self.name
        ]  # type: ignore[return-value]

    def book_values(self) -> list[GenreTypeContent]:
        return [GenreTypeContent(name=value, value=value) for value in sorted(BOOK_MACRO_SECTIONS)]

    def music_values(self) -> list[GenreTypeContent]:
        return [GenreTypeContent(name=value, value=value) for value in sorted(MUSIC_TYPES_LABEL_BY_CODE.values())]

    def show_values(self) -> list[GenreTypeContent]:
        return [GenreTypeContent(name=value, value=value) for value in sorted(SHOW_TYPES_LABEL_BY_CODE.values())]

    def movie_values(self) -> list[GenreTypeContent]:
        values = [GenreTypeContent(name=movie_type.name, value=movie_type.label) for movie_type in movie_types]
        return sorted(values, key=lambda x: x.value)


class NativeCategory(Enum):
    ABONNEMENTS_MUSEE = "Abonnements musée"
    ABONNEMENTS_SPECTACLE = "Abonnements spectacle"
    ACHAT_LOCATION_INSTRUMENT = "Achat & location d'instrument"
    ARTS_VISUELS = "Arts visuels"
    AUTRES_MEDIAS = "Autres médias"
    BIBLIOTHEQUE_MEDIATHEQUE = "Abonnements aux médiathèques et bibliothèques"
    CARTES_CINEMA = "Cartes cinéma"
    CARTES_JEUNES = "Cartes jeunes"
    CD = "CD"
    CONCERTS_EN_LIGNE = "Concerts en ligne"
    CONCERTS_EVENEMENTS = "Concerts, évènements"
    CONCOURS = "Concours"
    CONFERENCES = "Conférences"
    DEPRECIEE = "Dépréciée"
    DVD_BLU_RAY = "DVD, Blu-Ray"
    ESCAPE_GAMES = "Escape games"
    EVENEMENTS_CINEMA = "Evènements cinéma"
    EVENEMENTS_PATRIMOINE = "Evènements patrimoine"
    FESTIVALS = "Festivals"
    FESTIVAL_DU_LIVRE = "Évènements autour du livre"
    FILMS_SERIES_EN_LIGNE = "Films, séries en ligne"
    JEUX_EN_LIGNE = "Jeux en ligne"
    JEUX_PHYSIQUES = "Jeux physiques"
    LIVRES_AUDIO_PHYSIQUES = "Livres audio"
    LIVRES_NUMERIQUE_ET_AUDIO = "E-books"
    LIVRES_PAPIER = "Livres papier"
    LUDOTHEQUE = "Ludothèque"
    MATERIELS_CREATIFS = "Matériels créatifs"
    MUSIQUE_EN_LIGNE = "Musique en ligne"
    PARTITIONS_DE_MUSIQUE = "Partitions de musique"
    PODCAST = "Podcast"
    PRATIQUES_ET_ATELIERS_ARTISTIQUES = "Pratiques & ateliers artistiques"
    PRATIQUE_ARTISTIQUE_EN_LIGNE = "Pratique artistique en ligne"
    PRESSE_EN_LIGNE = "Presse en ligne"
    RENCONTRES = "Rencontres"
    RENCONTRES_EN_LIGNE = "Rencontres en ligne"
    RENCONTRES_EVENEMENTS = "Rencontres évènements"
    SALONS_ET_METIERS = "Salons & métiers"
    SEANCES_DE_CINEMA = "Séances de cinéma"
    SPECTACLES_ENREGISTRES = "Spectacles enregistrés"
    SPECTACLES_REPRESENTATIONS = "Spectacles & représentations"
    VINYLES = "Vinyles et autres supports"
    VISITES_CULTURELLES = "Visites culturelles"
    VISITES_CULTURELLES_EN_LIGNE = "Visites culturelles en ligne"

    @property
    def genre_type(self) -> GenreType | None:
        try:
            return NATIVE_CATEGORY_GENRES_TYPES_MAPPING[self]
        except KeyError:
            return None


NATIVE_CATEGORY_GENRES_TYPES_MAPPING = {
    NativeCategory.LIVRES_PAPIER: GenreType.BOOK,
    NativeCategory.SEANCES_DE_CINEMA: GenreType.MOVIE,
    NativeCategory.FESTIVALS: GenreType.MUSIC,
    NativeCategory.CD: GenreType.MUSIC,
    NativeCategory.VINYLES: GenreType.MUSIC,
    NativeCategory.MUSIQUE_EN_LIGNE: GenreType.MUSIC,
    NativeCategory.CONCERTS_EN_LIGNE: GenreType.MUSIC,
    NativeCategory.CONCERTS_EVENEMENTS: GenreType.MUSIC,
    NativeCategory.ABONNEMENTS_SPECTACLE: GenreType.SHOW,
    NativeCategory.SPECTACLES_ENREGISTRES: GenreType.SHOW,
    NativeCategory.SPECTACLES_REPRESENTATIONS: GenreType.SHOW,
}


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
        if self.search_group_name not in [s.name for s in SearchGroups]:
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
        return self.native_category.name

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
    native_category=NativeCategory.DVD_BLU_RAY,
    pro_label="Support physique (DVD, Blu-ray...)",
    app_label="Support physique (DVD, Blu-ray...)",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.BIBLIOTHEQUE_MEDIATHEQUE,
    pro_label="Abonnement médiathèque",
    app_label="Abonnement médiathèque",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.FILMS_SERIES_EN_LIGNE,
    pro_label="Vidéo à la demande",
    app_label="Vidéo à la demande",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.FILMS_SERIES_EN_LIGNE,
    pro_label="Abonnement plateforme streaming",
    app_label="Abonnement plateforme streaming",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.FILMS_SERIES_EN_LIGNE,
    pro_label="Autre support numérique",
    app_label="Autre support numérique",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.CARTES_CINEMA,
    pro_label="Carte cinéma multi-séances",
    app_label="Carte cinéma multi-séances",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.CARTES_CINEMA,
    pro_label="Carte cinéma illimité",
    app_label="Carte cinéma illimité",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.SEANCES_DE_CINEMA,
    pro_label="Séance de cinéma",
    app_label="Séance de cinéma",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.EVENEMENTS_CINEMA,
    pro_label="Évènement cinématographique",
    app_label="Évènement cinéma",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.EVENEMENTS_CINEMA,
    pro_label="Festival de cinéma",
    app_label="Festival de cinéma",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.SEANCES_DE_CINEMA,
    pro_label="Cinéma vente à distance",
    app_label="Cinéma",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.SEANCES_DE_CINEMA,
    pro_label="Cinéma plein air",
    app_label="Cinéma plein air",
    search_group_name=SearchGroups.FILMS_SERIES_CINEMA.name,
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
    native_category=NativeCategory.CONFERENCES,
    pro_label="Conférence",
    app_label="Conférence",
    search_group_name=SearchGroups.RENCONTRES_CONFERENCES.name,
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
    native_category=NativeCategory.RENCONTRES,
    pro_label="Rencontre",
    app_label="Rencontre",
    search_group_name=SearchGroups.RENCONTRES_CONFERENCES.name,
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
    native_category=NativeCategory.SALONS_ET_METIERS,
    pro_label="Découverte des métiers",
    app_label="Découverte des métiers",
    search_group_name=SearchGroups.RENCONTRES_CONFERENCES.name,
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
    native_category=NativeCategory.SALONS_ET_METIERS,
    pro_label="Salon, Convention",
    app_label="Salon, Convention",
    search_group_name=SearchGroups.RENCONTRES_CONFERENCES.name,
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
    native_category=NativeCategory.RENCONTRES_EN_LIGNE,
    pro_label="Rencontre en ligne",
    app_label="Rencontre en ligne",
    search_group_name=SearchGroups.RENCONTRES_CONFERENCES.name,
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
    native_category=NativeCategory.CONCOURS,
    pro_label="Concours - jeux",
    app_label="Concours - jeux",
    search_group_name=SearchGroups.JEUX_JEUX_VIDEOS.name,
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
    native_category=NativeCategory.RENCONTRES_EVENEMENTS,
    pro_label="Rencontres - jeux",
    app_label="Rencontres - jeux",
    search_group_name=SearchGroups.JEUX_JEUX_VIDEOS.name,
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
    native_category=NativeCategory.ESCAPE_GAMES,
    pro_label="Escape game",
    app_label="Escape game",
    search_group_name=SearchGroups.JEUX_JEUX_VIDEOS.name,
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
    native_category=NativeCategory.RENCONTRES_EVENEMENTS,
    pro_label="Évènements - jeux",
    app_label="Évènements - jeux",
    search_group_name=SearchGroups.JEUX_JEUX_VIDEOS.name,
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
    native_category=NativeCategory.JEUX_EN_LIGNE,
    pro_label="Jeux en ligne",
    app_label="Jeux en ligne",
    search_group_name=SearchGroups.JEUX_JEUX_VIDEOS.name,
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
    native_category=NativeCategory.JEUX_EN_LIGNE,
    pro_label="Abonnement jeux vidéos",
    app_label="Abonnement jeux vidéos",
    search_group_name=SearchGroups.JEUX_JEUX_VIDEOS.name,
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
    native_category=NativeCategory.LUDOTHEQUE,
    pro_label="Abonnement ludothèque",
    app_label="Abonnement ludothèque",
    search_group_name=SearchGroups.JEUX_JEUX_VIDEOS.name,
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
    native_category=NativeCategory.LIVRES_PAPIER,
    pro_label="Livre papier",
    app_label="Livre",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.LIVRES_NUMERIQUE_ET_AUDIO,
    pro_label="Livre numérique, e-book",
    app_label="Livre numérique, e-book",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.LIVRES_NUMERIQUE_ET_AUDIO,
    pro_label="Livre audio à télécharger",
    app_label="Livre audio à télécharger",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.LIVRES_AUDIO_PHYSIQUES,
    pro_label="Livre audio sur support physique",
    app_label="Livre audio sur support physique",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.BIBLIOTHEQUE_MEDIATHEQUE,
    pro_label="Abonnement (bibliothèques, médiathèques...)",
    app_label="Abonnement (bibliothèques, médiathèques...)",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.LIVRES_NUMERIQUE_ET_AUDIO,
    pro_label="Abonnement livres numériques",
    app_label="Abonnement livres numériques",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.FESTIVAL_DU_LIVRE,
    pro_label="Festival et salon du livre",
    app_label="Festival et salon du livre",
    search_group_name=SearchGroups.LIVRES.name,
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
    native_category=NativeCategory.CARTES_JEUNES,
    pro_label="Carte jeunes",
    app_label="Carte jeunes",
    search_group_name=SearchGroups.CARTES_JEUNES.name,
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
    native_category=NativeCategory.ABONNEMENTS_MUSEE,
    pro_label="Abonnement musée, carte ou pass",
    app_label="Abonnement musée, carte ou pass",
    search_group_name=SearchGroups.MUSEES_VISITES_CULTURELLES.name,
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
    native_category=NativeCategory.VISITES_CULTURELLES,
    pro_label="Visite",
    app_label="Visite",
    search_group_name=SearchGroups.MUSEES_VISITES_CULTURELLES.name,
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
    native_category=NativeCategory.VISITES_CULTURELLES,
    pro_label="Visite guidée",
    app_label="Visite guidée",
    search_group_name=SearchGroups.MUSEES_VISITES_CULTURELLES.name,
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
    native_category=NativeCategory.EVENEMENTS_PATRIMOINE,
    pro_label="Évènement et atelier patrimoine",
    app_label="Évènement et atelier patrimoine",
    search_group_name=SearchGroups.MUSEES_VISITES_CULTURELLES.name,
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
    native_category=NativeCategory.VISITES_CULTURELLES_EN_LIGNE,
    pro_label="Visite virtuelle",
    app_label="Visite virtuelle",
    search_group_name=SearchGroups.MUSEES_VISITES_CULTURELLES.name,
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
    native_category=NativeCategory.VISITES_CULTURELLES,
    pro_label="Musée vente à distance",
    app_label="Musée vente à distance",
    search_group_name=SearchGroups.MUSEES_VISITES_CULTURELLES.name,
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
    native_category=NativeCategory.ARTS_VISUELS,
    pro_label="Festival d'arts visuels / arts numériques",
    app_label="Festival d'arts visuels / arts numériques",
    search_group_name=SearchGroups.MUSEES_VISITES_CULTURELLES.name,
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
    native_category=NativeCategory.CONCERTS_EVENEMENTS,
    pro_label="Concert",
    app_label="Concert",
    search_group_name=SearchGroups.CONCERTS_FESTIVALS.name,
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
    native_category=NativeCategory.CONCERTS_EVENEMENTS,
    pro_label="Autre type d'évènement musical",
    app_label="Autre type d'évènement musical",
    search_group_name=SearchGroups.CONCERTS_FESTIVALS.name,
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
    native_category=NativeCategory.CONCERTS_EN_LIGNE,
    pro_label="Livestream musical",
    app_label="Livestream musical",
    search_group_name=SearchGroups.EVENEMENTS_EN_LIGNE.name,
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
    native_category=NativeCategory.CONCERTS_EVENEMENTS,
    pro_label="Abonnement concert",
    app_label="Abonnement concert",
    search_group_name=SearchGroups.CONCERTS_FESTIVALS.name,
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
    native_category=NativeCategory.FESTIVALS,
    pro_label="Festival de musique",
    app_label="Festival de musique",
    search_group_name=SearchGroups.CONCERTS_FESTIVALS.name,
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
    native_category=NativeCategory.CD,
    pro_label="CD",
    app_label="CD",
    search_group_name=SearchGroups.CD_VINYLE_MUSIQUE_EN_LIGNE.name,
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
    native_category=NativeCategory.VINYLES,
    pro_label="Vinyles et autres supports",
    app_label="Vinyles et autres supports",
    search_group_name=SearchGroups.CD_VINYLE_MUSIQUE_EN_LIGNE.name,
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
    native_category=NativeCategory.MUSIQUE_EN_LIGNE,
    pro_label="Téléchargement de musique",
    app_label="Téléchargement de musique",
    search_group_name=SearchGroups.CD_VINYLE_MUSIQUE_EN_LIGNE.name,
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
    native_category=NativeCategory.MUSIQUE_EN_LIGNE,
    pro_label="Abonnement plateforme musicale",
    app_label="Abonnement plateforme musicale",
    search_group_name=SearchGroups.CD_VINYLE_MUSIQUE_EN_LIGNE.name,
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
    native_category=NativeCategory.PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Captation musicale",
    app_label="Captation musicale",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
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
    native_category=NativeCategory.PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Séance d'essai",
    app_label="Séance d'essai",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
    homepage_label_name=HomepageLabels.BEAUX_ARTS.name,
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
    native_category=NativeCategory.PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Atelier, stage de pratique artistique",
    app_label="Atelier, stage de pratique artistique",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
    homepage_label_name=HomepageLabels.BEAUX_ARTS.name,
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
    native_category=NativeCategory.PRATIQUES_ET_ATELIERS_ARTISTIQUES,
    pro_label="Abonnement pratique artistique",
    app_label="Abonnement pratique artistique",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
    homepage_label_name=HomepageLabels.BEAUX_ARTS.name,
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
    native_category=NativeCategory.PRATIQUE_ARTISTIQUE_EN_LIGNE,
    pro_label="Pratique artistique - vente à distance",
    app_label="Pratique artistique - vente à distance",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
    homepage_label_name=HomepageLabels.BEAUX_ARTS.name,
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
    native_category=NativeCategory.PRATIQUE_ARTISTIQUE_EN_LIGNE,
    pro_label="Pratique artistique - plateforme en ligne",
    app_label="Plateforme de pratique artistique",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
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
    native_category=NativeCategory.PRATIQUE_ARTISTIQUE_EN_LIGNE,
    pro_label="Pratique artistique - livestream",
    app_label="Pratique artistique - livestream",
    search_group_name=SearchGroups.EVENEMENTS_EN_LIGNE.name,
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
    native_category=NativeCategory.PRESSE_EN_LIGNE,
    pro_label="Abonnement presse en ligne",
    app_label="Abonnement presse en ligne",
    search_group_name=SearchGroups.MEDIA_PRESSE.name,
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
    native_category=NativeCategory.PODCAST,
    pro_label="Podcast",
    app_label="Podcast",
    search_group_name=SearchGroups.MEDIA_PRESSE.name,
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
    native_category=NativeCategory.AUTRES_MEDIAS,
    pro_label="Application culturelle",
    app_label="Application culturelle",
    search_group_name=SearchGroups.MEDIA_PRESSE.name,
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
    native_category=NativeCategory.SPECTACLES_REPRESENTATIONS,
    pro_label="Spectacle, représentation",
    app_label="Spectacle, représentation",
    search_group_name=SearchGroups.SPECTACLES.name,
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
    native_category=NativeCategory.SPECTACLES_ENREGISTRES,
    pro_label="Spectacle enregistré",
    app_label="Spectacle enregistré",
    search_group_name=SearchGroups.SPECTACLES.name,
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
    native_category=NativeCategory.RENCONTRES_EN_LIGNE,
    pro_label="Livestream d'évènement",
    app_label="Livestream d'évènement",
    search_group_name=SearchGroups.EVENEMENTS_EN_LIGNE.name,
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
    native_category=NativeCategory.SPECTACLES_REPRESENTATIONS,
    pro_label="Festival de spectacle vivant",
    app_label="Festival de spectacle vivant",
    search_group_name=SearchGroups.SPECTACLES.name,
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
    native_category=NativeCategory.ABONNEMENTS_SPECTACLE,
    pro_label="Abonnement spectacle",
    app_label="Abonnement spectacle",
    search_group_name=SearchGroups.SPECTACLES.name,
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
    native_category=NativeCategory.SPECTACLES_REPRESENTATIONS,
    pro_label="Spectacle vivant - vente à distance",
    app_label="Spectacle vivant - vente à distance",
    search_group_name=SearchGroups.SPECTACLES.name,
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
    native_category=NativeCategory.ACHAT_LOCATION_INSTRUMENT,
    pro_label="Achat instrument",
    app_label="Achat instrument",
    search_group_name=SearchGroups.INSTRUMENTS.name,
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
    category=categories.INSTRUMENT,
    native_category=NativeCategory.ACHAT_LOCATION_INSTRUMENT,
    pro_label="Bon d'achat instrument",
    app_label="Bon d'achat instrument",
    search_group_name=SearchGroups.INSTRUMENTS.name,
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
    native_category=NativeCategory.ACHAT_LOCATION_INSTRUMENT,
    pro_label="Location instrument",
    app_label="Location instrument",
    search_group_name=SearchGroups.INSTRUMENTS.name,
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
    native_category=NativeCategory.PARTITIONS_DE_MUSIQUE,
    pro_label="Partition",
    app_label="Partition",
    search_group_name=SearchGroups.INSTRUMENTS.name,
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
    native_category=NativeCategory.MATERIELS_CREATIFS,
    pro_label="Matériel arts créatifs",
    app_label="Matériel arts créatifs",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
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
    search_group_name=SearchGroups.NONE.name,
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
    native_category=NativeCategory.DEPRECIEE,
)
ACTIVATION_THING = Subcategory(
    id="ACTIVATION_THING",
    category=categories.TECHNIQUE,
    pro_label="Catégorie technique de thing d'activation",
    app_label="Catégorie technique de thing d'activation",
    search_group_name=SearchGroups.NONE.name,
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
    native_category=NativeCategory.DEPRECIEE,
)
JEU_SUPPORT_PHYSIQUE = Subcategory(
    id="JEU_SUPPORT_PHYSIQUE",
    category=categories.TECHNIQUE,
    native_category=NativeCategory.JEUX_PHYSIQUES,
    pro_label="Catégorie technique Jeu support physique",
    app_label="Catégorie technique Jeu support physique",
    search_group_name=SearchGroups.NONE.name,
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
    native_category=NativeCategory.ARTS_VISUELS,
    pro_label="Catégorie technique d'oeuvre d'art",
    app_label="Catégorie technique d'oeuvre d'art",
    search_group_name=SearchGroups.ARTS_LOISIRS_CREATIFS.name,
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
    {search_group_name: search_group_name for search_group_name in [c.name for c in SearchGroups]},
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
    {native_category.name: native_category.name for native_category in NativeCategory},
)

# Support for old enum names serializers
# TODO: remove when old enum names are not used in the app anymore, and after a forced update
# Jira: https://passculture.atlassian.net/browse/PC-25049
SubcategoryIdEnum = Enum("SubcategoryIdEnum", {subcategory.id: subcategory.id for subcategory in ALL_SUBCATEGORIES})  # type: ignore[misc]
