from dataclasses import dataclass


@dataclass
class ShowSubType:
    code: int
    label: str


@dataclass
class ShowType(ShowSubType):
    children: list[ShowSubType]


# WARNING: the list below MUST be kept in sync with the list at pro/src/components/pages/Offers/Offer/OfferDetails/OfferForm/OfferCategories/subTypes.js
show_types = [
    ShowType(
        code=100,
        label="Arts de la rue",
        children=[
            ShowSubType(code=101, label="Carnaval"),
            ShowSubType(code=102, label="Fanfare"),
            ShowSubType(code=103, label="Mime"),
            ShowSubType(code=104, label="Parade"),
            ShowSubType(code=105, label="Théâtre de Rue"),
            ShowSubType(code=106, label="Théâtre Promenade"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=200,
        label="Cirque",
        children=[
            ShowSubType(code=201, label="Cirque Contemporain"),
            ShowSubType(code=202, label="Cirque Hors les murs"),
            ShowSubType(code=203, label="Cirque Traditionel"),
            ShowSubType(code=204, label="Cirque Voyageur"),
            ShowSubType(code=205, label="Clown"),
            ShowSubType(code=206, label="Hypnose"),
            ShowSubType(code=207, label="Mentaliste"),
            ShowSubType(code=208, label="Spectacle de Magie"),
            ShowSubType(code=209, label="Spectacle Équestre"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=300,
        label="Danse",
        children=[
            ShowSubType(code=302, label="Ballet"),
            ShowSubType(code=303, label="Cancan"),
            ShowSubType(code=304, label="Claquette"),
            ShowSubType(code=305, label="Classique"),
            ShowSubType(code=306, label="Contemporaine"),
            ShowSubType(code=307, label="Danse du Monde"),
            ShowSubType(code=308, label="Flamenco"),
            ShowSubType(code=309, label="Moderne Jazz"),
            ShowSubType(code=311, label="Salsa"),
            ShowSubType(code=312, label="Swing"),
            ShowSubType(code=313, label="Tango"),
            ShowSubType(code=314, label="Urbaine"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=400,
        label="Humour / Café-théâtre",
        children=[
            ShowSubType(code=401, label="Café Théâtre"),
            ShowSubType(code=402, label="Improvisation"),
            ShowSubType(code=403, label="Seul.e en scène"),
            ShowSubType(code=404, label="Sketch"),
            ShowSubType(code=405, label="Stand Up"),
            ShowSubType(code=406, label="Ventriloque"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=1100,
        label="Spectacle Musical / Cabaret / Opérette",
        children=[
            ShowSubType(code=1101, label="Cabaret"),
            ShowSubType(code=1102, label="Café Concert"),
            ShowSubType(code=1103, label="Claquette"),
            ShowSubType(code=1104, label="Comédie Musicale"),
            ShowSubType(code=1105, label="Opéra Bouffe"),
            ShowSubType(code=1108, label="Opérette"),
            ShowSubType(code=1109, label="Revue"),
            ShowSubType(code=1111, label="Burlesque"),
            ShowSubType(code=1112, label="Comédie-Ballet"),
            ShowSubType(code=1113, label="Opéra Comique"),
            ShowSubType(code=1114, label="Opéra-Ballet"),
            ShowSubType(code=1115, label="Théâtre musical"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=1200,
        label="Spectacle Jeunesse",
        children=[
            ShowSubType(code=1201, label="Conte"),
            ShowSubType(code=1202, label="Théâtre jeunesse"),
            ShowSubType(code=1203, label="Spectacle Petite Enfance"),
            ShowSubType(code=1204, label="Magie Enfance"),
            ShowSubType(code=1205, label="Spectacle pédagogique"),
            ShowSubType(code=1206, label="Marionettes"),
            ShowSubType(code=1207, label="Comédie musicale jeunesse"),
            ShowSubType(code=1208, label="Théâtre d'Ombres"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=1300,
        label="Théâtre",
        children=[
            ShowSubType(code=1301, label="Boulevard"),
            ShowSubType(code=1302, label="Classique"),
            ShowSubType(code=1303, label="Comédie"),
            ShowSubType(code=1304, label="Contemporain"),
            ShowSubType(code=1305, label="Lecture"),
            ShowSubType(code=1306, label="Spectacle Scénographique"),
            ShowSubType(code=1307, label="Théâtre Experimental"),
            ShowSubType(code=1308, label="Théâtre d'Objet"),
            ShowSubType(code=1309, label="Tragédie"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=1400,
        label="Pluridisciplinaire",
        children=[
            ShowSubType(code=1401, label="Performance"),
            ShowSubType(code=1402, label="Poésie"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=1500,
        label="Autre (spectacle sur glace, historique, aquatique, …)  ",
        children=[
            ShowSubType(code=1501, label="Son et lumière"),
            ShowSubType(code=1502, label="Spectacle sur glace"),
            ShowSubType(code=1503, label="Spectacle historique"),
            ShowSubType(code=1504, label="Spectacle aquatique"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=1510,
        label="Opéra",
        children=[
            ShowSubType(code=1511, label="Opéra série"),
            ShowSubType(code=1512, label="Grand opéra"),
            ShowSubType(code=1513, label="Opéra bouffe"),
            ShowSubType(code=1514, label="Opéra comique"),
            ShowSubType(code=1515, label="Opéra-ballet"),
            ShowSubType(code=1516, label="Singspiel"),
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
    ShowType(
        code=-1,
        label="Autre",
        children=[
            ShowSubType(code=-1, label="Autre"),
        ],
    ),
]

SHOW_TYPES_DICT = {vars(show_type)["code"]: vars(show_type)["label"] for show_type in show_types}

SHOW_SUB_TYPES_DICT = {
    vars(show_sub_type)["code"]: vars(show_sub_type)["label"]
    for show_type in show_types
    for show_sub_type in show_type.children
}
