from dataclasses import dataclass

from pcapi.core.providers.constants import TITELIVE_MUSIC_GENRES_BY_GTL_ID
from pcapi.core.providers.constants import TITELIVE_MUSIC_LABELS_BY_GTL_ID
from pcapi.core.providers.constants import TITELIVE_MUSIC_TYPES


@dataclass
class OldMusicSubType:
    code: int
    label: str
    slug: str


@dataclass
class OldMusicType:
    code: int
    label: str
    children: list[OldMusicSubType]


@dataclass
class MusicType:
    label: str
    name: str


OTHER_SHOW_TYPE_SLUG = "OTHER"

# WARNING: the list below MUST be kept in sync with the list at pro/src/core/Offers/categoriesSubTypes.ts
OLD_MUSIC_TYPES = [
    OldMusicType(
        code=501,
        label="Jazz",
        children=[
            OldMusicSubType(code=502, label="Acid Jazz", slug="JAZZ-ACID_JAZZ"),
            OldMusicSubType(code=503, label="Avant-Garde Jazz", slug="JAZZ-AVANT_GARDE_JAZZ"),
            OldMusicSubType(code=504, label="Bebop", slug="JAZZ-BEBOP"),
            OldMusicSubType(code=505, label="Big Band", slug="JAZZ-BIG_BAND"),
            OldMusicSubType(code=506, label="Blue Note", slug="JAZZ-BLUE_NOTE"),
            OldMusicSubType(code=507, label="Cool Jazz", slug="JAZZ-COOL_JAZZ"),
            OldMusicSubType(code=508, label="Crossover Jazz", slug="JAZZ-CROSSOVER_JAZZ"),
            OldMusicSubType(code=509, label="Dixieland", slug="JAZZ-DIXIELAND"),
            OldMusicSubType(code=510, label="Ethio Jazz", slug="JAZZ-ETHIO_JAZZ"),
            OldMusicSubType(code=511, label="Fusion", slug="JAZZ-FUSION"),
            OldMusicSubType(code=512, label="Jazz Contemporain", slug="JAZZ-JAZZ_CONTEMPORAIN"),
            OldMusicSubType(code=513, label="Jazz Funk", slug="JAZZ-JAZZ_FUNK"),
            OldMusicSubType(code=514, label="Mainstream", slug="JAZZ-MAINSTREAM"),
            OldMusicSubType(code=515, label="Manouche", slug="JAZZ-MANOUCHE"),
            OldMusicSubType(code=516, label="Traditionel", slug="JAZZ-TRADITIONEL"),
            OldMusicSubType(code=517, label="Vocal Jazz", slug="JAZZ-VOCAL_JAZZ"),
            OldMusicSubType(code=518, label="Ragtime", slug="JAZZ-RAGTIME"),
            OldMusicSubType(code=519, label="Smooth", slug="JAZZ-SMOOTH"),
            OldMusicSubType(code=-1, label="Autre", slug="JAZZ-OTHER"),
        ],
    ),
    OldMusicType(
        code=520,
        label="Blues",
        children=[
            OldMusicSubType(code=521, label="Blues Acoustique", slug="BLUES-BLUES_ACOUSTIQUE"),
            OldMusicSubType(code=522, label="Blues Contemporain", slug="BLUES-BLUES_CONTEMPORAIN"),
            OldMusicSubType(code=523, label="Blues Électrique", slug="BLUES-BLUES_ELECTRIQUE"),
            OldMusicSubType(code=524, label="Blues Rock", slug="BLUES-BLUES_ROCK"),
            OldMusicSubType(code=525, label="Chicago Blues", slug="BLUES-CHICAGO_BLUES"),
            OldMusicSubType(code=526, label="Classic Blues", slug="BLUES-CLASSIC_BLUES"),
            OldMusicSubType(code=527, label="Country Blues", slug="BLUES-COUNTRY_BLUES"),
            OldMusicSubType(code=528, label="Delta Blues", slug="BLUES-DELTA_BLUES"),
            OldMusicSubType(code=529, label="Ragtime", slug="BLUES-RAGTIME"),
            OldMusicSubType(code=-1, label="Autre", slug="BLUES-OTHER"),
        ],
    ),
    OldMusicType(
        code=530,
        label="Reggae",
        children=[
            OldMusicSubType(code=531, label="2-Tone", slug="REGGAE-TWO_TONE"),
            OldMusicSubType(code=532, label="Dancehall", slug="REGGAE-DANCEHALL"),
            OldMusicSubType(code=533, label="Dub", slug="REGGAE-DUB"),
            OldMusicSubType(code=534, label="Roots ", slug="REGGAE-ROOTS"),
            OldMusicSubType(code=535, label="Ska", slug="REGGAE-SKA"),
            OldMusicSubType(code=536, label="Zouk ", slug="REGGAE-ZOUK"),
            OldMusicSubType(code=-1, label="Autre", slug="REGGAE-OTHER"),
        ],
    ),
    OldMusicType(
        code=600,
        label="Classique",
        children=[
            OldMusicSubType(code=601, label="Avant-garde", slug="CLASSIQUE-AVANT_GARDE"),
            OldMusicSubType(code=602, label="Baroque", slug="CLASSIQUE-BAROQUE"),
            OldMusicSubType(code=603, label="Chant", slug="CLASSIQUE-CHANT"),
            OldMusicSubType(code=604, label="Chorale", slug="CLASSIQUE-CHORALE"),
            OldMusicSubType(code=605, label="Contemporain", slug="CLASSIQUE-CONTEMPORAIN"),
            OldMusicSubType(code=606, label="Expressioniste", slug="CLASSIQUE-EXPRESSIONISTE"),
            OldMusicSubType(code=607, label="Impressioniste", slug="CLASSIQUE-IMPRESSIONISTE"),
            OldMusicSubType(code=608, label="Médievale", slug="CLASSIQUE-MEDIEVALE"),
            OldMusicSubType(code=609, label="Minimaliste", slug="CLASSIQUE-MINIMALISTE"),
            OldMusicSubType(code=610, label="Moderne ", slug="CLASSIQUE-MODERNE"),
            OldMusicSubType(code=611, label="Oratorio", slug="CLASSIQUE-ORATORIO"),
            OldMusicSubType(code=612, label="Opéra", slug="CLASSIQUE-OPERA"),
            OldMusicSubType(code=613, label="Renaissance", slug="CLASSIQUE-RENAISSANCE"),
            OldMusicSubType(code=614, label="Romantique", slug="CLASSIQUE-ROMANTIQUE"),
            OldMusicSubType(code=-1, label="Autre", slug="CLASSIQUE-OTHER"),
        ],
    ),
    OldMusicType(
        code=700,
        label="Musique du Monde",
        children=[
            OldMusicSubType(code=701, label="Africaine", slug="MUSIQUE_DU_MONDE-AFRICAINE"),
            OldMusicSubType(code=702, label="Afro Beat", slug="MUSIQUE_DU_MONDE-AFRO_BEAT"),
            OldMusicSubType(code=703, label="Afro Pop", slug="MUSIQUE_DU_MONDE-AFRO_POP"),
            OldMusicSubType(code=704, label="Alternativo ", slug="MUSIQUE_DU_MONDE-ALTERNATIVO"),
            OldMusicSubType(code=705, label="Amérique du Nord", slug="MUSIQUE_DU_MONDE-AMERIQUE_DU_NORD"),
            OldMusicSubType(code=706, label="Amérique du Sud", slug="MUSIQUE_DU_MONDE-AMERIQUE_DU_SUD"),
            OldMusicSubType(code=707, label="Asiatique", slug="MUSIQUE_DU_MONDE-ASIATIQUE"),
            OldMusicSubType(code=708, label="Baladas y Boleros", slug="MUSIQUE_DU_MONDE-BALADAS_Y_BOLEROS"),
            OldMusicSubType(code=709, label="Bossa Nova", slug="MUSIQUE_DU_MONDE-BOSSA_NOVA"),
            OldMusicSubType(code=710, label="Brésilienne", slug="MUSIQUE_DU_MONDE-BRESILIENNE"),
            OldMusicSubType(code=711, label="Cajun", slug="MUSIQUE_DU_MONDE-CAJUN"),
            OldMusicSubType(code=712, label="Calypso", slug="MUSIQUE_DU_MONDE-CALYPSO"),
            OldMusicSubType(code=713, label="Caribéenne", slug="MUSIQUE_DU_MONDE-CARIBEENNE"),
            OldMusicSubType(code=714, label="Celtique", slug="MUSIQUE_DU_MONDE-CELTIQUE"),
            OldMusicSubType(code=715, label="Cumbia ", slug="MUSIQUE_DU_MONDE-CUMBIA"),
            OldMusicSubType(code=716, label="Flamenco", slug="MUSIQUE_DU_MONDE-FLAMENCO"),
            OldMusicSubType(code=717, label="Grècque", slug="MUSIQUE_DU_MONDE-GRECQUE"),
            OldMusicSubType(code=718, label="Indienne", slug="MUSIQUE_DU_MONDE-INDIENNE"),
            OldMusicSubType(code=719, label="Latin Jazz", slug="MUSIQUE_DU_MONDE-LATIN_JAZZ"),
            OldMusicSubType(code=720, label="Moyen-Orient", slug="MUSIQUE_DU_MONDE-MOYEN_ORIENT"),
            OldMusicSubType(
                code=721, label="Musique Latine Contemporaine", slug="MUSIQUE_DU_MONDE-LATINE_CONTEMPORAINE"
            ),
            OldMusicSubType(code=722, label="Nuevo Flamenco", slug="MUSIQUE_DU_MONDE-NUEVO_FLAMENCO"),
            OldMusicSubType(code=723, label="Pop Latino", slug="MUSIQUE_DU_MONDE-POP_LATINO"),
            OldMusicSubType(code=724, label="Portuguese fado ", slug="MUSIQUE_DU_MONDE-PORTUGUESE_FADO"),
            OldMusicSubType(code=725, label="Rai", slug="MUSIQUE_DU_MONDE-RAI"),
            OldMusicSubType(code=726, label="Salsa", slug="MUSIQUE_DU_MONDE-SALSA"),
            OldMusicSubType(code=727, label="Tango Argentin", slug="MUSIQUE_DU_MONDE-TANGO_ARGENTIN"),
            OldMusicSubType(code=728, label="Yiddish", slug="MUSIQUE_DU_MONDE-YIDDISH"),
            OldMusicSubType(code=-1, label="Autre", slug="MUSIQUE_DU_MONDE-OTHER"),
        ],
    ),
    OldMusicType(
        code=800,
        label="Pop",
        children=[
            OldMusicSubType(code=801, label="Britpop", slug="POP-BRITPOP"),
            OldMusicSubType(code=802, label="Bubblegum ", slug="POP-BUBBLEGUM"),
            OldMusicSubType(code=803, label="Dance Pop", slug="POP-DANCE_POP"),
            OldMusicSubType(code=804, label="Dream Pop ", slug="POP-DREAM_POP"),
            OldMusicSubType(code=805, label="Electro Pop", slug="POP-ELECTRO_POP"),
            OldMusicSubType(code=806, label="Indie Pop", slug="POP-INDIE_POP"),
            OldMusicSubType(code=808, label="J-Pop", slug="POP-J_POP"),
            OldMusicSubType(code=809, label="K-Pop", slug="POP-K_POP"),
            OldMusicSubType(code=810, label="Pop Punk ", slug="POP-POP_PUNK"),
            OldMusicSubType(code=811, label="Pop/Rock", slug="POP-POP_ROCK"),
            OldMusicSubType(code=812, label="Power Pop ", slug="POP-POWER_POP"),
            OldMusicSubType(code=813, label="Soft Rock", slug="POP-SOFT_ROCK"),
            OldMusicSubType(code=814, label="Synthpop ", slug="POP-SYNTHPOP"),
            OldMusicSubType(code=815, label="Teen Pop", slug="POP-TEEN_POP"),
            OldMusicSubType(code=-1, label="Autre", slug="POP-OTHER"),
        ],
    ),
    OldMusicType(
        code=820,
        label="Rock",
        children=[
            OldMusicSubType(code=821, label="Acid Rock ", slug="ROCK-ACID_ROCK"),
            OldMusicSubType(code=822, label="Arena Rock", slug="ROCK-ARENA_ROCK"),
            OldMusicSubType(code=823, label="Art Rock", slug="ROCK-ART_ROCK"),
            OldMusicSubType(code=824, label="College Rock", slug="ROCK-COLLEGE_ROCK"),
            OldMusicSubType(code=825, label="Glam Rock", slug="ROCK-GLAM_ROCK"),
            OldMusicSubType(code=826, label="Grunge", slug="ROCK-GRUNGE"),
            OldMusicSubType(code=827, label="Hard Rock", slug="ROCK-HARD_ROCK"),
            OldMusicSubType(code=828, label="Indie Rock", slug="ROCK-INDIE_ROCK"),
            OldMusicSubType(code=829, label="Lo-fi", slug="ROCK-LO_FI"),
            OldMusicSubType(code=830, label="Prog-Rock", slug="ROCK-PROG_ROCK"),
            OldMusicSubType(code=831, label="Psychedelic", slug="ROCK-PSYCHEDELIC"),
            OldMusicSubType(code=832, label="Rock & Roll", slug="ROCK-ROCK_N_ROLL"),
            OldMusicSubType(code=833, label="Rock Experimental", slug="ROCK-EXPERIMENTAL"),
            OldMusicSubType(code=834, label="Rockabilly", slug="ROCK-ROCKABILLY"),
            OldMusicSubType(code=835, label="Shoegaze", slug="ROCK-SHOEGAZE"),
            OldMusicSubType(code=836, label="Rock Electro", slug="ROCK-ELECTRO"),
            OldMusicSubType(code=-1, label="Autre", slug="ROCK-OTHER"),
        ],
    ),
    OldMusicType(
        code=840,
        label="Metal",
        children=[
            OldMusicSubType(code=841, label="Black Metal", slug="METAL-BLACK_METAL"),
            OldMusicSubType(code=842, label="Death Metal ", slug="METAL-DEATH_METAL"),
            OldMusicSubType(code=843, label="Doom Metal", slug="METAL-DOOM_METAL"),
            OldMusicSubType(code=844, label="Gothic ", slug="METAL-GOTHIC"),
            OldMusicSubType(code=845, label="Metal Core", slug="METAL-METAL_CORE"),
            OldMusicSubType(code=846, label="Metal Progressif", slug="METAL-METAL_PROGRESSIF"),
            OldMusicSubType(code=847, label="Trash Metal", slug="METAL-TRASH_METAL"),
            OldMusicSubType(code=848, label="Metal Industriel", slug="METAL-METAL_INDUSTRIEL"),
            OldMusicSubType(code=849, label="Fusion", slug="METAL-FUSION"),
            OldMusicSubType(code=-1, label="Autre", slug="METAL-OTHER"),
        ],
    ),
    OldMusicType(
        code=850,
        label="Punk",
        children=[
            OldMusicSubType(code=851, label="Post Punk ", slug="PUNK-POST_PUNK"),
            OldMusicSubType(code=852, label="Hardcore Punk", slug="PUNK-HARDCORE_PUNK"),
            OldMusicSubType(code=853, label="Afro Punk", slug="PUNK-AFRO_PUNK"),
            OldMusicSubType(code=854, label="Grindcore", slug="PUNK-GRINDCORE"),
            OldMusicSubType(code=855, label="Noise Rock ", slug="PUNK-NOISE_ROCK"),
            OldMusicSubType(code=-1, label="Autre", slug="PUNK-OTHER"),
        ],
    ),
    OldMusicType(
        code=860,
        label="Folk",
        children=[
            OldMusicSubType(code=861, label="Folk Contemporaine", slug="FOLK-FOLK_CONTEMPORAINE"),
            OldMusicSubType(code=862, label="Indie Folk", slug="FOLK-INDIE_FOLK"),
            OldMusicSubType(code=863, label="Folk Rock", slug="FOLK-FOLK_ROCK"),
            OldMusicSubType(code=864, label="New Acoustic", slug="FOLK-NEW_ACOUSTIC"),
            OldMusicSubType(code=865, label="Folk Traditionelle", slug="FOLK-FOLK_TRADITIONELLE"),
            OldMusicSubType(code=866, label="Tex-Mex", slug="FOLK-TEX_MEX"),
            OldMusicSubType(code=-1, label="Autre", slug="FOLK-OTHER"),
        ],
    ),
    OldMusicType(
        code=870,
        label="Country",
        children=[
            OldMusicSubType(code=871, label="Country Alternative", slug="COUNTRY-COUNTRY_ALTERNATIVE"),
            OldMusicSubType(code=872, label="Americana", slug="COUNTRY-AMERICANA"),
            OldMusicSubType(code=873, label="Bluegrass", slug="COUNTRY-BLUEGRASS"),
            OldMusicSubType(code=874, label="Country Contemporaine", slug="COUNTRY-COUNTRY_CONTEMPORAINE"),
            OldMusicSubType(code=875, label="Gospel Country", slug="COUNTRY-GOSPEL_COUNTRY"),
            OldMusicSubType(code=876, label="Country Pop", slug="COUNTRY-COUNTRY_POP"),
            OldMusicSubType(code=-1, label="Autre", slug="COUNTRY-OTHER"),
        ],
    ),
    OldMusicType(
        code=880,
        label="Electro",
        children=[
            OldMusicSubType(code=881, label="Bitpop", slug="ELECTRO-BITPOP"),
            OldMusicSubType(code=882, label="Breakbeat ", slug="ELECTRO-BREAKBEAT"),
            OldMusicSubType(code=883, label="Chillwave", slug="ELECTRO-CHILLWAVE"),
            OldMusicSubType(code=884, label="Dance", slug="ELECTRO-DANCE"),
            OldMusicSubType(code=885, label="Downtempo", slug="ELECTRO-DOWNTEMPO"),
            OldMusicSubType(code=886, label="Drum & Bass ", slug="ELECTRO-DRUM_AND_BASS"),
            OldMusicSubType(code=887, label="Dubstep", slug="ELECTRO-DUBSTEP"),
            OldMusicSubType(code=888, label="Electro Experimental", slug="ELECTRO-EXPERIMENTAL"),
            OldMusicSubType(code=889, label="Electronica", slug="ELECTRO-ELECTRONICA"),
            OldMusicSubType(code=890, label="Garage", slug="ELECTRO-GARAGE"),
            OldMusicSubType(code=891, label="Grime", slug="ELECTRO-GRIME"),
            OldMusicSubType(code=892, label="Hard Dance", slug="ELECTRO-HARD_DANCE"),
            OldMusicSubType(code=893, label="Hardcore", slug="ELECTRO-HARDCORE"),
            OldMusicSubType(code=894, label="House", slug="ELECTRO-HOUSE"),
            OldMusicSubType(code=895, label="Industriel", slug="ELECTRO-INDUSTRIEL"),
            OldMusicSubType(code=896, label="Lounge", slug="ELECTRO-LOUNGE"),
            OldMusicSubType(code=897, label="Techno", slug="ELECTRO-TECHNO"),
            OldMusicSubType(code=898, label="Trance", slug="ELECTRO-TRANCE"),
            OldMusicSubType(code=-1, label="Autre", slug="ELECTRO-OTHER"),
        ],
    ),
    OldMusicType(
        code=900,
        label="Hip-Hop/Rap",
        children=[
            OldMusicSubType(code=901, label="Bounce", slug="HIP_HOP_RAP-BOUNCE"),
            OldMusicSubType(code=902, label="Hip Hop", slug="HIP_HOP_RAP-HIP_HOP"),
            OldMusicSubType(code=903, label="Rap Alternatif", slug="HIP_HOP_RAP-RAP_ALTERNATIF"),
            OldMusicSubType(code=905, label="Rap East Coast", slug="HIP_HOP_RAP-RAP_EAST_COAST"),
            OldMusicSubType(code=906, label="Rap Français", slug="HIP_HOP_RAP-RAP_FRANCAIS"),
            OldMusicSubType(code=907, label="Rap Gangsta", slug="HIP_HOP_RAP-RAP_GANGSTA"),
            OldMusicSubType(code=908, label="Rap Hardcore", slug="HIP_HOP_RAP-RAP_HARDCORE"),
            OldMusicSubType(code=909, label="Rap Latino", slug="HIP_HOP_RAP-RAP_LATINO"),
            OldMusicSubType(code=910, label="Rap Old School", slug="HIP_HOP_RAP-RAP_OLD_SCHOOL"),
            OldMusicSubType(code=911, label="Rap Underground", slug="HIP_HOP_RAP-RAP_UNDERGROUND"),
            OldMusicSubType(code=912, label="Rap West Coast", slug="HIP_HOP_RAP-RAP_WEST_COAST"),
            OldMusicSubType(code=913, label="Trap", slug="HIP_HOP_RAP-TRAP"),
            OldMusicSubType(code=914, label="Trip Hop", slug="HIP_HOP_RAP-TRIP_HOP"),
            OldMusicSubType(code=921, label="R&B Contemporain", slug="HIP_HOP_RAP-R&B_CONTEMPORAIN"),
            OldMusicSubType(code=922, label="Disco", slug="HIP_HOP_RAP-DISCO"),
            OldMusicSubType(code=923, label="Doo Wop", slug="HIP_HOP_RAP-DOO_WOP"),
            OldMusicSubType(code=924, label="Funk", slug="HIP_HOP_RAP-FUNK"),
            OldMusicSubType(code=925, label="Soul", slug="HIP_HOP_RAP-SOUL"),
            OldMusicSubType(code=926, label="Motown", slug="HIP_HOP_RAP-MOTOWN"),
            OldMusicSubType(code=927, label="Neo Soul", slug="HIP_HOP_RAP-NEO_SOUL"),
            OldMusicSubType(code=928, label="Soul Psychedelique", slug="HIP_HOP_RAP-SOUL_PSYCHEDELIQUE"),
            OldMusicSubType(code=-1, label="Autre", slug="HIP_HOP_RAP-OTHER"),
        ],
    ),
    OldMusicType(
        code=930,
        label="Gospel",
        children=[
            OldMusicSubType(code=931, label="Spiritual Gospel", slug="GOSPEL-SPIRITUAL_GOSPEL"),
            OldMusicSubType(code=932, label="Traditional Gospel", slug="GOSPEL-TRADITIONAL_GOSPEL"),
            OldMusicSubType(code=933, label="Southern Gospel", slug="GOSPEL-SOUTHERN_GOSPEL"),
            OldMusicSubType(code=934, label="Contemporary Gospel", slug="GOSPEL-CONTEMPORARY_GOSPEL"),
            OldMusicSubType(code=935, label="Bluegrass Gospel", slug="GOSPEL-BLUEGRASS_GOSPEL"),
            OldMusicSubType(code=936, label="Blues Gospel", slug="GOSPEL-BLUES_GOSPEL"),
            OldMusicSubType(code=937, label="Country Gospel", slug="GOSPEL-COUNTRY_GOSPEL"),
            OldMusicSubType(code=938, label="Hybrid Gospel", slug="GOSPEL-HYBRID_GOSPEL"),
            OldMusicSubType(code=-1, label="Autre", slug="GOSPEL-OTHER"),
        ],
    ),
    OldMusicType(
        code=1000,
        label="Chansons / Variétés",
        children=[
            OldMusicSubType(code=1001, label="Musette", slug="CHANSON_VARIETE-MUSETTE"),
            OldMusicSubType(code=1002, label="Chanson Française", slug="CHANSON_VARIETE-CHANSON_FRANCAISE"),
            OldMusicSubType(code=1003, label="Music Hall", slug="CHANSON_VARIETE-MUSIC_HALL"),
            OldMusicSubType(code=1004, label="Folklore français", slug="CHANSON_VARIETE-FOLKLORE_FRANCAIS"),
            OldMusicSubType(code=1005, label="Chanson à texte", slug="CHANSON_VARIETE-CHANSON_À_TEXTE"),
            OldMusicSubType(code=1006, label="Slam", slug="CHANSON_VARIETE-SLAM"),
            OldMusicSubType(code=-1, label="Autre", slug="CHANSON_VARIETE-OTHER"),
        ],
    ),
    OldMusicType(
        code=-1,
        label="Autre",
        children=[OldMusicSubType(code=-1, label="Autre", slug=OTHER_SHOW_TYPE_SLUG)],
    ),
]


MUSIC_TYPES = [
    MusicType(
        name=TITELIVE_MUSIC_GENRES_BY_GTL_ID[music_type.gtl_id],
        label=TITELIVE_MUSIC_LABELS_BY_GTL_ID[music_type.gtl_id],
    )
    for music_type in TITELIVE_MUSIC_TYPES
]

MUSIC_TYPES_BY_CODE = {music_type.code: music_type for music_type in OLD_MUSIC_TYPES}
MUSIC_TYPES_LABEL_BY_CODE = {music_type.code: music_type.label for music_type in OLD_MUSIC_TYPES}
MUSIC_TYPES_BY_SLUG = {
    music_sub_type.slug: music_type for music_type in OLD_MUSIC_TYPES for music_sub_type in music_type.children
}
MUSIC_SUB_TYPES_LABEL_BY_CODE = {
    music_sub_type.code: music_sub_type.label
    for music_type in OLD_MUSIC_TYPES
    for music_sub_type in music_type.children
}
MUSIC_SUB_TYPES_BY_CODE = {
    music_sub_type.code: music_sub_type for music_type in OLD_MUSIC_TYPES for music_sub_type in music_type.children
}  # WARNING: for code -1, the sub type is not unique, it returns the one with the slug CHANSON_VARIETE-OTHER
MUSIC_SUB_TYPES_BY_SLUG = {
    music_sub_type.slug: music_sub_type for music_type in OLD_MUSIC_TYPES for music_sub_type in music_type.children
}
