from dataclasses import dataclass


BOOK_MACRO_SECTIONS = {
    "Géographie, cartographie",
    "Poésie, théâtre et spectacle",
    "Bandes dessinées",
    "Carrière/Concours",
    "Sport",
    "Policier",
    "Histoire",
    "Science-fiction, fantastique & terreur",
    "Littérature étrangère",
    "Sociologie",
    "Gestion/entreprise",
    "Littérature française",
    "Littérature Européenne",
    "Scolaire & Parascolaire",
    "Sciences Humaines, Encyclopédie, dictionnaire",
    "Langue",
    "Religions, spiritualités",
    "Vie pratique",
    "Art",
    "Santé",
    "Sciences, vie & Nature",
    "Informatique",
    "Jeunesse",
    "Sexualité",
    "Psychanalyse, psychologie",
    "Humour",
    "Manga",
    "Arts Culinaires",
    "Tourisme",
    "Jeux",
    "Droit",
    "Marketing et audio-visuel",
    "Faits, témoignages",
    "Économie",
    "Loisirs",
}


@dataclass
class GTL:
    code: str
    label: str
    level: int


@dataclass
class BookSubType:
    label: str
    gtls: list[GTL]
    position: int


@dataclass
class BookType:
    children: list[BookSubType]
    gtls: list[GTL]
    label: str
    position: int


BOOK_TYPES = [
    BookType(
        position=1,
        label="Romans & littérature",
        gtls=[
            GTL(code="01010000", label="Romans & Nouvelles", level=2),
            GTL(code="01020000", label="Romans & Nouvelles de genre", level=2),
            GTL(code="01030000", label="Œuvres classiques", level=2),
            GTL(code="02000000", label="Jeunesse", level=1),
            GTL(code="01060000", label="Biographie / Témoignage littéraire", level=2),
            GTL(code="01040000", label="Contes / Légendes", level=2),
            GTL(code="92000000", label="Romance", level=1),
            GTL(code="91000000", label="Fantasy & Science-fiction", level=1),
            GTL(code="90000000", label="Policier & Thriller", level=1),
        ],
        children=[
            BookSubType(
                position=1,
                label="Romance",
                gtls=[
                    GTL(code="01020600", label="Roman sentimental", level=3),
                    GTL(code="92000000", label="Romance", level=1),
                ],
            ),
            BookSubType(
                position=2,
                label="Thriller",
                gtls=[
                    GTL(code="01020500", label="Thriller", level=3),
                    GTL(code="90020000", label="Thriller", level=2),
                ],
            ),
            BookSubType(
                position=3,
                label="Fantasy",
                gtls=[
                    GTL(code="01020900", label="Fantasy", level=3),
                    GTL(code="91030000", label="Fantasy", level=2),
                ],
            ),
            BookSubType(
                position=4,
                label="Policier",
                gtls=[
                    GTL(code="01020400", label="Policier", level=3),
                    GTL(code="90010000", label="Policier", level=2),
                ],
            ),
            BookSubType(
                position=5, label="Œuvres classiques", gtls=[GTL(code="01030000", label="Œuvres classiques", level=2)]
            ),
            BookSubType(
                position=6,
                label="Science-fiction",
                gtls=[
                    GTL(code="01020700", label="Science-fiction", level=3),
                    GTL(code="91010000", label="Science-fiction", level=2),
                ],
            ),
            BookSubType(
                position=7,
                label="Horreur",
                gtls=[
                    GTL(code="01020802", label="Horreur / Terreur", level=4),
                    GTL(code="91020200", label="Horreur / Terreur", level=3),
                ],
            ),
            BookSubType(
                position=8,
                label="Aventure",
                gtls=[
                    GTL(code="01020200", label="Aventure", level=3),
                    GTL(code="01020300", label="Espionnage", level=3),
                ],
            ),
            BookSubType(
                position=9,
                label="Biographie",
                gtls=[GTL(code="01060000", label="Biographie / Témoignage littéraire", level=2)],
            ),
            BookSubType(
                position=10, label="Contes & légendes", gtls=[GTL(code="01040000", label="Contes / Légendes", level=2)]
            ),
        ],
    ),
    BookType(
        position=2,
        label="Mangas",
        gtls=[
            GTL(code="03040300", label="Kodomo", level=3),
            GTL(code="03040400", label="Shôjo", level=3),
            GTL(code="03040500", label="Shonen", level=3),
            GTL(code="03040600", label="Seinen", level=3),
            GTL(code="03040700", label="Josei", level=3),
            GTL(code="03040800", label="Yaoi", level=3),
            GTL(code="03040900", label="Yuri", level=3),
        ],
        children=[
            BookSubType(position=1, label="Shonen", gtls=[GTL(code="03040500", label="Shonen", level=3)]),
            BookSubType(position=2, label="Seinen", gtls=[GTL(code="03040600", label="Seinen", level=3)]),
            BookSubType(position=3, label="Shôjo", gtls=[GTL(code="03040400", label="Shôjo", level=3)]),
            BookSubType(position=4, label="Yaoi", gtls=[GTL(code="03040800", label="Yaoi", level=3)]),
            BookSubType(position=5, label="Kodomo", gtls=[GTL(code="03040300", label="Kodomo", level=3)]),
            BookSubType(position=6, label="Josei", gtls=[GTL(code="03040700", label="Josei", level=3)]),
            BookSubType(position=7, label="Yuri", gtls=[GTL(code="03040900", label="Yuri", level=3)]),
        ],
    ),
    BookType(
        position=3,
        label="BD & comics",
        gtls=[GTL(code="03020000", label="Bandes dessinées", level=2), GTL(code="03030000", label="Comics", level=2)],
        children=[
            BookSubType(
                position=1,
                label="Humour",
                gtls=[
                    GTL(code="03020111", label="Humour", level=4),
                    GTL(code="03020211", label="Humour", level=4),
                    GTL(code="03020310", label="Humour", level=4),
                    GTL(code="03030210", label="Humour", level=4),
                    GTL(code="03030310", label="Humour", level=4),
                    GTL(code="03030410", label="Humour", level=4),
                    GTL(code="03030510", label="Humour", level=4),
                    GTL(code="03030610", label="Humour", level=4),
                    GTL(code="03030710", label="Humour", level=4),
                ],
            ),
            BookSubType(
                position=2,
                label="Action & aventure",
                gtls=[
                    GTL(code="03020109", label="Action / Aventures", level=4),
                    GTL(code="03020209", label="Action / Aventures", level=4),
                    GTL(code="03020308", label="Action / Aventures", level=4),
                    GTL(code="03030208", label="Action / Aventures", level=4),
                    GTL(code="03030308", label="Action / Aventures", level=4),
                    GTL(code="03030408", label="Action / Aventures", level=4),
                    GTL(code="03030508", label="Action / Aventures", level=4),
                    GTL(code="03030608", label="Action / Aventures", level=4),
                    GTL(code="03030708", label="Action / Aventures", level=4),
                ],
            ),
            BookSubType(
                position=3,
                label="Fantastique & épouvante",
                gtls=[
                    GTL(code="03020206", label="Fantastique / Epouvante", level=4),
                    GTL(code="03020305", label="Fantastique / Epouvante", level=4),
                    GTL(code="03030205", label="Fantastique / Epouvante", level=4),
                    GTL(code="03030305", label="Fantastique / Epouvante", level=4),
                    GTL(code="03030405", label="Fantastique / Epouvante", level=4),
                    GTL(code="03030505", label="Fantastique / Epouvante", level=4),
                    GTL(code="03030605", label="Fantastique / Epouvante", level=4),
                    GTL(code="03030705", label="Fantastique / Epouvante", level=4),
                ],
            ),
            BookSubType(
                position=4,
                label="Documentaire & société",
                gtls=[
                    GTL(code="03020103", label="Documentaire / Société", level=4),
                    GTL(code="03020203", label="Documentaire / Société", level=4),
                    GTL(code="03020302", label="Documentaire / Société", level=4),
                    GTL(code="03030202", label="Documentaire / Société", level=4),
                    GTL(code="03030302", label="Documentaire / Société", level=4),
                    GTL(code="03030402", label="Documentaire / Société", level=4),
                    GTL(code="03030502", label="Documentaire / Société", level=4),
                    GTL(code="03030602", label="Documentaire / Société", level=4),
                    GTL(code="03030702", label="Documentaire / Société", level=4),
                ],
            ),
            BookSubType(
                position=5,
                label="Fantasy",
                gtls=[
                    GTL(code="03020105", label="Fantasy", level=4),
                    GTL(code="03020205", label="Fantasy", level=4),
                    GTL(code="03020304", label="Fantasy", level=4),
                    GTL(code="03030204", label="Fantasy", level=4),
                    GTL(code="03030304", label="Fantasy", level=4),
                    GTL(code="03030404", label="Fantasy", level=4),
                    GTL(code="03030504", label="Fantasy", level=4),
                    GTL(code="03030604", label="Fantasy", level=4),
                    GTL(code="03030704", label="Fantasy", level=4),
                ],
            ),
            BookSubType(
                position=6,
                label="Histoire",
                gtls=[
                    GTL(code="03020108", label="Histoire", level=4),
                    GTL(code="03020208", label="Histoire", level=4),
                    GTL(code="03020307", label="Histoire", level=4),
                    GTL(code="03030207", label="Histoire", level=4),
                    GTL(code="03030307", label="Histoire", level=4),
                    GTL(code="03030407", label="Histoire", level=4),
                    GTL(code="03030507", label="Histoire", level=4),
                    GTL(code="03030607", label="Histoire", level=4),
                    GTL(code="03030707", label="Histoire", level=4),
                ],
            ),
            BookSubType(
                position=7,
                label="Policier & thriller",
                gtls=[
                    GTL(code="03020107", label="Policier / Thriller", level=4),
                    GTL(code="03020207", label="Policier / Thriller", level=4),
                    GTL(code="03020306", label="Policier / Thriller", level=4),
                    GTL(code="03030206", label="Policier / Thriller", level=4),
                    GTL(code="03030306", label="Policier / Thriller", level=4),
                    GTL(code="03030406", label="Policier / Thriller", level=4),
                    GTL(code="03030506", label="Policier / Thriller", level=4),
                    GTL(code="03030606", label="Policier / Thriller", level=4),
                    GTL(code="03030706", label="Policier / Thriller", level=4),
                ],
            ),
            BookSubType(
                position=8,
                label="Science-fiction",
                gtls=[
                    GTL(code="03020104", label="Science-fiction", level=4),
                    GTL(code="03020204", label="Science-fiction", level=4),
                    GTL(code="03020303", label="Science-fiction", level=4),
                    GTL(code="03030203", label="Science-fiction", level=4),
                    GTL(code="03030303", label="Science-fiction", level=4),
                    GTL(code="03030403", label="Science-fiction", level=4),
                    GTL(code="03030503", label="Science-fiction", level=4),
                    GTL(code="03030603", label="Science-fiction", level=4),
                    GTL(code="03030703", label="Science-fiction", level=4),
                ],
            ),
            BookSubType(
                position=9,
                label="Adaptation",
                gtls=[
                    GTL(code="03020102", label="Adaptation", level=4),
                    GTL(code="03020202", label="Adaptation", level=4),
                    GTL(code="03020301", label="Adaptation", level=4),
                    GTL(code="03030201", label="Adaptation", level=4),
                    GTL(code="03030301", label="Adaptation", level=4),
                    GTL(code="03030401", label="Adaptation", level=4),
                    GTL(code="03030501", label="Adaptation Autre", level=4),
                    GTL(code="03030601", label="Adaptation", level=4),
                    GTL(code="03030701", label="Adaptation", level=4),
                ],
            ),
            BookSubType(
                position=10,
                label="Western",
                gtls=[
                    GTL(code="03020110", label="Western", level=4),
                    GTL(code="03020210", label="Western", level=4),
                    GTL(code="03020309", label="Western", level=4),
                    GTL(code="03030209", label="Western", level=4),
                    GTL(code="03030309", label="Western", level=4),
                    GTL(code="03030409", label="Western", level=4),
                    GTL(code="03030509", label="Western", level=4),
                    GTL(code="03030609", label="Western", level=4),
                    GTL(code="03030709", label="Western", level=4),
                ],
            ),
            BookSubType(position=11, label="Super héros", gtls=[GTL(code="03030400", label="Super Héros", level=3)]),
            BookSubType(position=12, label="Strip", gtls=[GTL(code="03030300", label="Strip", level=3)]),
        ],
    ),
    BookType(
        position=4,
        label="Loisirs & bien-être",
        gtls=[GTL(code="04000000", label="Vie pratique & Loisirs", level=1)],
        children=[
            BookSubType(
                position=1,
                label="Vie quotidienne & bien-être",
                gtls=[GTL(code="04060000", label="Vie quotidienne & Bien-être", level=2)],
            ),
            BookSubType(
                position=2,
                label="Cuisine",
                gtls=[GTL(code="04030000", label="Arts de la table / Gastronomie", level=2)],
            ),
            BookSubType(position=3, label="Activités manuelles", gtls=[GTL(code="04050000", label="Hobbies", level=2)]),
            BookSubType(position=4, label="Jeux", gtls=[GTL(code="04050500", label="Jeux", level=3)]),
            BookSubType(position=5, label="Sports", gtls=[GTL(code="04070000", label="Sports", level=2)]),
            BookSubType(position=6, label="Animaux", gtls=[GTL(code="04020000", label="Animaux", level=2)]),
            BookSubType(
                position=7, label="Nature & plein air", gtls=[GTL(code="04010000", label="Nature & Plein air", level=2)]
            ),
            BookSubType(
                position=8, label="Habitat & maison", gtls=[GTL(code="04040000", label="Habitat / Maison", level=2)]
            ),
            BookSubType(position=9, label="Transports", gtls=[GTL(code="04050700", label="Transports", level=3)]),
        ],
    ),
    BookType(
        position=5,
        label="Société & politique",
        gtls=[
            GTL(code="09000000", label="Sciences humaines & sociales", level=1),
            GTL(code="01110000", label="Actualités & Reportages", level=2),
        ],
        children=[
            BookSubType(position=1, label="Philosophie", gtls=[GTL(code="09080000", label="Philosophie", level=2)]),
            BookSubType(
                position=2,
                label="Sciences politiques",
                gtls=[GTL(code="09110000", label="Sciences politiques & Politique", level=2)],
            ),
            BookSubType(
                position=3,
                label="Sciences sociales & société",
                gtls=[GTL(code="09120000", label="Sciences sociales  / Société", level=2)],
            ),
            BookSubType(
                position=4,
                label="Psychologie & psychanalyse",
                gtls=[GTL(code="09090000", label="Psychologie / Psychanalyse", level=2)],
            ),
            BookSubType(
                position=5,
                label="Actualité & reportage",
                gtls=[GTL(code="01110000", label="Actualités & Reportages", level=2)],
            ),
            BookSubType(
                position=6,
                label="Anthropologie & ethnologie",
                gtls=[
                    GTL(code="09010000", label="Anthropologie", level=2),
                    GTL(code="09020000", label="Ethnologie", level=2),
                ],
            ),
        ],
    ),
    BookType(
        position=6,
        label="Théâtre, poésie & essais",
        gtls=[
            GTL(code="01080000", label="Théâtre", level=2),
            GTL(code="01090000", label="Poésie", level=2),
            GTL(code="01070000", label="Littérature argumentative", level=2),
            GTL(code="01050000", label="Récit", level=2),
        ],
        children=[
            BookSubType(position=1, label="Théâtre", gtls=[GTL(code="01080000", label="Théâtre", level=2)]),
            BookSubType(position=2, label="Poésie", gtls=[GTL(code="01090000", label="Poésie", level=2)]),
            BookSubType(
                position=3,
                label="Essais littéraires",
                gtls=[GTL(code="01070000", label="Littérature argumentative", level=2)],
            ),
            BookSubType(position=4, label="Récit", gtls=[GTL(code="01050000", label="Récit", level=2)]),
        ],
    ),
    BookType(
        position=7,
        label="Compétences générales",
        gtls=[
            GTL(code="08030000", label="Droit", level=2),
            GTL(code="10080000", label="Médecine", level=2),
            GTL(code="08040000", label="Entreprise, gestion et management", level=2),
            GTL(code="08010000", label="Sciences économiques", level=2),
            GTL(code="09050000", label="Histoire", level=2),
            GTL(code="09060000", label="Histoire du monde", level=2),
            GTL(code="09030000", label="Géographie", level=2),
            GTL(code="09040000", label="Géographie du monde", level=2),
            GTL(code="10050000", label="Sciences de la Terre et de l'Univers", level=2),
            GTL(code="10030000", label="Sciences physiques", level=2),
            GTL(code="10020000", label="Mathématiques", level=2),
            GTL(code="10070000", label="Informatique", level=2),
            GTL(code="10060000", label="Sciences appliquées et industrie", level=2),
            GTL(code="13010000", label="Dictionnaires de français", level=2),
            GTL(code="13020000", label="Encyclopédies", level=2),
        ],
        children=[
            BookSubType(position=1, label="Droit", gtls=[GTL(code="08030000", label="Droit", level=2)]),
            BookSubType(position=2, label="Médecine", gtls=[GTL(code="10080000", label="Médecine", level=2)]),
            BookSubType(
                position=3,
                label="Entreprise",
                gtls=[GTL(code="08040000", label="Entreprise, gestion et management", level=2)],
            ),
            BookSubType(
                position=4,
                label="Sciences économiques",
                gtls=[GTL(code="08010000", label="Sciences économiques", level=2)],
            ),
            BookSubType(
                position=5,
                label="Histoire",
                gtls=[
                    GTL(code="09050000", label="Histoire", level=2),
                    GTL(code="09060000", label="Histoire du monde", level=2),
                ],
            ),
            BookSubType(
                position=6,
                label="Géographie",
                gtls=[
                    GTL(code="09030000", label="Géographie", level=2),
                    GTL(code="09040000", label="Géographie du monde", level=2),
                ],
            ),
            BookSubType(
                position=7,
                label="Sciences de la Terre et de l’Univers",
                gtls=[GTL(code="10050000", label="Sciences de la Terre et de l'Univers", level=2)],
            ),
            BookSubType(
                position=8,
                label="Physiques, mathématiques & informatique",
                gtls=[
                    GTL(code="10030000", label="Sciences physiques", level=2),
                    GTL(code="10020000", label="Mathématiques", level=2),
                    GTL(code="10070000", label="Informatique", level=2),
                ],
            ),
            BookSubType(
                position=9,
                label="Sciences appliquées & industrie",
                gtls=[GTL(code="10060000", label="Sciences appliquées et industrie", level=2)],
            ),
            BookSubType(
                position=10,
                label="Dictionnaires",
                gtls=[GTL(code="13010000", label="Dictionnaires de français", level=2)],
            ),
            BookSubType(
                position=11, label="Encyclopédies", gtls=[GTL(code="13020000", label="Encyclopédies", level=2)]
            ),
        ],
    ),
    BookType(
        position=8,
        label="Mode & art",
        gtls=[GTL(code="06000000", label="Arts et spectacles", level=1)],
        children=[
            BookSubType(
                position=1, label="Mode", gtls=[GTL(code="06100200", label="Mode / Parfums / Cosmétiques", level=3)]
            ),
            BookSubType(
                position=2,
                label="Peinture, sculpture & arts graphiques",
                gtls=[
                    GTL(code="06100100", label="Arts appliqués / Arts décoratifs autre", level=3),
                    GTL(code="06100300", label="Décoration d'intérieur", level=3),
                    GTL(code="06100400", label="Métiers d'art", level=3),
                    GTL(code="06100500", label="Techniques / Enseignement", level=3),
                    GTL(code="06050000", label="Peinture / Arts graphiques", level=2),
                    GTL(code="06060000", label="Sculpture / Arts plastiques", level=2),
                ],
            ),
            BookSubType(
                position=3, label="Photos & cinéma", gtls=[GTL(code="06070000", label="Arts de l'image", level=2)]
            ),
            BookSubType(
                position=4,
                label="Architecture, urbanisme & design",
                gtls=[GTL(code="06040000", label="Architecture / Urbanisme", level=2)],
            ),
            BookSubType(position=5, label="Musique", gtls=[GTL(code="06030000", label="Musique", level=2)]),
        ],
    ),
    BookType(
        position=9,
        label="Tourisme & voyages",
        gtls=[GTL(code="05000000", label="Tourisme & Voyages", level=1)],
        children=[
            BookSubType(
                position=1, label="Monde", gtls=[GTL(code="05030000", label="Tourisme & Voyages Monde", level=2)]
            ),
            BookSubType(
                position=2, label="France", gtls=[GTL(code="05020000", label="Tourisme & Voyages France", level=2)]
            ),
            BookSubType(
                position=3, label="Europe", gtls=[GTL(code="05040000", label="Tourisme & Voyages Europe", level=2)]
            ),
            BookSubType(
                position=4, label="Asie", gtls=[GTL(code="05100000", label="Tourisme & Voyages Asie", level=2)]
            ),
            BookSubType(
                position=5,
                label="Amérique du Nord",
                gtls=[GTL(code="05070000", label="Tourisme & Voyages Amérique du Nord", level=2)],
            ),
            BookSubType(
                position=6, label="Afrique", gtls=[GTL(code="05060000", label="Tourisme & Voyages Afrique", level=2)]
            ),
            BookSubType(
                position=7, label="Océanie", gtls=[GTL(code="05110000", label="Tourisme & Voyages Océanie", level=2)]
            ),
            BookSubType(
                position=8,
                label="Arctique & Antarctique",
                gtls=[GTL(code="05120000", label="Tourisme & Voyages Arctique / Antarctique", level=2)],
            ),
            BookSubType(
                position=9,
                label="Amérique centrale & Caraïbes",
                gtls=[GTL(code="05080000", label="Tourisme & Voyages Amérique centrale et Caraïbes", level=2)],
            ),
            BookSubType(
                position=10,
                label="Amérique du Sud",
                gtls=[GTL(code="05090000", label="Tourisme & Voyages Amérique du Sud", level=2)],
            ),
            BookSubType(
                position=11,
                label="Moyen-Orient",
                gtls=[GTL(code="05050000", label="Tourisme & Voyages Moyen-Orient", level=2)],
            ),
        ],
    ),
]
