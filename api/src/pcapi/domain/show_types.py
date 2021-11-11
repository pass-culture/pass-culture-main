show_types = [
    {
        "code": 100,
        "label": "Arts de la rue",
        "children": [
            {"code": 101, "label": "Carnaval"},
            {"code": 102, "label": "Fanfare"},
            {"code": 103, "label": "Mime"},
            {"code": 104, "label": "Parade"},
            {"code": 105, "label": "Théâtre de Rue"},
            {"code": 106, "label": "Théâtre Promenade"},
        ],
    },
    {
        "code": 200,
        "label": "Cirque",
        "children": [
            {"code": 201, "label": "Cirque Contemporain"},
            {"code": 202, "label": "Cirque Hors les murs"},
            {"code": 203, "label": "Cirque Traditionel"},
            {"code": 204, "label": "Cirque Voyageur"},
            {"code": 205, "label": "Clown"},
            {"code": 206, "label": "Hypnose"},
            {"code": 207, "label": "Mentaliste"},
            {"code": 208, "label": "Spectacle de Magie"},
            {"code": 209, "label": "Spectacle Équestre"},
        ],
    },
    {
        "code": 300,
        "label": "Danse",
        "children": [
            {"code": 302, "label": "Ballet"},
            {"code": 303, "label": "Cancan"},
            {"code": 304, "label": "Claquette"},
            {"code": 305, "label": "Classique"},
            {"code": 306, "label": "Contemporaine"},
            {"code": 307, "label": "Danse du Monde"},
            {"code": 308, "label": "Flamenco"},
            {"code": 309, "label": "Moderne Jazz"},
            {"code": 311, "label": "Salsa"},
            {"code": 312, "label": "Swing"},
            {"code": 313, "label": "Tango"},
            {"code": 314, "label": "Urbaine"},
        ],
    },
    {
        "code": 400,
        "label": "Humour / Café-théâtre",
        "children": [
            {"code": 401, "label": "Café Théâtre"},
            {"code": 402, "label": "Improvisation"},
            {"code": 403, "label": "Seul.e en scène"},
            {"code": 404, "label": "Sketch"},
            {"code": 405, "label": "Stand Up"},
            {"code": 406, "label": "Ventriloque"},
        ],
    },
    {
        "code": 1100,
        "label": "Spectacle Musical / Cabaret / Opérette",
        "children": [
            {"code": 1101, "label": "Cabaret"},
            {"code": 1102, "label": "Café Concert"},
            {"code": 1103, "label": "Claquette"},
            {"code": 1104, "label": "Comédie Musicale"},
            {"code": 1105, "label": "Opéra Bouffe"},
            {"code": 1108, "label": "Opérette"},
            {"code": 1109, "label": "Revue"},
            {"code": 1111, "label": "Burlesque"},
            {"code": 1112, "label": "Comédie-Ballet"},
            {"code": 1113, "label": "Opéra Comique"},
            {"code": 1114, "label": "Opéra-Ballet"},
            {"code": 1115, "label": "Théâtre musical"},
        ],
    },
    {
        "code": 1200,
        "label": "Spectacle Jeunesse",
        "children": [
            {"code": 1201, "label": "Conte"},
            {"code": 1202, "label": "Théâtre jeunesse"},
            {"code": 1203, "label": "Spectacle Petite Enfance"},
            {"code": 1204, "label": "Magie Enfance"},
            {"code": 1205, "label": "Spectacle pédagogique"},
            {"code": 1206, "label": "Marionettes"},
            {"code": 1207, "label": "Comédie musicale jeunesse"},
            {"code": 1208, "label": "Théâtre d'Ombres"},
        ],
    },
    {
        "code": 1300,
        "label": "Théâtre",
        "children": [
            {"code": 1301, "label": "Boulevard"},
            {"code": 1302, "label": "Classique"},
            {"code": 1303, "label": "Comédie"},
            {"code": 1304, "label": "Contemporain"},
            {"code": 1305, "label": "Lecture"},
            {"code": 1306, "label": "Spectacle Scénographique"},
            {"code": 1307, "label": "Théâtre Experimental"},
            {"code": 1308, "label": "Théâtre d'Objet"},
            {"code": 1309, "label": "Tragédie"},
        ],
    },
    {
        "code": 1400,
        "label": "Pluridisciplinaire",
        "children": [
            {"code": 1401, "label": "Performance"},
            {"code": 1402, "label": "Poésie"},
        ],
    },
    {
        "code": 1500,
        "label": "Autre (spectacle sur glace, historique, aquatique, …)  ",
        "children": [
            {"code": 1501, "label": "Son et lumière"},
            {"code": 1502, "label": "Spectacle sur glace"},
            {"code": 1503, "label": "Spectacle historique"},
            {"code": 1504, "label": "Spectacle aquatique"},
        ],
    },
]

SHOW_TYPES_DICT = {show_type["code"]: show_type["label"] for show_type in show_types}

SHOW_SUB_TYPES_DICT = {
    show_sub_type["code"]: show_sub_type["label"] for show_type in show_types for show_sub_type in show_type["children"]
}
