from dataclasses import dataclass


@dataclass
class MusicSubType:
    code: int
    label: str
    slug: str


@dataclass
class MusicType:
    code: int
    label: str
    children: list[MusicSubType]


OTHER_SHOW_TYPE_SLUG = "OTHER"


@dataclass
class TiteliveMusicType:
    gtl_id: str
    label: str
    can_be_event: bool = True


TITELIVE_MUSIC_TYPES = (
    TiteliveMusicType(gtl_id="01000000", label="Musique Classique"),
    TiteliveMusicType(gtl_id="02000000", label="Jazz / Blues"),
    TiteliveMusicType(gtl_id="03000000", label="Bandes originales", can_be_event=False),
    TiteliveMusicType(gtl_id="04000000", label="Electro"),
    TiteliveMusicType(gtl_id="05000000", label="Pop"),
    TiteliveMusicType(gtl_id="06000000", label="Rock"),
    TiteliveMusicType(gtl_id="07000000", label="Metal"),
    TiteliveMusicType(gtl_id="08000000", label="Alternatif"),
    TiteliveMusicType(gtl_id="09000000", label="Variétés"),
    TiteliveMusicType(gtl_id="10000000", label="Funk / Soul / RnB / Disco"),
    TiteliveMusicType(gtl_id="11000000", label="Rap/ Hip Hop"),
    TiteliveMusicType(gtl_id="12000000", label="Reggae / Ragga"),
    TiteliveMusicType(gtl_id="13000000", label="Musique du monde"),
    TiteliveMusicType(gtl_id="14000000", label="Country / Folk"),
    TiteliveMusicType(gtl_id="15000000", label="Vidéos musicales", can_be_event=False),
    TiteliveMusicType(gtl_id="16000000", label="Compilations", can_be_event=False),
    TiteliveMusicType(gtl_id="17000000", label="Ambiance"),
    TiteliveMusicType(gtl_id="18000000", label="Enfants", can_be_event=False),
    TiteliveMusicType(gtl_id="19000000", label="Autre"),
)

# WARNING: the list below MUST be kept in sync with the list at pro/src/core/Offers/categoriesSubTypes.ts
music_types = [
    MusicType(
        code=501,
        label="Jazz",
        children=[
            MusicSubType(code=502, label="Acid Jazz", slug="JAZZ-ACID_JAZZ"),
            MusicSubType(code=503, label="Avant-Garde Jazz", slug="JAZZ-AVANT_GARDE_JAZZ"),
            MusicSubType(code=504, label="Bebop", slug="JAZZ-BEBOP"),
            MusicSubType(code=505, label="Big Band", slug="JAZZ-BIG_BAND"),
            MusicSubType(code=506, label="Blue Note", slug="JAZZ-BLUE_NOTE"),
            MusicSubType(code=507, label="Cool Jazz", slug="JAZZ-COOL_JAZZ"),
            MusicSubType(code=508, label="Crossover Jazz", slug="JAZZ-CROSSOVER_JAZZ"),
            MusicSubType(code=509, label="Dixieland", slug="JAZZ-DIXIELAND"),
            MusicSubType(code=510, label="Ethio Jazz", slug="JAZZ-ETHIO_JAZZ"),
            MusicSubType(code=511, label="Fusion", slug="JAZZ-FUSION"),
            MusicSubType(code=512, label="Jazz Contemporain", slug="JAZZ-JAZZ_CONTEMPORAIN"),
            MusicSubType(code=513, label="Jazz Funk", slug="JAZZ-JAZZ_FUNK"),
            MusicSubType(code=514, label="Mainstream", slug="JAZZ-MAINSTREAM"),
            MusicSubType(code=515, label="Manouche", slug="JAZZ-MANOUCHE"),
            MusicSubType(code=516, label="Traditionel", slug="JAZZ-TRADITIONEL"),
            MusicSubType(code=517, label="Vocal Jazz", slug="JAZZ-VOCAL_JAZZ"),
            MusicSubType(code=518, label="Ragtime", slug="JAZZ-RAGTIME"),
            MusicSubType(code=519, label="Smooth", slug="JAZZ-SMOOTH"),
            MusicSubType(code=-1, label="Autre", slug="JAZZ-OTHER"),
        ],
    ),
    MusicType(
        code=520,
        label="Blues",
        children=[
            MusicSubType(code=521, label="Blues Acoustique", slug="BLUES-BLUES_ACOUSTIQUE"),
            MusicSubType(code=522, label="Blues Contemporain", slug="BLUES-BLUES_CONTEMPORAIN"),
            MusicSubType(code=523, label="Blues Électrique", slug="BLUES-BLUES_ELECTRIQUE"),
            MusicSubType(code=524, label="Blues Rock", slug="BLUES-BLUES_ROCK"),
            MusicSubType(code=525, label="Chicago Blues", slug="BLUES-CHICAGO_BLUES"),
            MusicSubType(code=526, label="Classic Blues", slug="BLUES-CLASSIC_BLUES"),
            MusicSubType(code=527, label="Country Blues", slug="BLUES-COUNTRY_BLUES"),
            MusicSubType(code=528, label="Delta Blues", slug="BLUES-DELTA_BLUES"),
            MusicSubType(code=529, label="Ragtime", slug="BLUES-RAGTIME"),
            MusicSubType(code=-1, label="Autre", slug="BLUES-OTHER"),
        ],
    ),
    MusicType(
        code=530,
        label="Reggae",
        children=[
            MusicSubType(code=531, label="2-Tone", slug="REGGAE-TWO_TONE"),
            MusicSubType(code=532, label="Dancehall", slug="REGGAE-DANCEHALL"),
            MusicSubType(code=533, label="Dub", slug="REGGAE-DUB"),
            MusicSubType(code=534, label="Roots ", slug="REGGAE-ROOTS"),
            MusicSubType(code=535, label="Ska", slug="REGGAE-SKA"),
            MusicSubType(code=536, label="Zouk ", slug="REGGAE-ZOUK"),
            MusicSubType(code=-1, label="Autre", slug="REGGAE-OTHER"),
        ],
    ),
    MusicType(
        code=600,
        label="Classique",
        children=[
            MusicSubType(code=601, label="Avant-garde", slug="CLASSIQUE-AVANT_GARDE"),
            MusicSubType(code=602, label="Baroque", slug="CLASSIQUE-BAROQUE"),
            MusicSubType(code=603, label="Chant", slug="CLASSIQUE-CHANT"),
            MusicSubType(code=604, label="Chorale", slug="CLASSIQUE-CHORALE"),
            MusicSubType(code=605, label="Contemporain", slug="CLASSIQUE-CONTEMPORAIN"),
            MusicSubType(code=606, label="Expressioniste", slug="CLASSIQUE-EXPRESSIONISTE"),
            MusicSubType(code=607, label="Impressioniste", slug="CLASSIQUE-IMPRESSIONISTE"),
            MusicSubType(code=608, label="Médievale", slug="CLASSIQUE-MEDIEVALE"),
            MusicSubType(code=609, label="Minimaliste", slug="CLASSIQUE-MINIMALISTE"),
            MusicSubType(code=610, label="Moderne ", slug="CLASSIQUE-MODERNE"),
            MusicSubType(code=611, label="Oratorio", slug="CLASSIQUE-ORATORIO"),
            MusicSubType(code=612, label="Opéra", slug="CLASSIQUE-OPERA"),
            MusicSubType(code=613, label="Renaissance", slug="CLASSIQUE-RENAISSANCE"),
            MusicSubType(code=614, label="Romantique", slug="CLASSIQUE-ROMANTIQUE"),
            MusicSubType(code=-1, label="Autre", slug="CLASSIQUE-OTHER"),
        ],
    ),
    MusicType(
        code=700,
        label="Musique du Monde",
        children=[
            MusicSubType(code=701, label="Africaine", slug="MUSIQUE_DU_MONDE-AFRICAINE"),
            MusicSubType(code=702, label="Afro Beat", slug="MUSIQUE_DU_MONDE-AFRO_BEAT"),
            MusicSubType(code=703, label="Afro Pop", slug="MUSIQUE_DU_MONDE-AFRO_POP"),
            MusicSubType(code=704, label="Alternativo ", slug="MUSIQUE_DU_MONDE-ALTERNATIVO"),
            MusicSubType(code=705, label="Amérique du Nord", slug="MUSIQUE_DU_MONDE-AMERIQUE_DU_NORD"),
            MusicSubType(code=706, label="Amérique du Sud", slug="MUSIQUE_DU_MONDE-AMERIQUE_DU_SUD"),
            MusicSubType(code=707, label="Asiatique", slug="MUSIQUE_DU_MONDE-ASIATIQUE"),
            MusicSubType(code=708, label="Baladas y Boleros", slug="MUSIQUE_DU_MONDE-BALADAS_Y_BOLEROS"),
            MusicSubType(code=709, label="Bossa Nova", slug="MUSIQUE_DU_MONDE-BOSSA_NOVA"),
            MusicSubType(code=710, label="Brésilienne", slug="MUSIQUE_DU_MONDE-BRESILIENNE"),
            MusicSubType(code=711, label="Cajun", slug="MUSIQUE_DU_MONDE-CAJUN"),
            MusicSubType(code=712, label="Calypso", slug="MUSIQUE_DU_MONDE-CALYPSO"),
            MusicSubType(code=713, label="Caribéenne", slug="MUSIQUE_DU_MONDE-CARIBEENNE"),
            MusicSubType(code=714, label="Celtique", slug="MUSIQUE_DU_MONDE-CELTIQUE"),
            MusicSubType(code=715, label="Cumbia ", slug="MUSIQUE_DU_MONDE-CUMBIA"),
            MusicSubType(code=716, label="Flamenco", slug="MUSIQUE_DU_MONDE-FLAMENCO"),
            MusicSubType(code=717, label="Grècque", slug="MUSIQUE_DU_MONDE-GRECQUE"),
            MusicSubType(code=718, label="Indienne", slug="MUSIQUE_DU_MONDE-INDIENNE"),
            MusicSubType(code=719, label="Latin Jazz", slug="MUSIQUE_DU_MONDE-LATIN_JAZZ"),
            MusicSubType(code=720, label="Moyen-Orient", slug="MUSIQUE_DU_MONDE-MOYEN_ORIENT"),
            MusicSubType(code=721, label="Musique Latine Contemporaine", slug="MUSIQUE_DU_MONDE-LATINE_CONTEMPORAINE"),
            MusicSubType(code=722, label="Nuevo Flamenco", slug="MUSIQUE_DU_MONDE-NUEVO_FLAMENCO"),
            MusicSubType(code=723, label="Pop Latino", slug="MUSIQUE_DU_MONDE-POP_LATINO"),
            MusicSubType(code=724, label="Portuguese fado ", slug="MUSIQUE_DU_MONDE-PORTUGUESE_FADO"),
            MusicSubType(code=725, label="Rai", slug="MUSIQUE_DU_MONDE-RAI"),
            MusicSubType(code=726, label="Salsa", slug="MUSIQUE_DU_MONDE-SALSA"),
            MusicSubType(code=727, label="Tango Argentin", slug="MUSIQUE_DU_MONDE-TANGO_ARGENTIN"),
            MusicSubType(code=728, label="Yiddish", slug="MUSIQUE_DU_MONDE-YIDDISH"),
            MusicSubType(code=-1, label="Autre", slug="MUSIQUE_DU_MONDE-OTHER"),
        ],
    ),
    MusicType(
        code=800,
        label="Pop",
        children=[
            MusicSubType(code=801, label="Britpop", slug="POP-BRITPOP"),
            MusicSubType(code=802, label="Bubblegum ", slug="POP-BUBBLEGUM"),
            MusicSubType(code=803, label="Dance Pop", slug="POP-DANCE_POP"),
            MusicSubType(code=804, label="Dream Pop ", slug="POP-DREAM_POP"),
            MusicSubType(code=805, label="Electro Pop", slug="POP-ELECTRO_POP"),
            MusicSubType(code=806, label="Indie Pop", slug="POP-INDIE_POP"),
            MusicSubType(code=808, label="J-Pop", slug="POP-J_POP"),
            MusicSubType(code=809, label="K-Pop", slug="POP-K_POP"),
            MusicSubType(code=810, label="Pop Punk ", slug="POP-POP_PUNK"),
            MusicSubType(code=811, label="Pop/Rock", slug="POP-POP_ROCK"),
            MusicSubType(code=812, label="Power Pop ", slug="POP-POWER_POP"),
            MusicSubType(code=813, label="Soft Rock", slug="POP-SOFT_ROCK"),
            MusicSubType(code=814, label="Synthpop ", slug="POP-SYNTHPOP"),
            MusicSubType(code=815, label="Teen Pop", slug="POP-TEEN_POP"),
            MusicSubType(code=-1, label="Autre", slug="POP-OTHER"),
        ],
    ),
    MusicType(
        code=820,
        label="Rock",
        children=[
            MusicSubType(code=821, label="Acid Rock ", slug="ROCK-ACID_ROCK"),
            MusicSubType(code=822, label="Arena Rock", slug="ROCK-ARENA_ROCK"),
            MusicSubType(code=823, label="Art Rock", slug="ROCK-ART_ROCK"),
            MusicSubType(code=824, label="College Rock", slug="ROCK-COLLEGE_ROCK"),
            MusicSubType(code=825, label="Glam Rock", slug="ROCK-GLAM_ROCK"),
            MusicSubType(code=826, label="Grunge", slug="ROCK-GRUNGE"),
            MusicSubType(code=827, label="Hard Rock", slug="ROCK-HARD_ROCK"),
            MusicSubType(code=828, label="Indie Rock", slug="ROCK-INDIE_ROCK"),
            MusicSubType(code=829, label="Lo-fi", slug="ROCK-LO_FI"),
            MusicSubType(code=830, label="Prog-Rock", slug="ROCK-PROG_ROCK"),
            MusicSubType(code=831, label="Psychedelic", slug="ROCK-PSYCHEDELIC"),
            MusicSubType(code=832, label="Rock & Roll", slug="ROCK-ROCK_N_ROLL"),
            MusicSubType(code=833, label="Rock Experimental", slug="ROCK-EXPERIMENTAL"),
            MusicSubType(code=834, label="Rockabilly", slug="ROCK-ROCKABILLY"),
            MusicSubType(code=835, label="Shoegaze", slug="ROCK-SHOEGAZE"),
            MusicSubType(code=836, label="Rock Electro", slug="ROCK-ELECTRO"),
            MusicSubType(code=-1, label="Autre", slug="ROCK-OTHER"),
        ],
    ),
    MusicType(
        code=840,
        label="Metal",
        children=[
            MusicSubType(code=841, label="Black Metal", slug="METAL-BLACK_METAL"),
            MusicSubType(code=842, label="Death Metal ", slug="METAL-DEATH_METAL"),
            MusicSubType(code=843, label="Doom Metal", slug="METAL-DOOM_METAL"),
            MusicSubType(code=844, label="Gothic ", slug="METAL-GOTHIC"),
            MusicSubType(code=845, label="Metal Core", slug="METAL-METAL_CORE"),
            MusicSubType(code=846, label="Metal Progressif", slug="METAL-METAL_PROGRESSIF"),
            MusicSubType(code=847, label="Trash Metal", slug="METAL-TRASH_METAL"),
            MusicSubType(code=848, label="Metal Industriel", slug="METAL-METAL_INDUSTRIEL"),
            MusicSubType(code=849, label="Fusion", slug="METAL-FUSION"),
            MusicSubType(code=-1, label="Autre", slug="METAL-OTHER"),
        ],
    ),
    MusicType(
        code=850,
        label="Punk",
        children=[
            MusicSubType(code=851, label="Post Punk ", slug="PUNK-POST_PUNK"),
            MusicSubType(code=852, label="Hardcore Punk", slug="PUNK-HARDCORE_PUNK"),
            MusicSubType(code=853, label="Afro Punk", slug="PUNK-AFRO_PUNK"),
            MusicSubType(code=854, label="Grindcore", slug="PUNK-GRINDCORE"),
            MusicSubType(code=855, label="Noise Rock ", slug="PUNK-NOISE_ROCK"),
            MusicSubType(code=-1, label="Autre", slug="PUNK-OTHER"),
        ],
    ),
    MusicType(
        code=860,
        label="Folk",
        children=[
            MusicSubType(code=861, label="Folk Contemporaine", slug="FOLK-FOLK_CONTEMPORAINE"),
            MusicSubType(code=862, label="Indie Folk", slug="FOLK-INDIE_FOLK"),
            MusicSubType(code=863, label="Folk Rock", slug="FOLK-FOLK_ROCK"),
            MusicSubType(code=864, label="New Acoustic", slug="FOLK-NEW_ACOUSTIC"),
            MusicSubType(code=865, label="Folk Traditionelle", slug="FOLK-FOLK_TRADITIONELLE"),
            MusicSubType(code=866, label="Tex-Mex", slug="FOLK-TEX_MEX"),
            MusicSubType(code=-1, label="Autre", slug="FOLK-OTHER"),
        ],
    ),
    MusicType(
        code=870,
        label="Country",
        children=[
            MusicSubType(code=871, label="Country Alternative", slug="COUNTRY-COUNTRY_ALTERNATIVE"),
            MusicSubType(code=872, label="Americana", slug="COUNTRY-AMERICANA"),
            MusicSubType(code=873, label="Bluegrass", slug="COUNTRY-BLUEGRASS"),
            MusicSubType(code=874, label="Country Contemporaine", slug="COUNTRY-COUNTRY_CONTEMPORAINE"),
            MusicSubType(code=875, label="Gospel Country", slug="COUNTRY-GOSPEL_COUNTRY"),
            MusicSubType(code=876, label="Country Pop", slug="COUNTRY-COUNTRY_POP"),
            MusicSubType(code=-1, label="Autre", slug="COUNTRY-OTHER"),
        ],
    ),
    MusicType(
        code=880,
        label="Electro",
        children=[
            MusicSubType(code=881, label="Bitpop", slug="ELECTRO-BITPOP"),
            MusicSubType(code=882, label="Breakbeat ", slug="ELECTRO-BREAKBEAT"),
            MusicSubType(code=883, label="Chillwave", slug="ELECTRO-CHILLWAVE"),
            MusicSubType(code=884, label="Dance", slug="ELECTRO-DANCE"),
            MusicSubType(code=885, label="Downtempo", slug="ELECTRO-DOWNTEMPO"),
            MusicSubType(code=886, label="Drum & Bass ", slug="ELECTRO-DRUM_AND_BASS"),
            MusicSubType(code=887, label="Dubstep", slug="ELECTRO-DUBSTEP"),
            MusicSubType(code=888, label="Electro Experimental", slug="ELECTRO-EXPERIMENTAL"),
            MusicSubType(code=889, label="Electronica", slug="ELECTRO-ELECTRONICA"),
            MusicSubType(code=890, label="Garage", slug="ELECTRO-GARAGE"),
            MusicSubType(code=891, label="Grime", slug="ELECTRO-GRIME"),
            MusicSubType(code=892, label="Hard Dance", slug="ELECTRO-HARD_DANCE"),
            MusicSubType(code=893, label="Hardcore", slug="ELECTRO-HARDCORE"),
            MusicSubType(code=894, label="House", slug="ELECTRO-HOUSE"),
            MusicSubType(code=895, label="Industriel", slug="ELECTRO-INDUSTRIEL"),
            MusicSubType(code=896, label="Lounge", slug="ELECTRO-LOUNGE"),
            MusicSubType(code=897, label="Techno", slug="ELECTRO-TECHNO"),
            MusicSubType(code=898, label="Trance", slug="ELECTRO-TRANCE"),
            MusicSubType(code=-1, label="Autre", slug="ELECTRO-OTHER"),
        ],
    ),
    MusicType(
        code=900,
        label="Hip-Hop/Rap",
        children=[
            MusicSubType(code=901, label="Bounce", slug="HIP_HOP_RAP-BOUNCE"),
            MusicSubType(code=902, label="Hip Hop", slug="HIP_HOP_RAP-HIP_HOP"),
            MusicSubType(code=903, label="Rap Alternatif", slug="HIP_HOP_RAP-RAP_ALTERNATIF"),
            MusicSubType(code=905, label="Rap East Coast", slug="HIP_HOP_RAP-RAP_EAST_COAST"),
            MusicSubType(code=906, label="Rap Français", slug="HIP_HOP_RAP-RAP_FRANCAIS"),
            MusicSubType(code=907, label="Rap Gangsta", slug="HIP_HOP_RAP-RAP_GANGSTA"),
            MusicSubType(code=908, label="Rap Hardcore", slug="HIP_HOP_RAP-RAP_HARDCORE"),
            MusicSubType(code=909, label="Rap Latino", slug="HIP_HOP_RAP-RAP_LATINO"),
            MusicSubType(code=910, label="Rap Old School", slug="HIP_HOP_RAP-RAP_OLD_SCHOOL"),
            MusicSubType(code=911, label="Rap Underground", slug="HIP_HOP_RAP-RAP_UNDERGROUND"),
            MusicSubType(code=912, label="Rap West Coast", slug="HIP_HOP_RAP-RAP_WEST_COAST"),
            MusicSubType(code=913, label="Trap", slug="HIP_HOP_RAP-TRAP"),
            MusicSubType(code=914, label="Trip Hop", slug="HIP_HOP_RAP-TRIP_HOP"),
            MusicSubType(code=921, label="R&B Contemporain", slug="HIP_HOP_RAP-R&B_CONTEMPORAIN"),
            MusicSubType(code=922, label="Disco", slug="HIP_HOP_RAP-DISCO"),
            MusicSubType(code=923, label="Doo Wop", slug="HIP_HOP_RAP-DOO_WOP"),
            MusicSubType(code=924, label="Funk", slug="HIP_HOP_RAP-FUNK"),
            MusicSubType(code=925, label="Soul", slug="HIP_HOP_RAP-SOUL"),
            MusicSubType(code=926, label="Motown", slug="HIP_HOP_RAP-MOTOWN"),
            MusicSubType(code=927, label="Neo Soul", slug="HIP_HOP_RAP-NEO_SOUL"),
            MusicSubType(code=928, label="Soul Psychedelique", slug="HIP_HOP_RAP-SOUL_PSYCHEDELIQUE"),
            MusicSubType(code=-1, label="Autre", slug="HIP_HOP_RAP-OTHER"),
        ],
    ),
    MusicType(
        code=930,
        label="Gospel",
        children=[
            MusicSubType(code=931, label="Spiritual Gospel", slug="GOSPEL-SPIRITUAL_GOSPEL"),
            MusicSubType(code=932, label="Traditional Gospel", slug="GOSPEL-TRADITIONAL_GOSPEL"),
            MusicSubType(code=933, label="Southern Gospel", slug="GOSPEL-SOUTHERN_GOSPEL"),
            MusicSubType(code=934, label="Contemporary Gospel", slug="GOSPEL-CONTEMPORARY_GOSPEL"),
            MusicSubType(code=935, label="Bluegrass Gospel", slug="GOSPEL-BLUEGRASS_GOSPEL"),
            MusicSubType(code=936, label="Blues Gospel", slug="GOSPEL-BLUES_GOSPEL"),
            MusicSubType(code=937, label="Country Gospel", slug="GOSPEL-COUNTRY_GOSPEL"),
            MusicSubType(code=938, label="Hybrid Gospel", slug="GOSPEL-HYBRID_GOSPEL"),
            MusicSubType(code=-1, label="Autre", slug="GOSPEL-OTHER"),
        ],
    ),
    MusicType(
        code=1000,
        label="Chansons / Variétés",
        children=[
            MusicSubType(code=1001, label="Musette", slug="CHANSON_VARIETE-MUSETTE"),
            MusicSubType(code=1002, label="Chanson Française", slug="CHANSON_VARIETE-CHANSON_FRANCAISE"),
            MusicSubType(code=1003, label="Music Hall", slug="CHANSON_VARIETE-MUSIC_HALL"),
            MusicSubType(code=1004, label="Folklore français", slug="CHANSON_VARIETE-FOLKLORE_FRANCAIS"),
            MusicSubType(code=1005, label="Chanson à texte", slug="CHANSON_VARIETE-CHANSON_À_TEXTE"),
            MusicSubType(code=1006, label="Slam", slug="CHANSON_VARIETE-SLAM"),
            MusicSubType(code=-1, label="Autre", slug="CHANSON_VARIETE-OTHER"),
        ],
    ),
    MusicType(
        code=-1,
        label="Autre",
        children=[MusicSubType(code=-1, label="Autre", slug=OTHER_SHOW_TYPE_SLUG)],
    ),
]

MUSIC_TYPES_BY_CODE = {music_type.code: music_type for music_type in music_types}
MUSIC_TYPES_LABEL_BY_CODE = {music_type.code: music_type.label for music_type in music_types}
MUSIC_TYPES_BY_SLUG = {
    music_sub_type.slug: music_type for music_type in music_types for music_sub_type in music_type.children
}

MUSIC_SUB_TYPES_LABEL_BY_CODE = {
    music_sub_type.code: music_sub_type.label for music_type in music_types for music_sub_type in music_type.children
}
MUSIC_SUB_TYPES_BY_CODE = {
    music_sub_type.code: music_sub_type for music_type in music_types for music_sub_type in music_type.children
}  # WARNING: for code -1, the sub type is not unique, it returns the one with the slug CHANSON_VARIETE-OTHER
MUSIC_SUB_TYPES_BY_SLUG = {
    music_sub_type.slug: music_sub_type for music_type in music_types for music_sub_type in music_type.children
}
