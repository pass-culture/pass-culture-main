from pcapi.core.categories import app_search_tree
from pcapi.core.categories import models as categories_models
from pcapi.core.categories import subcategories
from pcapi.core.testing import assert_num_queries


class SubcategoriesTest:
    def test_get_subcategories_v2(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/subcategories/v2")

        assert response.status_code == 200

        assert set(response.json.keys()) == {
            "subcategories",
            "searchGroups",
            "homepageLabels",
            "nativeCategories",
            "genreTypes",
        }

        found_subcategory_ids = {x["id"] for x in response.json["subcategories"]}
        expected_subcategory_ids = {x.id for x in subcategories.ALL_SUBCATEGORIES}
        assert found_subcategory_ids == expected_subcategory_ids

        found_search_group_names = {x["name"] for x in response.json["searchGroups"]}
        expected_search_group_names = {x.name for x in app_search_tree.SEARCH_GROUPS}
        assert found_search_group_names == expected_search_group_names

        found_home_labels = {x["name"] for x in response.json["homepageLabels"]}
        expected_home_labels = {x.homepage_label_name for x in subcategories.ALL_SUBCATEGORIES}
        assert found_home_labels == expected_home_labels

        found_native_categories = {x["name"] for x in response.json["nativeCategories"]}
        expected_native_categories = {x.name for x in app_search_tree.NATIVE_CATEGORIES}
        assert found_native_categories == expected_native_categories

        found_genre_types = {x["name"] for x in response.json["genreTypes"]}
        expected_genre_types = {x.name for x in categories_models.GenreType}
        assert found_genre_types == expected_genre_types

    def test_genre_types(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/subcategories/v2")

        genreTypes = response.json["genreTypes"]
        assert genreTypes == [
            {
                "name": "BOOK",
                "values": [
                    {"name": "Art", "value": "Art"},
                    {"name": "Arts Culinaires", "value": "Arts Culinaires"},
                    {"name": "Bandes dessinées", "value": "Bandes dessinées"},
                    {"name": "Carrière/Concours", "value": "Carrière/Concours"},
                    {"name": "Droit", "value": "Droit"},
                    {"name": "Faits, témoignages", "value": "Faits, témoignages"},
                    {"name": "Gestion/entreprise", "value": "Gestion/entreprise"},
                    {"name": "Géographie, cartographie", "value": "Géographie, cartographie"},
                    {"name": "Histoire", "value": "Histoire"},
                    {"name": "Humour", "value": "Humour"},
                    {"name": "Informatique", "value": "Informatique"},
                    {"name": "Jeunesse", "value": "Jeunesse"},
                    {"name": "Jeux", "value": "Jeux"},
                    {"name": "Langue", "value": "Langue"},
                    {"name": "Littérature Européenne", "value": "Littérature Européenne"},
                    {"name": "Littérature française", "value": "Littérature française"},
                    {"name": "Littérature étrangère", "value": "Littérature étrangère"},
                    {"name": "Loisirs", "value": "Loisirs"},
                    {"name": "Manga", "value": "Manga"},
                    {"name": "Marketing et audio-visuel", "value": "Marketing et audio-visuel"},
                    {"name": "Policier", "value": "Policier"},
                    {"name": "Poésie, théâtre et spectacle", "value": "Poésie, théâtre et spectacle"},
                    {"name": "Psychanalyse, psychologie", "value": "Psychanalyse, psychologie"},
                    {"name": "Religions, spiritualités", "value": "Religions, spiritualités"},
                    {"name": "Santé", "value": "Santé"},
                    {
                        "name": "Science-fiction, fantastique & terreur",
                        "value": "Science-fiction, fantastique & terreur",
                    },
                    {
                        "name": "Sciences Humaines, Encyclopédie, dictionnaire",
                        "value": "Sciences Humaines, Encyclopédie, dictionnaire",
                    },
                    {"name": "Sciences, vie & Nature", "value": "Sciences, vie & Nature"},
                    {"name": "Scolaire & Parascolaire", "value": "Scolaire & Parascolaire"},
                    {"name": "Sexualité", "value": "Sexualité"},
                    {"name": "Sociologie", "value": "Sociologie"},
                    {"name": "Sport", "value": "Sport"},
                    {"name": "Tourisme", "value": "Tourisme"},
                    {"name": "Vie pratique", "value": "Vie pratique"},
                    {"name": "Économie", "value": "Économie"},
                ],
                "trees": [
                    {
                        "children": [
                            {
                                "label": "Romance",
                                "gtls": [
                                    {"code": "01020600", "label": "Roman sentimental", "level": 3},
                                    {"code": "92000000", "label": "Romance", "level": 1},
                                ],
                                "position": 1,
                            },
                            {
                                "label": "Thriller",
                                "gtls": [
                                    {"code": "01020500", "label": "Thriller", "level": 3},
                                    {"code": "90020000", "label": "Thriller", "level": 2},
                                ],
                                "position": 2,
                            },
                            {
                                "label": "Fantasy",
                                "gtls": [
                                    {"code": "01020900", "label": "Fantasy", "level": 3},
                                    {"code": "91030000", "label": "Fantasy", "level": 2},
                                ],
                                "position": 3,
                            },
                            {
                                "label": "Policier",
                                "gtls": [
                                    {"code": "01020400", "label": "Policier", "level": 3},
                                    {"code": "90010000", "label": "Policier", "level": 2},
                                ],
                                "position": 4,
                            },
                            {
                                "label": "Œuvres classiques",
                                "gtls": [{"code": "01030000", "label": "Œuvres classiques", "level": 2}],
                                "position": 5,
                            },
                            {
                                "label": "Science-fiction",
                                "gtls": [
                                    {"code": "01020700", "label": "Science-fiction", "level": 3},
                                    {"code": "91010000", "label": "Science-fiction", "level": 2},
                                ],
                                "position": 6,
                            },
                            {
                                "label": "Horreur",
                                "gtls": [
                                    {"code": "01020802", "label": "Horreur / Terreur", "level": 4},
                                    {"code": "91020200", "label": "Horreur / Terreur", "level": 3},
                                ],
                                "position": 7,
                            },
                            {
                                "label": "Aventure",
                                "gtls": [
                                    {"code": "01020200", "label": "Aventure", "level": 3},
                                    {"code": "01020300", "label": "Espionnage", "level": 3},
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Biographie",
                                "gtls": [
                                    {"code": "01060000", "label": "Biographie / Témoignage littéraire", "level": 2}
                                ],
                                "position": 9,
                            },
                            {
                                "label": "Contes & légendes",
                                "gtls": [{"code": "01040000", "label": "Contes / Légendes", "level": 2}],
                                "position": 10,
                            },
                        ],
                        "gtls": [
                            {"code": "01010000", "label": "Romans & Nouvelles", "level": 2},
                            {"code": "01020000", "label": "Romans & Nouvelles de genre", "level": 2},
                            {"code": "01030000", "label": "Œuvres classiques", "level": 2},
                            {"code": "02000000", "label": "Jeunesse", "level": 1},
                            {"code": "01060000", "label": "Biographie / Témoignage littéraire", "level": 2},
                            {"code": "01040000", "label": "Contes / Légendes", "level": 2},
                            {"code": "92000000", "label": "Romance", "level": 1},
                            {"code": "91000000", "label": "Fantasy & Science-fiction", "level": 1},
                            {"code": "90000000", "label": "Policier & Thriller", "level": 1},
                        ],
                        "label": "Romans & littérature",
                        "position": 1,
                    },
                    {
                        "children": [
                            {
                                "label": "Shonen",
                                "gtls": [{"code": "03040500", "label": "Shonen", "level": 3}],
                                "position": 1,
                            },
                            {
                                "label": "Seinen",
                                "gtls": [{"code": "03040600", "label": "Seinen", "level": 3}],
                                "position": 2,
                            },
                            {
                                "label": "Shôjo",
                                "gtls": [{"code": "03040400", "label": "Shôjo", "level": 3}],
                                "position": 3,
                            },
                            {
                                "label": "Yaoi",
                                "gtls": [{"code": "03040800", "label": "Yaoi", "level": 3}],
                                "position": 4,
                            },
                            {
                                "label": "Kodomo",
                                "gtls": [{"code": "03040300", "label": "Kodomo", "level": 3}],
                                "position": 5,
                            },
                            {
                                "label": "Josei",
                                "gtls": [{"code": "03040700", "label": "Josei", "level": 3}],
                                "position": 6,
                            },
                            {
                                "label": "Yuri",
                                "gtls": [{"code": "03040900", "label": "Yuri", "level": 3}],
                                "position": 7,
                            },
                        ],
                        "gtls": [
                            {"code": "03040300", "label": "Kodomo", "level": 3},
                            {"code": "03040400", "label": "Shôjo", "level": 3},
                            {"code": "03040500", "label": "Shonen", "level": 3},
                            {"code": "03040600", "label": "Seinen", "level": 3},
                            {"code": "03040700", "label": "Josei", "level": 3},
                            {"code": "03040800", "label": "Yaoi", "level": 3},
                            {"code": "03040900", "label": "Yuri", "level": 3},
                        ],
                        "label": "Mangas",
                        "position": 2,
                    },
                    {
                        "children": [
                            {
                                "label": "Humour",
                                "gtls": [
                                    {"code": "03020111", "label": "Humour", "level": 4},
                                    {"code": "03020211", "label": "Humour", "level": 4},
                                    {"code": "03020310", "label": "Humour", "level": 4},
                                    {"code": "03030210", "label": "Humour", "level": 4},
                                    {"code": "03030310", "label": "Humour", "level": 4},
                                    {"code": "03030410", "label": "Humour", "level": 4},
                                    {"code": "03030510", "label": "Humour", "level": 4},
                                    {"code": "03030610", "label": "Humour", "level": 4},
                                    {"code": "03030710", "label": "Humour", "level": 4},
                                ],
                                "position": 1,
                            },
                            {
                                "label": "Action & aventure",
                                "gtls": [
                                    {"code": "03020109", "label": "Action / Aventures", "level": 4},
                                    {"code": "03020209", "label": "Action / Aventures", "level": 4},
                                    {"code": "03020308", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030208", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030308", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030408", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030508", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030608", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030708", "label": "Action / Aventures", "level": 4},
                                ],
                                "position": 2,
                            },
                            {
                                "label": "Fantastique & épouvante",
                                "gtls": [
                                    {"code": "03020206", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03020305", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030205", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030305", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030405", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030505", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030605", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030705", "label": "Fantastique / Epouvante", "level": 4},
                                ],
                                "position": 3,
                            },
                            {
                                "label": "Documentaire & société",
                                "gtls": [
                                    {"code": "03020103", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03020203", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03020302", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030202", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030302", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030402", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030502", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030602", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030702", "label": "Documentaire / Société", "level": 4},
                                ],
                                "position": 4,
                            },
                            {
                                "label": "Fantasy",
                                "gtls": [
                                    {"code": "03020105", "label": "Fantasy", "level": 4},
                                    {"code": "03020205", "label": "Fantasy", "level": 4},
                                    {"code": "03020304", "label": "Fantasy", "level": 4},
                                    {"code": "03030204", "label": "Fantasy", "level": 4},
                                    {"code": "03030304", "label": "Fantasy", "level": 4},
                                    {"code": "03030404", "label": "Fantasy", "level": 4},
                                    {"code": "03030504", "label": "Fantasy", "level": 4},
                                    {"code": "03030604", "label": "Fantasy", "level": 4},
                                    {"code": "03030704", "label": "Fantasy", "level": 4},
                                ],
                                "position": 5,
                            },
                            {
                                "label": "Histoire",
                                "gtls": [
                                    {"code": "03020108", "label": "Histoire", "level": 4},
                                    {"code": "03020208", "label": "Histoire", "level": 4},
                                    {"code": "03020307", "label": "Histoire", "level": 4},
                                    {"code": "03030207", "label": "Histoire", "level": 4},
                                    {"code": "03030307", "label": "Histoire", "level": 4},
                                    {"code": "03030407", "label": "Histoire", "level": 4},
                                    {"code": "03030507", "label": "Histoire", "level": 4},
                                    {"code": "03030607", "label": "Histoire", "level": 4},
                                    {"code": "03030707", "label": "Histoire", "level": 4},
                                ],
                                "position": 6,
                            },
                            {
                                "label": "Policier & thriller",
                                "gtls": [
                                    {"code": "03020107", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03020207", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03020306", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030206", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030306", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030406", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030506", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030606", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030706", "label": "Policier / Thriller", "level": 4},
                                ],
                                "position": 7,
                            },
                            {
                                "label": "Science-fiction",
                                "gtls": [
                                    {"code": "03020104", "label": "Science-fiction", "level": 4},
                                    {"code": "03020204", "label": "Science-fiction", "level": 4},
                                    {"code": "03020303", "label": "Science-fiction", "level": 4},
                                    {"code": "03030203", "label": "Science-fiction", "level": 4},
                                    {"code": "03030303", "label": "Science-fiction", "level": 4},
                                    {"code": "03030403", "label": "Science-fiction", "level": 4},
                                    {"code": "03030503", "label": "Science-fiction", "level": 4},
                                    {"code": "03030603", "label": "Science-fiction", "level": 4},
                                    {"code": "03030703", "label": "Science-fiction", "level": 4},
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Adaptation",
                                "gtls": [
                                    {"code": "03020102", "label": "Adaptation", "level": 4},
                                    {"code": "03020202", "label": "Adaptation", "level": 4},
                                    {"code": "03020301", "label": "Adaptation", "level": 4},
                                    {"code": "03030201", "label": "Adaptation", "level": 4},
                                    {"code": "03030301", "label": "Adaptation", "level": 4},
                                    {"code": "03030401", "label": "Adaptation", "level": 4},
                                    {"code": "03030501", "label": "Adaptation Autre", "level": 4},
                                    {"code": "03030601", "label": "Adaptation", "level": 4},
                                    {"code": "03030701", "label": "Adaptation", "level": 4},
                                ],
                                "position": 9,
                            },
                            {
                                "label": "Western",
                                "gtls": [
                                    {"code": "03020110", "label": "Western", "level": 4},
                                    {"code": "03020210", "label": "Western", "level": 4},
                                    {"code": "03020309", "label": "Western", "level": 4},
                                    {"code": "03030209", "label": "Western", "level": 4},
                                    {"code": "03030309", "label": "Western", "level": 4},
                                    {"code": "03030409", "label": "Western", "level": 4},
                                    {"code": "03030509", "label": "Western", "level": 4},
                                    {"code": "03030609", "label": "Western", "level": 4},
                                    {"code": "03030709", "label": "Western", "level": 4},
                                ],
                                "position": 10,
                            },
                            {
                                "label": "Super héros",
                                "gtls": [{"code": "03030400", "label": "Super Héros", "level": 3}],
                                "position": 11,
                            },
                            {
                                "label": "Strip",
                                "gtls": [{"code": "03030300", "label": "Strip", "level": 3}],
                                "position": 12,
                            },
                        ],
                        "gtls": [
                            {"code": "03020000", "label": "Bandes dessinées", "level": 2},
                            {"code": "03030000", "label": "Comics", "level": 2},
                        ],
                        "label": "BD & comics",
                        "position": 3,
                    },
                    {
                        "children": [
                            {
                                "label": "Vie quotidienne & bien-être",
                                "gtls": [{"code": "04060000", "label": "Vie quotidienne & Bien-être", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Cuisine",
                                "gtls": [{"code": "04030000", "label": "Arts de la table / Gastronomie", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Activités manuelles",
                                "gtls": [{"code": "04050000", "label": "Hobbies", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Jeux",
                                "gtls": [{"code": "04050500", "label": "Jeux", "level": 3}],
                                "position": 4,
                            },
                            {
                                "label": "Sports",
                                "gtls": [{"code": "04070000", "label": "Sports", "level": 2}],
                                "position": 5,
                            },
                            {
                                "label": "Animaux",
                                "gtls": [{"code": "04020000", "label": "Animaux", "level": 2}],
                                "position": 6,
                            },
                            {
                                "label": "Nature & plein air",
                                "gtls": [{"code": "04010000", "label": "Nature & Plein air", "level": 2}],
                                "position": 7,
                            },
                            {
                                "label": "Habitat & maison",
                                "gtls": [{"code": "04040000", "label": "Habitat / Maison", "level": 2}],
                                "position": 8,
                            },
                            {
                                "label": "Transports",
                                "gtls": [{"code": "04050700", "label": "Transports", "level": 3}],
                                "position": 9,
                            },
                        ],
                        "gtls": [{"code": "04000000", "label": "Vie pratique & Loisirs", "level": 1}],
                        "label": "Loisirs & bien-être",
                        "position": 4,
                    },
                    {
                        "children": [
                            {
                                "label": "Philosophie",
                                "gtls": [{"code": "09080000", "label": "Philosophie", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Sciences politiques",
                                "gtls": [{"code": "09110000", "label": "Sciences politiques & Politique", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Sciences sociales & société",
                                "gtls": [{"code": "09120000", "label": "Sciences sociales  / Société", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Psychologie & psychanalyse",
                                "gtls": [{"code": "09090000", "label": "Psychologie / Psychanalyse", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Actualité & reportage",
                                "gtls": [{"code": "01110000", "label": "Actualités & Reportages", "level": 2}],
                                "position": 5,
                            },
                            {
                                "label": "Anthropologie & ethnologie",
                                "gtls": [
                                    {"code": "09010000", "label": "Anthropologie", "level": 2},
                                    {"code": "09020000", "label": "Ethnologie", "level": 2},
                                ],
                                "position": 6,
                            },
                        ],
                        "gtls": [
                            {"code": "09000000", "label": "Sciences humaines & sociales", "level": 1},
                            {"code": "01110000", "label": "Actualités & Reportages", "level": 2},
                        ],
                        "label": "Société & politique",
                        "position": 5,
                    },
                    {
                        "children": [
                            {
                                "label": "Théâtre",
                                "gtls": [{"code": "01080000", "label": "Théâtre", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Poésie",
                                "gtls": [{"code": "01090000", "label": "Poésie", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Essais littéraires",
                                "gtls": [{"code": "01070000", "label": "Littérature argumentative", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Récit",
                                "gtls": [{"code": "01050000", "label": "Récit", "level": 2}],
                                "position": 4,
                            },
                        ],
                        "gtls": [
                            {"code": "01080000", "label": "Théâtre", "level": 2},
                            {"code": "01090000", "label": "Poésie", "level": 2},
                            {"code": "01070000", "label": "Littérature argumentative", "level": 2},
                            {"code": "01050000", "label": "Récit", "level": 2},
                        ],
                        "label": "Théâtre, poésie & essais",
                        "position": 6,
                    },
                    {
                        "children": [
                            {
                                "label": "Droit",
                                "gtls": [{"code": "08030000", "label": "Droit", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Médecine",
                                "gtls": [{"code": "10080000", "label": "Médecine", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Entreprise",
                                "gtls": [
                                    {"code": "08040000", "label": "Entreprise, gestion et management", "level": 2}
                                ],
                                "position": 3,
                            },
                            {
                                "label": "Sciences économiques",
                                "gtls": [{"code": "08010000", "label": "Sciences économiques", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Histoire",
                                "gtls": [
                                    {"code": "09050000", "label": "Histoire", "level": 2},
                                    {"code": "09060000", "label": "Histoire du monde", "level": 2},
                                ],
                                "position": 5,
                            },
                            {
                                "label": "Géographie",
                                "gtls": [
                                    {"code": "09030000", "label": "Géographie", "level": 2},
                                    {"code": "09040000", "label": "Géographie du monde", "level": 2},
                                ],
                                "position": 6,
                            },
                            {
                                "label": "Sciences de la Terre et de l’Univers",
                                "gtls": [
                                    {"code": "10050000", "label": "Sciences de la Terre et de l'Univers", "level": 2}
                                ],
                                "position": 7,
                            },
                            {
                                "label": "Physiques, mathématiques & informatique",
                                "gtls": [
                                    {"code": "10030000", "label": "Sciences physiques", "level": 2},
                                    {"code": "10020000", "label": "Mathématiques", "level": 2},
                                    {"code": "10070000", "label": "Informatique", "level": 2},
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Sciences appliquées & industrie",
                                "gtls": [{"code": "10060000", "label": "Sciences appliquées et industrie", "level": 2}],
                                "position": 9,
                            },
                            {
                                "label": "Dictionnaires",
                                "gtls": [{"code": "13010000", "label": "Dictionnaires de français", "level": 2}],
                                "position": 10,
                            },
                            {
                                "label": "Encyclopédies",
                                "gtls": [{"code": "13020000", "label": "Encyclopédies", "level": 2}],
                                "position": 11,
                            },
                        ],
                        "gtls": [
                            {"code": "08030000", "label": "Droit", "level": 2},
                            {"code": "10080000", "label": "Médecine", "level": 2},
                            {"code": "08040000", "label": "Entreprise, gestion et management", "level": 2},
                            {"code": "08010000", "label": "Sciences économiques", "level": 2},
                            {"code": "09050000", "label": "Histoire", "level": 2},
                            {"code": "09060000", "label": "Histoire du monde", "level": 2},
                            {"code": "09030000", "label": "Géographie", "level": 2},
                            {"code": "09040000", "label": "Géographie du monde", "level": 2},
                            {"code": "10050000", "label": "Sciences de la Terre et de l'Univers", "level": 2},
                            {"code": "10030000", "label": "Sciences physiques", "level": 2},
                            {"code": "10020000", "label": "Mathématiques", "level": 2},
                            {"code": "10070000", "label": "Informatique", "level": 2},
                            {"code": "10060000", "label": "Sciences appliquées et industrie", "level": 2},
                            {"code": "13010000", "label": "Dictionnaires de français", "level": 2},
                            {"code": "13020000", "label": "Encyclopédies", "level": 2},
                        ],
                        "label": "Compétences générales",
                        "position": 7,
                    },
                    {
                        "children": [
                            {
                                "label": "Mode",
                                "gtls": [{"code": "06100200", "label": "Mode / Parfums / Cosmétiques", "level": 3}],
                                "position": 1,
                            },
                            {
                                "label": "Peinture, sculpture & arts graphiques",
                                "gtls": [
                                    {"code": "06100100", "label": "Arts appliqués / Arts décoratifs autre", "level": 3},
                                    {"code": "06100300", "label": "Décoration d'intérieur", "level": 3},
                                    {"code": "06100400", "label": "Métiers d'art", "level": 3},
                                    {"code": "06100500", "label": "Techniques / Enseignement", "level": 3},
                                    {"code": "06050000", "label": "Peinture / Arts graphiques", "level": 2},
                                    {"code": "06060000", "label": "Sculpture / Arts plastiques", "level": 2},
                                ],
                                "position": 2,
                            },
                            {
                                "label": "Photos & cinéma",
                                "gtls": [{"code": "06070000", "label": "Arts de l'image", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Architecture, urbanisme & design",
                                "gtls": [{"code": "06040000", "label": "Architecture / Urbanisme", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Musique",
                                "gtls": [{"code": "06030000", "label": "Musique", "level": 2}],
                                "position": 5,
                            },
                        ],
                        "gtls": [{"code": "06000000", "label": "Arts et spectacles", "level": 1}],
                        "label": "Mode & art",
                        "position": 8,
                    },
                    {
                        "children": [
                            {
                                "label": "Monde",
                                "gtls": [{"code": "05030000", "label": "Tourisme & Voyages Monde", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "France",
                                "gtls": [{"code": "05020000", "label": "Tourisme & Voyages France", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Europe",
                                "gtls": [{"code": "05040000", "label": "Tourisme & Voyages Europe", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Asie",
                                "gtls": [{"code": "05100000", "label": "Tourisme & Voyages Asie", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Amérique du Nord",
                                "gtls": [
                                    {"code": "05070000", "label": "Tourisme & Voyages Amérique du Nord", "level": 2}
                                ],
                                "position": 5,
                            },
                            {
                                "label": "Afrique",
                                "gtls": [{"code": "05060000", "label": "Tourisme & Voyages Afrique", "level": 2}],
                                "position": 6,
                            },
                            {
                                "label": "Océanie",
                                "gtls": [{"code": "05110000", "label": "Tourisme & Voyages Océanie", "level": 2}],
                                "position": 7,
                            },
                            {
                                "label": "Arctique & Antarctique",
                                "gtls": [
                                    {
                                        "code": "05120000",
                                        "label": "Tourisme & Voyages Arctique / Antarctique",
                                        "level": 2,
                                    }
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Amérique centrale & Caraïbes",
                                "gtls": [
                                    {
                                        "code": "05080000",
                                        "label": "Tourisme & Voyages Amérique centrale et Caraïbes",
                                        "level": 2,
                                    }
                                ],
                                "position": 9,
                            },
                            {
                                "label": "Amérique du Sud",
                                "gtls": [
                                    {"code": "05090000", "label": "Tourisme & Voyages Amérique du Sud", "level": 2}
                                ],
                                "position": 10,
                            },
                            {
                                "label": "Moyen-Orient",
                                "gtls": [{"code": "05050000", "label": "Tourisme & Voyages Moyen-Orient", "level": 2}],
                                "position": 11,
                            },
                        ],
                        "gtls": [{"code": "05000000", "label": "Tourisme & Voyages", "level": 1}],
                        "label": "Tourisme & voyages",
                        "position": 9,
                    },
                ],
            },
            {
                "name": "MUSIC",
                "values": [
                    {"name": "ALTERNATIF", "value": "Alternatif"},
                    {"name": "AMBIANCE", "value": "Ambiance"},
                    {"name": "AUTRES", "value": "Autre"},
                    {"name": "BANDES_ORIGINALES", "value": "Bandes originales"},
                    {"name": "COMPILATIONS", "value": "Compilations"},
                    {"name": "COUNTRY-FOLK", "value": "Country / Folk"},
                    {"name": "ELECTRO", "value": "Electro"},
                    {"name": "ENFANTS", "value": "Enfants"},
                    {"name": "FUNK-SOUL-RNB-DISCO", "value": "Funk / Soul / RnB / Disco"},
                    {"name": "JAZZ-BLUES", "value": "Jazz / Blues"},
                    {"name": "METAL", "value": "Metal"},
                    {"name": "MUSIQUE_CLASSIQUE", "value": "Musique Classique"},
                    {"name": "MUSIQUE_DU_MONDE", "value": "Musique du monde"},
                    {"name": "POP", "value": "Pop"},
                    {"name": "RAP-HIP HOP", "value": "Rap / Hip Hop"},
                    {"name": "REGGAE-RAGGA", "value": "Reggae / Ragga"},
                    {"name": "ROCK", "value": "Rock"},
                    {"name": "VARIETES", "value": "Variétés"},
                    {"name": "VIDEOS_MUSICALES", "value": "Vidéos musicales"},
                ],
                "trees": [
                    {"label": "Musique Classique", "name": "MUSIQUE_CLASSIQUE"},
                    {"label": "Jazz / Blues", "name": "JAZZ-BLUES"},
                    {"label": "Bandes originales", "name": "BANDES_ORIGINALES"},
                    {"label": "Electro", "name": "ELECTRO"},
                    {"label": "Pop", "name": "POP"},
                    {"label": "Rock", "name": "ROCK"},
                    {"label": "Metal", "name": "METAL"},
                    {"label": "Alternatif", "name": "ALTERNATIF"},
                    {"label": "Variétés", "name": "VARIETES"},
                    {"label": "Funk / Soul / RnB / Disco", "name": "FUNK-SOUL-RNB-DISCO"},
                    {"label": "Rap / Hip Hop", "name": "RAP-HIP HOP"},
                    {"label": "Reggae / Ragga", "name": "REGGAE-RAGGA"},
                    {"label": "Musique du monde", "name": "MUSIQUE_DU_MONDE"},
                    {"label": "Country / Folk", "name": "COUNTRY-FOLK"},
                    {"label": "Vidéos musicales", "name": "VIDEOS_MUSICALES"},
                    {"label": "Compilations", "name": "COMPILATIONS"},
                    {"label": "Ambiance", "name": "AMBIANCE"},
                    {"label": "Enfants", "name": "ENFANTS"},
                    {"label": "Autre", "name": "AUTRES"},
                ],
            },
            {
                "name": "SHOW",
                "values": [
                    {"name": "Arts de la rue", "value": "Arts de la rue"},
                    {"name": "Autre", "value": "Autre"},
                    {
                        "name": "Autre (spectacle sur glace, historique, aquatique, …)  ",
                        "value": "Autre (spectacle sur glace, historique, aquatique, …)  ",
                    },
                    {"name": "Cirque", "value": "Cirque"},
                    {"name": "Danse", "value": "Danse"},
                    {"name": "Humour / Café-théâtre", "value": "Humour / Café-théâtre"},
                    {"name": "Opéra", "value": "Opéra"},
                    {"name": "Pluridisciplinaire", "value": "Pluridisciplinaire"},
                    {"name": "Spectacle Jeunesse", "value": "Spectacle Jeunesse"},
                    {
                        "name": "Spectacle Musical / Cabaret / Opérette",
                        "value": "Spectacle Musical / Cabaret / Opérette",
                    },
                    {"name": "Théâtre", "value": "Théâtre"},
                ],
                "trees": [
                    {
                        "children": [
                            {"code": 101, "label": "Carnaval", "slug": "ART_DE_LA_RUE-CARNAVAL"},
                            {"code": 102, "label": "Fanfare", "slug": "ART_DE_LA_RUE-FANFARE"},
                            {"code": 103, "label": "Mime", "slug": "ART_DE_LA_RUE-MIME"},
                            {"code": 104, "label": "Parade", "slug": "ART_DE_LA_RUE-PARADE"},
                            {"code": 105, "label": "Théâtre de Rue", "slug": "ART_DE_LA_RUE-THEATRE_DE_RUE"},
                            {"code": 106, "label": "Théâtre Promenade", "slug": "ART_DE_LA_RUE-THEATRE_PROMENADE"},
                            {"code": -1, "label": "Autre", "slug": "ART_DE_LA_RUE-OTHER"},
                        ],
                        "code": 100,
                        "label": "Arts de la rue",
                    },
                    {
                        "children": [
                            {"code": 201, "label": "Cirque Contemporain", "slug": "CIRQUE-CIRQUE_CONTEMPORAIN"},
                            {"code": 202, "label": "Cirque Hors les murs", "slug": "CIRQUE-CIRQUE_HORS_LES_MURS"},
                            {"code": 203, "label": "Cirque Traditionel", "slug": "CIRQUE-CIRQUE_TRADITIONNEL"},
                            {"code": 204, "label": "Cirque Voyageur", "slug": "CIRQUE-CIRQUE_VOYAGEUR"},
                            {"code": 205, "label": "Clown", "slug": "CIRQUE-CLOWN"},
                            {"code": 206, "label": "Hypnose", "slug": "CIRQUE-HYPNOSE"},
                            {"code": 207, "label": "Mentaliste", "slug": "CIRQUE-MENTALISTE"},
                            {"code": 208, "label": "Spectacle de Magie", "slug": "CIRQUE-SPECTACLE_DE_MAGIE"},
                            {"code": 209, "label": "Spectacle Équestre", "slug": "CIRQUE-SPECTACLE_EQUESTRE"},
                            {"code": -1, "label": "Autre", "slug": "CIRQUE-OTHER"},
                        ],
                        "code": 200,
                        "label": "Cirque",
                    },
                    {
                        "children": [
                            {"code": 302, "label": "Ballet", "slug": "DANSE-BALLET"},
                            {"code": 303, "label": "Cancan", "slug": "DANSE-CANCAN"},
                            {"code": 304, "label": "Claquette", "slug": "DANSE-CLAQUETTE"},
                            {"code": 305, "label": "Classique", "slug": "DANSE-CLASSIQUE"},
                            {"code": 306, "label": "Contemporaine", "slug": "DANSE-CONTEMPORAINE"},
                            {"code": 307, "label": "Danse du Monde", "slug": "DANSE-DANSE_DU_MONDE"},
                            {"code": 308, "label": "Flamenco", "slug": "DANSE-FLAMENCO"},
                            {"code": 309, "label": "Moderne Jazz", "slug": "DANSE-MODERNE_JAZZ"},
                            {"code": 311, "label": "Salsa", "slug": "DANSE-SALSA"},
                            {"code": 312, "label": "Swing", "slug": "DANSE-SWING"},
                            {"code": 313, "label": "Tango", "slug": "DANSE-TANGO"},
                            {"code": 314, "label": "Urbaine", "slug": "DANSE-URBAINE"},
                            {"code": -1, "label": "Autre", "slug": "DANSE-OTHER"},
                        ],
                        "code": 300,
                        "label": "Danse",
                    },
                    {
                        "children": [
                            {"code": 401, "label": "Café Théâtre", "slug": "HUMOUR-CAFE_THEATRE"},
                            {"code": 402, "label": "Improvisation", "slug": "HUMOUR-IMPROVISATION"},
                            {"code": 403, "label": "Seul.e en scène", "slug": "HUMOUR-SEUL_EN_SCENE"},
                            {"code": 404, "label": "Sketch", "slug": "HUMOUR-SKETCH"},
                            {"code": 405, "label": "Stand Up", "slug": "HUMOUR-STAND_UP"},
                            {"code": 406, "label": "Ventriloque", "slug": "HUMOUR-VENTRILOQUE"},
                            {"code": -1, "label": "Autre", "slug": "HUMOUR-OTHER"},
                        ],
                        "code": 400,
                        "label": "Humour / Café-théâtre",
                    },
                    {
                        "children": [
                            {"code": 1101, "label": "Cabaret", "slug": "SPECTACLE_MUSICAL-CABARET"},
                            {"code": 1102, "label": "Café Concert", "slug": "SPECTACLE_MUSICAL-CAFE_CONCERT"},
                            {"code": 1103, "label": "Claquette", "slug": "SPECTACLE_MUSICAL-CLAQUETTE"},
                            {"code": 1104, "label": "Comédie Musicale", "slug": "SPECTACLE_MUSICAL-COMEDIE_MUSICALE"},
                            {"code": 1105, "label": "Opéra Bouffe", "slug": "SPECTACLE_MUSICAL-OPERA_BOUFFE"},
                            {"code": 1108, "label": "Opérette", "slug": "SPECTACLE_MUSICAL-OPERETTE"},
                            {"code": 1109, "label": "Revue", "slug": "SPECTACLE_MUSICAL-REVUE"},
                            {"code": 1111, "label": "Burlesque", "slug": "SPECTACLE_MUSICAL-BURLESQUE"},
                            {"code": 1112, "label": "Comédie-Ballet", "slug": "SPECTACLE_MUSICAL-COMEDIE_BALLET"},
                            {"code": 1113, "label": "Opéra Comique", "slug": "SPECTACLE_MUSICAL-OPERA_COMIQUE"},
                            {"code": 1114, "label": "Opéra-Ballet", "slug": "SPECTACLE_MUSICAL-OPERA_BALLET"},
                            {"code": 1115, "label": "Théâtre musical", "slug": "SPECTACLE_MUSICAL-THEATRE_MUSICAL"},
                            {"code": -1, "label": "Autre", "slug": "SPECTACLE_MUSICAL-OTHER"},
                        ],
                        "code": 1100,
                        "label": "Spectacle Musical / Cabaret / Opérette",
                    },
                    {
                        "children": [
                            {"code": 1201, "label": "Conte", "slug": "SPECTACLE_JEUNESSE-CONTE"},
                            {"code": 1202, "label": "Théâtre jeunesse", "slug": "SPECTACLE_JEUNESSE-THEATRE_JEUNESSE"},
                            {
                                "code": 1203,
                                "label": "Spectacle Petite Enfance",
                                "slug": "SPECTACLE_JEUNESSE-SPECTACLE_PETITE_ENFANCE",
                            },
                            {"code": 1204, "label": "Magie Enfance", "slug": "SPECTACLE_JEUNESSE-MAGIE_ENFANCE"},
                            {
                                "code": 1205,
                                "label": "Spectacle pédagogique",
                                "slug": "SPECTACLE_JEUNESSE-SPECTACLE_PEDAGOGIQUE",
                            },
                            {"code": 1206, "label": "Marionettes", "slug": "SPECTACLE_JEUNESSE-MARIONETTES"},
                            {
                                "code": 1207,
                                "label": "Comédie musicale jeunesse",
                                "slug": "SPECTACLE_JEUNESSE-COMEDIE_MUSICALE_JEUNESSE",
                            },
                            {"code": 1208, "label": "Théâtre d'Ombres", "slug": "SPECTACLE_JEUNESSE-THEATRE_D_OMBRES"},
                            {"code": -1, "label": "Autre", "slug": "SPECTACLE_JEUNESSE-OTHER"},
                        ],
                        "code": 1200,
                        "label": "Spectacle Jeunesse",
                    },
                    {
                        "children": [
                            {"code": 1301, "label": "Boulevard", "slug": "THEATRE-BOULEVARD"},
                            {"code": 1302, "label": "Classique", "slug": "THEATRE-CLASSIQUE"},
                            {"code": 1303, "label": "Comédie", "slug": "THEATRE-COMEDIE"},
                            {"code": 1304, "label": "Contemporain", "slug": "THEATRE-CONTEMPORAIN"},
                            {"code": 1305, "label": "Lecture", "slug": "THEATRE-LECTURE"},
                            {
                                "code": 1306,
                                "label": "Spectacle Scénographique",
                                "slug": "THEATRE-SPECTACLE_SCENOGRAPHIQUE",
                            },
                            {"code": 1307, "label": "Théâtre Experimental", "slug": "THEATRE-THEATRE_EXPERIMENTAL"},
                            {"code": 1308, "label": "Théâtre d'Objet", "slug": "THEATRE-THEATRE_D_OBJET"},
                            {"code": 1309, "label": "Tragédie", "slug": "THEATRE-TRAGEDIE"},
                            {"code": -1, "label": "Autre", "slug": "THEATRE-OTHER"},
                        ],
                        "code": 1300,
                        "label": "Théâtre",
                    },
                    {
                        "children": [
                            {"code": 1401, "label": "Performance", "slug": "PLURIDISCIPLINAIRE-PERFORMANCE"},
                            {"code": 1402, "label": "Poésie", "slug": "PLURIDISCIPLINAIRE-POESIE"},
                            {"code": -1, "label": "Autre", "slug": "PLURIDISCIPLINAIRE-OTHER"},
                        ],
                        "code": 1400,
                        "label": "Pluridisciplinaire",
                    },
                    {
                        "children": [
                            {"code": 1501, "label": "Son et lumière", "slug": "OTHER-SON_ET_LUMIERE"},
                            {"code": 1502, "label": "Spectacle sur glace", "slug": "OTHER-SPECTACLE_SUR_GLACE"},
                            {"code": 1503, "label": "Spectacle historique", "slug": "OTHER-SPECTACLE_HISTORIQUE"},
                            {"code": 1504, "label": "Spectacle aquatique", "slug": "OTHER-SPECTACLE_AQUATIQUE"},
                            {"code": -1, "label": "Autre", "slug": "OTHER-OTHER"},
                        ],
                        "code": 1500,
                        "label": "Autre (spectacle sur glace, historique, aquatique, …)  ",
                    },
                    {
                        "children": [
                            {"code": 1511, "label": "Opéra série", "slug": "OPERA-OPERA_SERIE"},
                            {"code": 1512, "label": "Grand opéra", "slug": "OPERA-GRAND_OPERA"},
                            {"code": 1513, "label": "Opéra bouffe", "slug": "OPERA-OPERA_BOUFFE"},
                            {"code": 1514, "label": "Opéra comique", "slug": "OPERA-OPERA_COMIQUE"},
                            {"code": 1515, "label": "Opéra-ballet", "slug": "OPERA-OPERA_BALLET"},
                            {"code": 1516, "label": "Singspiel", "slug": "OPERA-SINGSPIEL"},
                            {"code": -1, "label": "Autre", "slug": "OPERA-OTHER"},
                        ],
                        "code": 1510,
                        "label": "Opéra",
                    },
                    {"children": [{"code": -1, "label": "Autre", "slug": "OTHER"}], "code": -1, "label": "Autre"},
                ],
            },
            {
                "name": "MOVIE",
                "values": [
                    {"name": "ACTION", "value": "Action"},
                    {"name": "ANIMATION", "value": "Animation"},
                    {"name": "MARTIAL_ARTS", "value": "Arts martiaux"},
                    {"name": "ADVENTURE", "value": "Aventure"},
                    {"name": "BIOPIC", "value": "Biopic"},
                    {"name": "BOLLYWOOD", "value": "Bollywood"},
                    {"name": "COMEDY", "value": "Comédie"},
                    {"name": "COMEDY_DRAMA", "value": "Comédie dramatique"},
                    {"name": "MUSICAL", "value": "Comédie musicale"},
                    {"name": "CONCERT", "value": "Concert"},
                    {"name": "DIVERS", "value": "Divers"},
                    {"name": "DOCUMENTARY", "value": "Documentaire"},
                    {"name": "DRAMA", "value": "Drame"},
                    {"name": "KOREAN_DRAMA", "value": "Drame coréen"},
                    {"name": "SPY", "value": "Espionnage"},
                    {"name": "EXPERIMENTAL", "value": "Expérimental"},
                    {"name": "FAMILY", "value": "Familial"},
                    {"name": "FANTASY", "value": "Fantastique"},
                    {"name": "WARMOVIE", "value": "Guerre"},
                    {"name": "HISTORICAL", "value": "Historique"},
                    {"name": "HISTORICAL_EPIC", "value": "Historique-épique"},
                    {"name": "HORROR", "value": "Horreur"},
                    {"name": "JUDICIAL", "value": "Judiciaire"},
                    {"name": "MUSIC", "value": "Musique"},
                    {"name": "OPERA", "value": "Opéra"},
                    {"name": "PERFORMANCE", "value": "Performance"},
                    {"name": "DETECTIVE", "value": "Policier"},
                    {"name": "ROMANCE", "value": "Romance"},
                    {"name": "SCIENCE_FICTION", "value": "Science-fiction"},
                    {"name": "SPORT_EVENT", "value": "Sport"},
                    {"name": "THRILLER", "value": "Thriller"},
                    {"name": "WESTERN", "value": "Western"},
                    {"name": "EROTIC", "value": "Érotique"},
                ],
                "trees": [
                    {"label": "Action", "name": "ACTION"},
                    {"label": "Aventure", "name": "ADVENTURE"},
                    {"label": "Animation", "name": "ANIMATION"},
                    {"label": "Biopic", "name": "BIOPIC"},
                    {"label": "Bollywood", "name": "BOLLYWOOD"},
                    {"label": "Comédie", "name": "COMEDY"},
                    {"label": "Comédie dramatique", "name": "COMEDY_DRAMA"},
                    {"label": "Concert", "name": "CONCERT"},
                    {"label": "Policier", "name": "DETECTIVE"},
                    {"label": "Divers", "name": "DIVERS"},
                    {"label": "Documentaire", "name": "DOCUMENTARY"},
                    {"label": "Drame", "name": "DRAMA"},
                    {"label": "Érotique", "name": "EROTIC"},
                    {"label": "Expérimental", "name": "EXPERIMENTAL"},
                    {"label": "Familial", "name": "FAMILY"},
                    {"label": "Fantastique", "name": "FANTASY"},
                    {"label": "Historique", "name": "HISTORICAL"},
                    {"label": "Historique-épique", "name": "HISTORICAL_EPIC"},
                    {"label": "Horreur", "name": "HORROR"},
                    {"label": "Judiciaire", "name": "JUDICIAL"},
                    {"label": "Drame coréen", "name": "KOREAN_DRAMA"},
                    {"label": "Arts martiaux", "name": "MARTIAL_ARTS"},
                    {"label": "Musique", "name": "MUSIC"},
                    {"label": "Comédie musicale", "name": "MUSICAL"},
                    {"label": "Opéra", "name": "OPERA"},
                    {"label": "Performance", "name": "PERFORMANCE"},
                    {"label": "Romance", "name": "ROMANCE"},
                    {"label": "Science-fiction", "name": "SCIENCE_FICTION"},
                    {"label": "Sport", "name": "SPORT_EVENT"},
                    {"label": "Espionnage", "name": "SPY"},
                    {"label": "Thriller", "name": "THRILLER"},
                    {"label": "Guerre", "name": "WARMOVIE"},
                    {"label": "Western", "name": "WESTERN"},
                ],
            },
        ]


class CategoriesTest:
    def test_returns_200(self, client):
        response = client.get("/native/v1/categories")

        assert response.status_code == 200
