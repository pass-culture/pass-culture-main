from pcapi.core.categories.genres.book import BOOK_TYPES
from pcapi.core.categories.genres.movie import MOVIE_TYPES
from pcapi.core.categories.genres.music import MUSIC_TYPES
from pcapi.core.categories.genres.show import SHOW_TYPES
from pcapi.core.categories.models import BookGenre
from pcapi.core.categories.models import GenreType
from pcapi.core.categories.models import MovieGenre
from pcapi.core.categories.models import MusicGenre
from pcapi.core.categories.models import NativeCategory
from pcapi.core.categories.models import SearchGroup
from pcapi.core.categories.models import SearchNode
from pcapi.core.categories.models import ShowGenre
from pcapi.core.categories.models import get_all_instances
from pcapi.core.categories.models import get_native_categories
from pcapi.core.categories.models import get_search_groups


# region genres
def get_book_nodes() -> list[BookGenre]:
    nodes = []
    for book_type in BOOK_TYPES:
        node = BookGenre(
            label=book_type.label,
            children=[
                BookGenre(label=book_subtype.label, gtls=[gtl.code for gtl in book_subtype.gtls])
                for book_subtype in book_type.children
            ],
            gtls=[gtl.code for gtl in book_type.gtls],
        )
        nodes.append(node)

    return nodes


def get_movie_nodes() -> list[MovieGenre]:
    return [MovieGenre(label=movie_type.label, search_value=movie_type.name) for movie_type in MOVIE_TYPES]


def get_music_nodes() -> list[MusicGenre]:
    return [MusicGenre(label=music_type.label, search_value=music_type.name) for music_type in MUSIC_TYPES]


def get_show_nodes() -> list[ShowGenre]:
    return [ShowGenre(label=show_type.label, search_value=show_type.label) for show_type in SHOW_TYPES]


def get_theatre_et_humour_genres() -> list[ShowGenre]:
    return [
        ShowGenre(label=show_sub_type.label)
        for show_type in SHOW_TYPES
        for show_sub_type in show_type.children
        if show_type.code in (400, 1300) and show_sub_type.code != -1
    ]


def get_spectacles_genres() -> list[ShowGenre]:
    return [
        ShowGenre(label=show_sub_type.label)
        for show_type in SHOW_TYPES
        for show_sub_type in show_type.children
        if show_type.code not in (400, 1300) and show_sub_type.code != -1
    ]


BOOK_GENRES: list[BookGenre] = get_book_nodes()
MOVIE_GENRES: list[MovieGenre] = get_movie_nodes()
MUSIC_GENRES: list[MusicGenre] = get_music_nodes()
SHOW_GENRES: list[ShowGenre] = get_show_nodes()
SPECTACLES_GENRES: list[ShowGenre] = get_spectacles_genres()
THEATRE_ET_HUMOUR_GENRES: list[ShowGenre] = get_theatre_et_humour_genres()

# endregion


# region NativeCategory
NATIVE_CATEGORY_ABO_PLATEFORME_VIDEO = NativeCategory(
    search_value="ABO_PLATEFORME_VIDEO",
    label="Abonnements streaming",
    included_subcategories=["ABO_PLATEFORME_VIDEO"],
)
NATIVE_CATEGORY_ABONNEMENTS_MUSEE = NativeCategory(
    search_value="ABONNEMENTS_MUSEE",
    label="Abonnements musée",
    included_subcategories=["CARTE_MUSEE"],
)
NATIVE_CATEGORY_ABONNEMENTS_SPECTACLE = NativeCategory(
    search_value="ABONNEMENTS_SPECTACLE",
    label="Abonnements spectacle",
    children=SHOW_GENRES,
    included_subcategories=["ABO_SPECTACLE"],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_ACHAT_LOCATION_INSTRUMENT = NativeCategory(
    search_value="ACHAT_LOCATION_INSTRUMENT",
    label="Achat et location d'instruments",
    included_subcategories=["ACHAT_INSTRUMENT", "BON_ACHAT_INSTRUMENT", "LOCATION_INSTRUMENT"],
)
NATIVE_CATEGORY_ARTS_VISUELS = NativeCategory(
    search_value="ARTS_VISUELS",
    label="Arts visuels",
    included_subcategories=["FESTIVAL_ART_VISUEL", "OEUVRE_ART"],
)
NATIVE_CATEGORY_AUTRES_MEDIAS = NativeCategory(
    search_value="AUTRES_MEDIAS",
    label="Autres médias",
    included_subcategories=["APP_CULTURELLE"],
)
NATIVE_CATEGORY_BIBLIOTHEQUE_MEDIATHEQUE = NativeCategory(
    search_value="BIBLIOTHEQUE_MEDIATHEQUE",
    label="Abonnements aux médiathèques et bibliothèques",
    included_subcategories=["ABO_BIBLIOTHEQUE", "ABO_MEDIATHEQUE"],
)
NATIVE_CATEGORY_CARTES_CINEMA = NativeCategory(
    search_value="CARTES_CINEMA",
    label="Cartes cinéma",
    included_subcategories=["CARTE_CINE_ILLIMITE", "CARTE_CINE_MULTISEANCES", "CINE_VENTE_DISTANCE"],
)
NATIVE_CATEGORY_CD = NativeCategory(
    search_value="CD",
    label="CDs",
    children=MUSIC_GENRES,
    included_subcategories=["SUPPORT_PHYSIQUE_MUSIQUE_CD"],
    genre_type=GenreType.MUSIC,
)
NATIVE_CATEGORY_CONCERTS_EN_LIGNE = NativeCategory(
    search_value="CONCERTS_EN_LIGNE",
    label="Concerts en ligne",
    children=MUSIC_GENRES,
    included_subcategories=["LIVESTREAM_MUSIQUE"],
    genre_type=GenreType.MUSIC,
)
NATIVE_CATEGORY_CONCERTS_EVENEMENTS = NativeCategory(
    search_value="CONCERTS_EVENEMENTS",
    label="Concerts",
    children=MUSIC_GENRES,
    included_subcategories=["ABO_CONCERT", "CONCERT", "EVENEMENT_MUSIQUE"],
    genre_type=GenreType.MUSIC,
)
NATIVE_CATEGORY_CONCOURS = NativeCategory(
    search_value="CONCOURS",
    label="Concours",
    included_subcategories=["CONCOURS"],
)
NATIVE_CATEGORY_CONFERENCES = NativeCategory(
    search_value="CONFERENCES",
    label="Conférences",
    included_subcategories=["CONFERENCE"],
)
NATIVE_CATEGORY_DEPRECIEE = NativeCategory(
    search_value="DEPRECIEE",
    label="Dépréciée",
    included_subcategories=["ACTIVATION_EVENT", "ACTIVATION_THING"],
)
NATIVE_CATEGORY_DVD_BLU_RAY = NativeCategory(
    search_value="DVD_BLU_RAY",
    label="DVD, Blu-Ray",
    included_subcategories=["SUPPORT_PHYSIQUE_FILM"],
)
NATIVE_CATEGORY_ESCAPE_GAMES = NativeCategory(
    search_value="ESCAPE_GAMES",
    label="Escape games",
    included_subcategories=["ESCAPE_GAME"],
)
NATIVE_CATEGORY_EVENEMENTS_CINEMA = NativeCategory(
    search_value="EVENEMENTS_CINEMA",
    label="Evènements cinéma",
    included_subcategories=["EVENEMENT_CINE", "FESTIVAL_CINE"],
)
NATIVE_CATEGORY_EVENEMENTS_PATRIMOINE = NativeCategory(
    search_value="EVENEMENTS_PATRIMOINE",
    label="Evènements patrimoine",
    included_subcategories=["EVENEMENT_PATRIMOINE"],
)
NATIVE_CATEGORY_FESTIVALS = NativeCategory(
    search_value="FESTIVALS",
    label="Festivals",
    children=MUSIC_GENRES,
    included_subcategories=["FESTIVAL_MUSIQUE"],
    genre_type=GenreType.MUSIC,
)
NATIVE_CATEGORY_FESTIVAL_DU_LIVRE = NativeCategory(
    search_value="FESTIVAL_DU_LIVRE",
    label="Évènements autour du livre",
    included_subcategories=["FESTIVAL_LIVRE"],
)
NATIVE_CATEGORY_JEUX_EN_LIGNE = NativeCategory(
    search_value="JEUX_EN_LIGNE",
    label="Jeux en ligne",
    included_subcategories=["ABO_JEU_VIDEO", "JEU_EN_LIGNE"],
)
NATIVE_CATEGORY_JEUX_PHYSIQUES = NativeCategory(
    search_value="JEUX_PHYSIQUES",
    label="Jeux physiques",
    included_subcategories=["JEU_SUPPORT_PHYSIQUE"],
)
NATIVE_CATEGORY_LIVESTREAM_EVENEMENT = NativeCategory(
    search_value="LIVESTREAM_EVENEMENT",
    label="Livestream d'évènements",
    included_subcategories=["LIVESTREAM_EVENEMENT"],
)
NATIVE_CATEGORY_LIVRES_AUDIO_PHYSIQUES = NativeCategory(
    search_value="LIVRES_AUDIO_PHYSIQUES",
    label="Livres audio",
    included_subcategories=["LIVRE_AUDIO_PHYSIQUE"],
)
NATIVE_CATEGORY_LIVRES_NUMERIQUE_ET_AUDIO = NativeCategory(
    search_value="LIVRES_NUMERIQUE_ET_AUDIO",
    label="E-books",
    included_subcategories=[
        "ABO_LIVRE_NUMERIQUE",
        "LIVRE_NUMERIQUE",
        "TELECHARGEMENT_LIVRE_AUDIO",
    ],
)
NATIVE_CATEGORY_LIVRES_PAPIER = NativeCategory(
    search_value="LIVRES_PAPIER",
    label="Livres papier",
    children=BOOK_GENRES,
    included_subcategories=["LIVRE_PAPIER"],
    genre_type=GenreType.BOOK,
)
NATIVE_CATEGORY_LUDOTHEQUE = NativeCategory(
    search_value="LUDOTHEQUE",
    label="Ludothèque",
    included_subcategories=["ABO_LUDOTHEQUE"],
)
NATIVE_CATEGORY_MATERIELS_CREATIFS = NativeCategory(
    search_value="MATERIELS_CREATIFS",
    label="Matériels créatifs",
    included_subcategories=["MATERIEL_ART_CREATIF"],
)
NATIVE_CATEGORY_MUSIQUE_EN_LIGNE = NativeCategory(
    search_value="MUSIQUE_EN_LIGNE",
    label="Musique en ligne",
    children=MUSIC_GENRES,
    included_subcategories=["ABO_PLATEFORME_MUSIQUE", "TELECHARGEMENT_MUSIQUE"],
    genre_type=GenreType.MUSIC,
)
NATIVE_CATEGORY_PARTITIONS_DE_MUSIQUE = NativeCategory(
    search_value="PARTITIONS_DE_MUSIQUE",
    label="Partitions de musique",
    included_subcategories=["PARTITION"],
)
NATIVE_CATEGORY_PODCAST = NativeCategory(
    search_value="PODCAST",
    label="Podcast",
    included_subcategories=["PODCAST"],
)
NATIVE_CATEGORY_PRATIQUES_ET_ATELIERS_ARTISTIQUES = NativeCategory(
    search_value="PRATIQUES_ET_ATELIERS_ARTISTIQUES",
    label="Pratiques & ateliers artistiques",
    included_subcategories=[
        "ABO_PRATIQUE_ART",
        "ATELIER_PRATIQUE_ART",
        "CAPTATION_MUSIQUE",
        "SEANCE_ESSAI_PRATIQUE_ART",
    ],
)
NATIVE_CATEGORY_PRATIQUE_ARTISTIQUE_EN_LIGNE = NativeCategory(
    search_value="PRATIQUE_ARTISTIQUE_EN_LIGNE",
    label="Pratique artistique en ligne",
    included_subcategories=[
        "LIVESTREAM_PRATIQUE_ARTISTIQUE",
        "PLATEFORME_PRATIQUE_ARTISTIQUE",
        "PRATIQUE_ART_VENTE_DISTANCE",
    ],
)
NATIVE_CATEGORY_PRESSE_EN_LIGNE = NativeCategory(
    search_value="PRESSE_EN_LIGNE",
    label="Presse en ligne",
    included_subcategories=["ABO_PRESSE_EN_LIGNE"],
)
NATIVE_CATEGORY_RENCONTRES = NativeCategory(
    search_value="RENCONTRES",
    label="Rencontres",
    included_subcategories=["RENCONTRE"],
)
NATIVE_CATEGORY_RENCONTRES_EN_LIGNE = NativeCategory(
    search_value="RENCONTRES_EN_LIGNE",
    label="Rencontres en ligne",
    included_subcategories=["LIVESTREAM_EVENEMENT", "RENCONTRE_EN_LIGNE"],
)
NATIVE_CATEGORY_RENCONTRES_EVENEMENTS = NativeCategory(
    search_value="RENCONTRES_EVENEMENTS",
    label="Rencontres évènements",
    included_subcategories=["EVENEMENT_JEU", "RENCONTRE_JEU"],
)
NATIVE_CATEGORY_SALONS_ET_METIERS = NativeCategory(
    search_value="SALONS_ET_METIERS",
    label="Salons & métiers",
    included_subcategories=["DECOUVERTE_METIERS", "SALON"],
)
NATIVE_CATEGORY_SEANCES_DE_CINEMA = NativeCategory(
    search_value="SEANCES_DE_CINEMA",
    label="Films à l'affiche",
    children=MOVIE_GENRES,
    included_subcategories=["CINE_PLEIN_AIR", "SEANCE_CINE"],
    genre_type=GenreType.MOVIE,
)
NATIVE_CATEGORY_SPECTACLE_VIVANT_VENTE_A_DISTANCE = NativeCategory(
    search_value="SPECTACLE_VIVANT_VENTE_A_DISTANCE",
    label="Spectacle vivant - vente à distance",
    included_subcategories=["SPECTACLE_VENTE_DISTANCE"],
)
NATIVE_CATEGORY_SPECTACLES_ENREGISTRES = NativeCategory(
    search_value="SPECTACLES_ENREGISTRES",
    label="Spectacles enregistrés",
    children=SHOW_GENRES,
    included_subcategories=["SPECTACLE_ENREGISTRE"],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_SPECTACLES_REPRESENTATIONS = NativeCategory(
    search_value="SPECTACLES_REPRESENTATIONS",
    label="Spectacles & représentations",
    children=SHOW_GENRES,
    included_subcategories=[
        "FESTIVAL_SPECTACLE",
        "SPECTACLE_REPRESENTATION",
        "SPECTACLE_VENTE_DISTANCE",
    ],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_SPECTACLES = NativeCategory(
    search_value="SPECTACLES",
    label="Spectacles",
    children=SPECTACLES_GENRES,
    included_subcategories=[
        "FESTIVAL_SPECTACLE",
        "SPECTACLE_REPRESENTATION",
        "SPECTACLE_VENTE_DISTANCE",
    ],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_THEATRES_ET_HUMOUR = NativeCategory(
    search_value="THEATRES_ET_HUMOUR",
    label="Théâtre et humour",
    children=THEATRE_ET_HUMOUR_GENRES,
    included_subcategories=[
        "FESTIVAL_SPECTACLE",
        "SPECTACLE_REPRESENTATION",
        "SPECTACLE_VENTE_DISTANCE",
    ],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_VIDEOS_ET_DOCUMENTAIRES = NativeCategory(
    search_value="VIDEOS_ET_DOCUMENTAIRES",
    label="Vidéos et documentaires",
    included_subcategories=["AUTRE_SUPPORT_NUMERIQUE", "VOD"],
)
NATIVE_CATEGORY_VINYLES = NativeCategory(
    search_value="VINYLES",
    label="Vinyles",
    children=MUSIC_GENRES,
    included_subcategories=["SUPPORT_PHYSIQUE_MUSIQUE_VINYLE"],
    genre_type=GenreType.MUSIC,
)
NATIVE_CATEGORY_VISITES_CULTURELLES = NativeCategory(
    search_value="VISITES_CULTURELLES",
    label="Visites culturelles",
    included_subcategories=["MUSEE_VENTE_DISTANCE", "VISITE_GUIDEE", "VISITE"],
)
NATIVE_CATEGORY_VISITES_CULTURELLES_EN_LIGNE = NativeCategory(
    search_value="VISITES_CULTURELLES_EN_LIGNE",
    label="Visites culturelles en ligne",
    included_subcategories=["VISITE_VIRTUELLE"],
)
NATIVE_CATEGORY_AUTRES_REPRESENTATIONS = NativeCategory(
    search_value="AUTRES_REPRESENTATIONS",
    label="Autres représentations",
    children=[
        NATIVE_CATEGORY_SPECTACLES_ENREGISTRES,
        NATIVE_CATEGORY_LIVESTREAM_EVENEMENT,
        NATIVE_CATEGORY_SPECTACLE_VIVANT_VENTE_A_DISTANCE,
    ],
    included_subcategories=["LIVESTREAM_EVENEMENT", "SPECTACLE_ENREGISTRE", "SPECTACLE_VENTE_DISTANCE"],
    genre_type=GenreType.SHOW,
)
NATIVE_CATEGORY_FESTIVALS_DE_SPECTACLES = NativeCategory(
    search_value="FESTIVALS_DE_SPECTACLES",
    label="Festivals de spectacles",
    children=SPECTACLES_GENRES + [NATIVE_CATEGORY_THEATRES_ET_HUMOUR],
    included_subcategories=["FESTIVAL_SPECTACLE"],
    genre_type=GenreType.SHOW,
)
# endregion

# region SearchGroup
SEARCH_GROUP_ARTS_LOISIRS_CREATIFS = SearchGroup(
    children=[
        NATIVE_CATEGORY_ARTS_VISUELS,
        NATIVE_CATEGORY_MATERIELS_CREATIFS,
        NATIVE_CATEGORY_PRATIQUES_ET_ATELIERS_ARTISTIQUES,
        NATIVE_CATEGORY_PRATIQUE_ARTISTIQUE_EN_LIGNE,
    ],
    search_value="ARTS_LOISIRS_CREATIFS",
    label="Arts & loisirs créatifs",
    included_subcategories=[
        "ABO_PRATIQUE_ART",
        "ATELIER_PRATIQUE_ART",
        "CAPTATION_MUSIQUE",
        "MATERIEL_ART_CREATIF",
        "OEUVRE_ART",
        "PLATEFORME_PRATIQUE_ARTISTIQUE",
        "PRATIQUE_ART_VENTE_DISTANCE",
        "SEANCE_ESSAI_PRATIQUE_ART",
    ],
)
SEARCH_GROUP_CARTES_JEUNES = SearchGroup(
    children=[],
    search_value="CARTES_JEUNES",
    label="Cartes jeunes",
    included_subcategories=["CARTE_JEUNES"],
)
# FIXME (thconte, 2024-10-15): Delete this SearchGroup once app's minimal version has bumped
SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE = SearchGroup(
    children=[
        NATIVE_CATEGORY_CD,
        NATIVE_CATEGORY_MUSIQUE_EN_LIGNE,
        NATIVE_CATEGORY_VINYLES,
    ],
    search_value="CD_VINYLE_MUSIQUE_EN_LIGNE",
    label="CD, vinyles, musique en ligne",
    included_subcategories=[
        "ABO_PLATEFORME_MUSIQUE",
        "SUPPORT_PHYSIQUE_MUSIQUE_CD",
        "SUPPORT_PHYSIQUE_MUSIQUE_VINYLE",
        "TELECHARGEMENT_MUSIQUE",
    ],
)
SEARCH_GROUP_CONCERTS_FESTIVALS = SearchGroup(
    children=[
        NATIVE_CATEGORY_CONCERTS_EVENEMENTS,
        NATIVE_CATEGORY_FESTIVALS,
    ],
    search_value="CONCERTS_FESTIVALS",
    label="Concerts & festivals",
    included_subcategories=["ABO_CONCERT", "CONCERT", "EVENEMENT_MUSIQUE", "FESTIVAL_MUSIQUE"],
)
SEARCH_GROUP_EVENEMENTS_EN_LIGNE = SearchGroup(
    children=[
        NATIVE_CATEGORY_CONCERTS_EN_LIGNE,
        NATIVE_CATEGORY_PRATIQUE_ARTISTIQUE_EN_LIGNE,
        NATIVE_CATEGORY_RENCONTRES_EN_LIGNE,
    ],
    search_value="EVENEMENTS_EN_LIGNE",
    label="Évènements en ligne",
    included_subcategories=["LIVESTREAM_EVENEMENT", "LIVESTREAM_MUSIQUE", "LIVESTREAM_PRATIQUE_ARTISTIQUE"],
)
# FIXME (thconte, 2024-10-03): Delete this SearchGroup once app's minimal version has bumped
SEARCH_GROUP_FILMS_SERIES_CINEMA = SearchGroup(
    children=[
        NATIVE_CATEGORY_ABO_PLATEFORME_VIDEO,
        NATIVE_CATEGORY_CARTES_CINEMA,
        NATIVE_CATEGORY_DVD_BLU_RAY,
        NATIVE_CATEGORY_EVENEMENTS_CINEMA,
        NATIVE_CATEGORY_SEANCES_DE_CINEMA,
        NATIVE_CATEGORY_VIDEOS_ET_DOCUMENTAIRES,
    ],
    search_value="FILMS_SERIES_CINEMA",
    label="Cinéma, films et séries",
    included_subcategories=[
        "ABO_PLATEFORME_VIDEO",
        "AUTRE_SUPPORT_NUMERIQUE",
        "CARTE_CINE_ILLIMITE",
        "CARTE_CINE_MULTISEANCES",
        "CINE_PLEIN_AIR",
        "CINE_VENTE_DISTANCE",
        "EVENEMENT_CINE",
        "FESTIVAL_CINE",
        "SEANCE_CINE",
        "SUPPORT_PHYSIQUE_FILM",
        "VOD",
    ],
)
SEARCH_GROUP_CINEMA = SearchGroup(
    children=[
        NATIVE_CATEGORY_SEANCES_DE_CINEMA,
        NATIVE_CATEGORY_CARTES_CINEMA,
        NATIVE_CATEGORY_EVENEMENTS_CINEMA,
    ],
    search_value="CINEMA",
    label="Cinéma",
    included_subcategories=[
        "CARTE_CINE_ILLIMITE",
        "CARTE_CINE_MULTISEANCES",
        "CINE_PLEIN_AIR",
        "CINE_VENTE_DISTANCE",
        "EVENEMENT_CINE",
        "FESTIVAL_CINE",
        "SEANCE_CINE",
    ],
)
SEARCH_GROUP_FILMS_DOCUMENTAIRES_SERIES = SearchGroup(
    children=[
        NATIVE_CATEGORY_ABO_PLATEFORME_VIDEO,
        NATIVE_CATEGORY_DVD_BLU_RAY,
        NATIVE_CATEGORY_VIDEOS_ET_DOCUMENTAIRES,
    ],
    search_value="FILMS_DOCUMENTAIRES_SERIES",
    label="Films, séries et documentaires",
    included_subcategories=["ABO_PLATEFORME_VIDEO", "AUTRE_SUPPORT_NUMERIQUE", "SUPPORT_PHYSIQUE_FILM", "VOD"],
)
# FIXME (thconte, 2024-10-15): Delete this SearchGroup once app's minimal version has bumped
SEARCH_GROUP_INSTRUMENTS = SearchGroup(
    children=[
        NATIVE_CATEGORY_ACHAT_LOCATION_INSTRUMENT,
        NATIVE_CATEGORY_PARTITIONS_DE_MUSIQUE,
    ],
    search_value="INSTRUMENTS",
    label="Instruments de musique",
    included_subcategories=["ACHAT_INSTRUMENT", "BON_ACHAT_INSTRUMENT", "LOCATION_INSTRUMENT", "PARTITION"],
)
SEARCH_GROUP_JEUX_JEUX_VIDEOS = SearchGroup(
    children=[
        NATIVE_CATEGORY_CONCOURS,
        NATIVE_CATEGORY_ESCAPE_GAMES,
        NATIVE_CATEGORY_JEUX_EN_LIGNE,
        NATIVE_CATEGORY_LUDOTHEQUE,
        NATIVE_CATEGORY_RENCONTRES_EVENEMENTS,
    ],
    search_value="JEUX_JEUX_VIDEOS",
    label="Jeux & jeux vidéos",
    included_subcategories=[
        "ABO_JEU_VIDEO",
        "ABO_LUDOTHEQUE",
        "CONCOURS",
        "ESCAPE_GAME",
        "EVENEMENT_JEU",
        "JEU_EN_LIGNE",
        "RENCONTRE_JEU",
    ],
)
SEARCH_GROUP_LIVRES = SearchGroup(
    children=[
        NATIVE_CATEGORY_BIBLIOTHEQUE_MEDIATHEQUE,
        NATIVE_CATEGORY_FESTIVAL_DU_LIVRE,
        NATIVE_CATEGORY_LIVRES_AUDIO_PHYSIQUES,
        NATIVE_CATEGORY_LIVRES_NUMERIQUE_ET_AUDIO,
        NATIVE_CATEGORY_LIVRES_PAPIER,
    ],
    search_value="LIVRES",
    label="Livres",
    included_subcategories=[
        "ABO_BIBLIOTHEQUE",
        "ABO_LIVRE_NUMERIQUE",
        "ABO_MEDIATHEQUE",
        "FESTIVAL_LIVRE",
        "LIVRE_AUDIO_PHYSIQUE",
        "LIVRE_NUMERIQUE",
        "LIVRE_PAPIER",
        "TELECHARGEMENT_LIVRE_AUDIO",
    ],
)
SEARCH_GROUP_MEDIA_PRESSE = SearchGroup(
    children=[NATIVE_CATEGORY_AUTRES_MEDIAS, NATIVE_CATEGORY_PODCAST, NATIVE_CATEGORY_PRESSE_EN_LIGNE],
    search_value="MEDIA_PRESSE",
    label="Médias & presse",
    included_subcategories=["ABO_PRESSE_EN_LIGNE", "APP_CULTURELLE", "PODCAST"],
)
SEARCH_GROUP_MUSEES_VISITES_CULTURELLES = SearchGroup(
    children=[
        NATIVE_CATEGORY_ABONNEMENTS_MUSEE,
        NATIVE_CATEGORY_EVENEMENTS_PATRIMOINE,
        NATIVE_CATEGORY_VISITES_CULTURELLES,
        NATIVE_CATEGORY_VISITES_CULTURELLES_EN_LIGNE,
    ],
    search_value="MUSEES_VISITES_CULTURELLES",
    label="Musées & visites culturelles",
    included_subcategories=[
        "CARTE_MUSEE",
        "EVENEMENT_PATRIMOINE",
        "FESTIVAL_ART_VISUEL",
        "MUSEE_VENTE_DISTANCE",
        "VISITE_GUIDEE",
        "VISITE_VIRTUELLE",
        "VISITE",
    ],
)
SEARCH_GROUP_MUSIQUE = SearchGroup(
    children=[
        NATIVE_CATEGORY_ACHAT_LOCATION_INSTRUMENT,
        NATIVE_CATEGORY_CD,
        NATIVE_CATEGORY_CONCERTS_EVENEMENTS,
        NATIVE_CATEGORY_FESTIVALS,
        NATIVE_CATEGORY_MUSIQUE_EN_LIGNE,
        NATIVE_CATEGORY_PARTITIONS_DE_MUSIQUE,
        NATIVE_CATEGORY_VINYLES,
    ],
    search_value="MUSIQUE",
    label="Musique",
    included_subcategories=[
        "ABO_CONCERT",
        "ABO_PLATEFORME_MUSIQUE",
        "ACHAT_INSTRUMENT",
        "BON_ACHAT_INSTRUMENT",
        "CONCERT",
        "EVENEMENT_MUSIQUE",
        "FESTIVAL_MUSIQUE",
        "LOCATION_INSTRUMENT",
        "PARTITION",
        "SUPPORT_PHYSIQUE_MUSIQUE_CD",
        "SUPPORT_PHYSIQUE_MUSIQUE_VINYLE",
        "TELECHARGEMENT_MUSIQUE",
    ],
)
SEARCH_GROUP_NONE = SearchGroup(
    children=[],
    search_value="NONE",
    label="None",
    included_subcategories=["ACTIVATION_EVENT", "ACTIVATION_THING", "JEU_SUPPORT_PHYSIQUE"],
)
SEARCH_GROUP_RENCONTRES_CONFERENCES = SearchGroup(
    children=[
        NATIVE_CATEGORY_CONFERENCES,
        NATIVE_CATEGORY_RENCONTRES,
        NATIVE_CATEGORY_RENCONTRES_EN_LIGNE,
        NATIVE_CATEGORY_SALONS_ET_METIERS,
    ],
    search_value="RENCONTRES_CONFERENCES",
    label="Conférences & rencontres",
    included_subcategories=["CONFERENCE", "DECOUVERTE_METIERS", "RENCONTRE_EN_LIGNE", "RENCONTRE", "SALON"],
)
SEARCH_GROUP_SPECTACLES = SearchGroup(
    children=[
        NATIVE_CATEGORY_ABONNEMENTS_SPECTACLE,
        NATIVE_CATEGORY_SPECTACLES_ENREGISTRES,
        NATIVE_CATEGORY_SPECTACLES_REPRESENTATIONS,
    ],
    search_value="SPECTACLES",
    label="Spectacles",
    included_subcategories=[
        "ABO_SPECTACLE",
        "FESTIVAL_SPECTACLE",
        "SPECTACLE_ENREGISTRE",
        "SPECTACLE_REPRESENTATION",
        "SPECTACLE_VENTE_DISTANCE",
    ],
)
SEARCH_GROUP_THEATRE_ET_SPECTACLES = SearchGroup(
    children=[
        NATIVE_CATEGORY_THEATRES_ET_HUMOUR,
        NATIVE_CATEGORY_SPECTACLES,
        NATIVE_CATEGORY_FESTIVALS_DE_SPECTACLES,
        NATIVE_CATEGORY_ABONNEMENTS_SPECTACLE,
        NATIVE_CATEGORY_AUTRES_REPRESENTATIONS,
    ],
    search_value="THEATRE_ET_SPECTACLES",
    label="Théâtre et spectacles",
    included_subcategories=[
        "ABO_SPECTACLE",
        "FESTIVAL_SPECTACLE",
        "SPECTACLE_ENREGISTRE",
        "SPECTACLE_REPRESENTATION",
        "SPECTACLE_VENTE_DISTANCE",
    ],
)
# endregion

SEARCH_NODES_ROOT = SearchNode(
    label="Root",
    children=[
        SEARCH_GROUP_CONCERTS_FESTIVALS,
        SEARCH_GROUP_FILMS_SERIES_CINEMA,
        SEARCH_GROUP_CINEMA,
        SEARCH_GROUP_FILMS_DOCUMENTAIRES_SERIES,
        SEARCH_GROUP_LIVRES,
        SEARCH_GROUP_MUSIQUE,
        SEARCH_GROUP_CD_VINYLE_MUSIQUE_EN_LIGNE,
        SEARCH_GROUP_ARTS_LOISIRS_CREATIFS,
        SEARCH_GROUP_SPECTACLES,
        SEARCH_GROUP_MUSEES_VISITES_CULTURELLES,
        SEARCH_GROUP_JEUX_JEUX_VIDEOS,
        SEARCH_GROUP_INSTRUMENTS,
        SEARCH_GROUP_MEDIA_PRESSE,
        SEARCH_GROUP_CARTES_JEUNES,
        SEARCH_GROUP_RENCONTRES_CONFERENCES,
        SEARCH_GROUP_EVENEMENTS_EN_LIGNE,
        SEARCH_GROUP_THEATRE_ET_SPECTACLES,
        SEARCH_GROUP_NONE,
    ],
)

SEARCH_GROUPS = get_search_groups()
NATIVE_CATEGORIES = get_native_categories()
SEARCH_NODES = get_all_instances()
