from dataclasses import dataclass


@dataclass
class ShowSubType:
    code: int
    label: str
    slug: str


@dataclass
class ShowType:
    children: list[ShowSubType]
    code: int
    label: str


OTHER_SHOW_TYPE_SLUG = "OTHER"

# WARNING: the list below MUST be kept in sync with the list at pro/src/core/Offers/categoriesSubTypes.ts
SHOW_TYPES = [
    ShowType(
        code=100,
        label="Arts de la rue",
        children=[
            ShowSubType(code=101, label="Carnaval", slug="ART_DE_LA_RUE-CARNAVAL"),
            ShowSubType(code=102, label="Fanfare", slug="ART_DE_LA_RUE-FANFARE"),
            ShowSubType(code=103, label="Mime", slug="ART_DE_LA_RUE-MIME"),
            ShowSubType(code=104, label="Parade", slug="ART_DE_LA_RUE-PARADE"),
            ShowSubType(code=105, label="Théâtre de Rue", slug="ART_DE_LA_RUE-THEATRE_DE_RUE"),
            ShowSubType(code=106, label="Théâtre Promenade", slug="ART_DE_LA_RUE-THEATRE_PROMENADE"),
            ShowSubType(code=-1, label="Autre", slug="ART_DE_LA_RUE-OTHER"),
        ],
    ),
    ShowType(
        code=200,
        label="Cirque",
        children=[
            ShowSubType(code=201, label="Cirque Contemporain", slug="CIRQUE-CIRQUE_CONTEMPORAIN"),
            ShowSubType(code=202, label="Cirque Hors les murs", slug="CIRQUE-CIRQUE_HORS_LES_MURS"),
            ShowSubType(code=203, label="Cirque Traditionel", slug="CIRQUE-CIRQUE_TRADITIONNEL"),
            ShowSubType(code=204, label="Cirque Voyageur", slug="CIRQUE-CIRQUE_VOYAGEUR"),
            ShowSubType(code=205, label="Clown", slug="CIRQUE-CLOWN"),
            ShowSubType(code=206, label="Hypnose", slug="CIRQUE-HYPNOSE"),
            ShowSubType(code=207, label="Mentaliste", slug="CIRQUE-MENTALISTE"),
            ShowSubType(code=208, label="Spectacle de Magie", slug="CIRQUE-SPECTACLE_DE_MAGIE"),
            ShowSubType(code=209, label="Spectacle Équestre", slug="CIRQUE-SPECTACLE_EQUESTRE"),
            ShowSubType(code=-1, label="Autre", slug="CIRQUE-OTHER"),
        ],
    ),
    ShowType(
        code=300,
        label="Danse",
        children=[
            ShowSubType(code=302, label="Ballet", slug="DANSE-BALLET"),
            ShowSubType(code=303, label="Cancan", slug="DANSE-CANCAN"),
            ShowSubType(code=304, label="Claquette", slug="DANSE-CLAQUETTE"),
            ShowSubType(code=305, label="Classique", slug="DANSE-CLASSIQUE"),
            ShowSubType(code=306, label="Contemporaine", slug="DANSE-CONTEMPORAINE"),
            ShowSubType(code=307, label="Danse du Monde", slug="DANSE-DANSE_DU_MONDE"),
            ShowSubType(code=308, label="Flamenco", slug="DANSE-FLAMENCO"),
            ShowSubType(code=309, label="Moderne Jazz", slug="DANSE-MODERNE_JAZZ"),
            ShowSubType(code=311, label="Salsa", slug="DANSE-SALSA"),
            ShowSubType(code=312, label="Swing", slug="DANSE-SWING"),
            ShowSubType(code=313, label="Tango", slug="DANSE-TANGO"),
            ShowSubType(code=314, label="Urbaine", slug="DANSE-URBAINE"),
            ShowSubType(code=-1, label="Autre", slug="DANSE-OTHER"),
        ],
    ),
    ShowType(
        code=400,
        label="Humour / Café-théâtre",
        children=[
            ShowSubType(code=401, label="Café Théâtre", slug="HUMOUR-CAFE_THEATRE"),
            ShowSubType(code=402, label="Improvisation", slug="HUMOUR-IMPROVISATION"),
            ShowSubType(code=403, label="Seul.e en scène", slug="HUMOUR-SEUL_EN_SCENE"),
            ShowSubType(code=404, label="Sketch", slug="HUMOUR-SKETCH"),
            ShowSubType(code=405, label="Stand Up", slug="HUMOUR-STAND_UP"),
            ShowSubType(code=406, label="Ventriloque", slug="HUMOUR-VENTRILOQUE"),
            ShowSubType(code=-1, label="Autre", slug="HUMOUR-OTHER"),
        ],
    ),
    ShowType(
        code=1100,
        label="Spectacle Musical / Cabaret / Opérette",
        children=[
            ShowSubType(code=1101, label="Cabaret", slug="SPECTACLE_MUSICAL-CABARET"),
            ShowSubType(code=1102, label="Café Concert", slug="SPECTACLE_MUSICAL-CAFE_CONCERT"),
            ShowSubType(code=1103, label="Claquette", slug="SPECTACLE_MUSICAL-CLAQUETTE"),
            ShowSubType(code=1104, label="Comédie Musicale", slug="SPECTACLE_MUSICAL-COMEDIE_MUSICALE"),
            ShowSubType(code=1105, label="Opéra Bouffe", slug="SPECTACLE_MUSICAL-OPERA_BOUFFE"),
            ShowSubType(code=1108, label="Opérette", slug="SPECTACLE_MUSICAL-OPERETTE"),
            ShowSubType(code=1109, label="Revue", slug="SPECTACLE_MUSICAL-REVUE"),
            ShowSubType(code=1111, label="Burlesque", slug="SPECTACLE_MUSICAL-BURLESQUE"),
            ShowSubType(code=1112, label="Comédie-Ballet", slug="SPECTACLE_MUSICAL-COMEDIE_BALLET"),
            ShowSubType(code=1113, label="Opéra Comique", slug="SPECTACLE_MUSICAL-OPERA_COMIQUE"),
            ShowSubType(code=1114, label="Opéra-Ballet", slug="SPECTACLE_MUSICAL-OPERA_BALLET"),
            ShowSubType(code=1115, label="Théâtre musical", slug="SPECTACLE_MUSICAL-THEATRE_MUSICAL"),
            ShowSubType(code=-1, label="Autre", slug="SPECTACLE_MUSICAL-OTHER"),
        ],
    ),
    ShowType(
        code=1200,
        label="Spectacle Jeunesse",
        children=[
            ShowSubType(code=1201, label="Conte", slug="SPECTACLE_JEUNESSE-CONTE"),
            ShowSubType(code=1202, label="Théâtre jeunesse", slug="SPECTACLE_JEUNESSE-THEATRE_JEUNESSE"),
            ShowSubType(
                code=1203, label="Spectacle Petite Enfance", slug="SPECTACLE_JEUNESSE-SPECTACLE_PETITE_ENFANCE"
            ),
            ShowSubType(code=1204, label="Magie Enfance", slug="SPECTACLE_JEUNESSE-MAGIE_ENFANCE"),
            ShowSubType(code=1205, label="Spectacle pédagogique", slug="SPECTACLE_JEUNESSE-SPECTACLE_PEDAGOGIQUE"),
            ShowSubType(code=1206, label="Marionettes", slug="SPECTACLE_JEUNESSE-MARIONETTES"),
            ShowSubType(
                code=1207, label="Comédie musicale jeunesse", slug="SPECTACLE_JEUNESSE-COMEDIE_MUSICALE_JEUNESSE"
            ),
            ShowSubType(code=1208, label="Théâtre d'Ombres", slug="SPECTACLE_JEUNESSE-THEATRE_D_OMBRES"),
            ShowSubType(code=-1, label="Autre", slug="SPECTACLE_JEUNESSE-OTHER"),
        ],
    ),
    ShowType(
        code=1300,
        label="Théâtre",
        children=[
            ShowSubType(code=1301, label="Boulevard", slug="THEATRE-BOULEVARD"),
            ShowSubType(code=1302, label="Classique", slug="THEATRE-CLASSIQUE"),
            ShowSubType(code=1303, label="Comédie", slug="THEATRE-COMEDIE"),
            ShowSubType(code=1304, label="Contemporain", slug="THEATRE-CONTEMPORAIN"),
            ShowSubType(code=1305, label="Lecture", slug="THEATRE-LECTURE"),
            ShowSubType(code=1306, label="Spectacle Scénographique", slug="THEATRE-SPECTACLE_SCENOGRAPHIQUE"),
            ShowSubType(code=1307, label="Théâtre Experimental", slug="THEATRE-THEATRE_EXPERIMENTAL"),
            ShowSubType(code=1308, label="Théâtre d'Objet", slug="THEATRE-THEATRE_D_OBJET"),
            ShowSubType(code=1309, label="Tragédie", slug="THEATRE-TRAGEDIE"),
            ShowSubType(code=-1, label="Autre", slug="THEATRE-OTHER"),
        ],
    ),
    ShowType(
        code=1400,
        label="Pluridisciplinaire",
        children=[
            ShowSubType(code=1401, label="Performance", slug="PLURIDISCIPLINAIRE-PERFORMANCE"),
            ShowSubType(code=1402, label="Poésie", slug="PLURIDISCIPLINAIRE-POESIE"),
            ShowSubType(code=-1, label="Autre", slug="PLURIDISCIPLINAIRE-OTHER"),
        ],
    ),
    ShowType(
        code=1500,
        label="Autre (spectacle sur glace, historique, aquatique, …)  ",
        children=[
            ShowSubType(code=1501, label="Son et lumière", slug="OTHER-SON_ET_LUMIERE"),
            ShowSubType(code=1502, label="Spectacle sur glace", slug="OTHER-SPECTACLE_SUR_GLACE"),
            ShowSubType(code=1503, label="Spectacle historique", slug="OTHER-SPECTACLE_HISTORIQUE"),
            ShowSubType(code=1504, label="Spectacle aquatique", slug="OTHER-SPECTACLE_AQUATIQUE"),
            ShowSubType(code=-1, label="Autre", slug="OTHER-OTHER"),
        ],
    ),
    ShowType(
        code=1510,
        label="Opéra",
        children=[
            ShowSubType(code=1511, label="Opéra série", slug="OPERA-OPERA_SERIE"),
            ShowSubType(code=1512, label="Grand opéra", slug="OPERA-GRAND_OPERA"),
            ShowSubType(code=1513, label="Opéra bouffe", slug="OPERA-OPERA_BOUFFE"),
            ShowSubType(code=1514, label="Opéra comique", slug="OPERA-OPERA_COMIQUE"),
            ShowSubType(code=1515, label="Opéra-ballet", slug="OPERA-OPERA_BALLET"),
            ShowSubType(code=1516, label="Singspiel", slug="OPERA-SINGSPIEL"),
            ShowSubType(code=-1, label="Autre", slug="OPERA-OTHER"),
        ],
    ),
    ShowType(
        code=-1,
        label="Autre",
        children=[
            ShowSubType(code=-1, label="Autre", slug=OTHER_SHOW_TYPE_SLUG),
        ],
    ),
]

SHOW_TYPES_BY_CODE = {show_type.code: show_type for show_type in SHOW_TYPES}
SHOW_TYPES_LABEL_BY_CODE = {show_type.code: show_type.label for show_type in SHOW_TYPES}
SHOW_TYPES_BY_SLUG = {show_sub_type.slug: show_type for show_type in SHOW_TYPES for show_sub_type in show_type.children}

SHOW_SUB_TYPES_LABEL_BY_CODE = {
    show_sub_type.code: show_sub_type.label for show_type in SHOW_TYPES for show_sub_type in show_type.children
}
SHOW_SUB_TYPES_BY_CODE = {
    show_sub_type.code: show_sub_type for show_type in SHOW_TYPES for show_sub_type in show_type.children
}  # WARNING: for code -1, the sub type is not unique, it returns the one with the one with the slug OPERA-OTHER
SHOW_SUB_TYPES_BY_SLUG = {
    show_sub_type.slug: show_sub_type for show_type in SHOW_TYPES for show_sub_type in show_type.children
}
