import copy


ALLOCINE_MOVIE_LIST_PAGE_1 = {
    "movieList": {
        "totalCount": 4,
        "pageInfo": {"hasNextPage": True, "endCursor": "YXJyYXljb25uZWN0aW9uOjQ5"},
        "edges": [
            {
                "node": {
                    "id": "TW92aWU6MTMxMTM2",
                    "internalId": 131136,
                    "backlink": {
                        "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=131136.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                    },
                    "data": {"eidr": None, "productionYear": 1915},
                    "title": "Ceux de chez nous",
                    "originalTitle": "Ceux de chez nous",
                    "type": "FEATURE_FILM",
                    "runtime": "PT0H21M0S",
                    "poster": {"url": "https://fr.web.img2.acsta.net/medias/nmedia/18/78/15/02/19447537.jpg"},
                    "synopsis": "Alors que la Premi\u00e8re Guerre Mondiale a \u00e9clat\u00e9, et en r\u00e9ponse aux propos des intellectuels allemands de l'\u00e9poque, Sacha Guitry filme les grands artistes de l'\u00e9poque qui contribuent au rayonnement culturel de la France.",
                    "releases": [
                        {
                            "name": "ReRelease",
                            "releaseDate": {"date": "2023-11-01"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [411399]"},
                                "visa_number": "108245",
                            },
                            "certificate": None,
                        },
                        {
                            "name": "Released",
                            "releaseDate": {"date": "1915-11-22"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [411400]"},
                                "visa_number": "108245",
                            },
                            "certificate": None,
                        },
                    ],
                    "credits": {
                        "edges": [
                            {
                                "node": {
                                    "person": {"firstName": "Sacha", "lastName": "Guitry"},
                                    "position": {"name": "DIRECTOR"},
                                }
                            }
                        ]
                    },
                    "cast": {
                        "backlink": {
                            "url": "https://www.allocine.fr/film/fichefilm-131136/casting/",
                            "label": "Casting complet du film sur AlloCin\u00e9",
                        },
                        "edges": [
                            {"node": {"actor": {"firstName": "Sacha", "lastName": "Guitry"}, "role": "(doublage)"}},
                            {"node": {"actor": {"firstName": "Sarah", "lastName": "Bernhardt"}, "role": None}},
                            {"node": {"actor": {"firstName": "Anatole", "lastName": "France"}, "role": None}},
                        ],
                    },
                    "countries": [{"name": "France", "alpha3": "FRA"}],
                    "genres": ["DOCUMENTARY"],
                    "companies": [
                        {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                        {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                    ],
                }
            },
            {
                "node": {
                    "id": "TW92aWU6NDEzMjQ=",
                    "internalId": 41324,
                    "backlink": {
                        "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=41324.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                    },
                    "data": {"eidr": "10.5240/205D-17AD-BBB2-F62A-2481-7", "productionYear": 1931},
                    "title": "The Front page",
                    "originalTitle": "The Front page",
                    "type": "FEATURE_FILM",
                    "runtime": "PT1H41M0S",
                    "poster": {"url": "https://fr.web.img4.acsta.net/pictures/17/12/21/10/23/2878333.jpg"},
                    "synopsis": "Un journaliste s'appr\u00eate \u00e0 se marier, lorsqu'il est envoy\u00e9 de toute urgence sur un scoop: l'ex\u00e9cution d'un homme accus\u00e9 d'avoir tu\u00e9 un policier. Mais ce dernier s'\u00e9vade.",
                    "releases": [
                        {
                            "name": "ReRelease",
                            "releaseDate": {"date": "2024-10-16"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [408737]"}
                            },
                            "certificate": None,
                        },
                        {
                            "name": "Released",
                            "releaseDate": {"date": "1931-09-25"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [278514]"}
                            },
                            "certificate": None,
                        },
                    ],
                    "credits": {
                        "edges": [
                            {
                                "node": {
                                    "person": {"firstName": "Lewis", "lastName": "Milestone"},
                                    "position": {"name": "DIRECTOR"},
                                }
                            }
                        ]
                    },
                    "cast": {
                        "backlink": {
                            "url": "https://www.allocine.fr/film/fichefilm-41324/casting/",
                            "label": "Casting complet du film sur AlloCin\u00e9",
                        },
                        "edges": [
                            {"node": {"actor": {"firstName": "Adolphe", "lastName": "Menjou"}, "role": "Walter Burns"}},
                            {"node": {"actor": {"firstName": "Pat", "lastName": "O'Brien"}, "role": "Hildy Johnson"}},
                            {"node": {"actor": {"firstName": "Mary", "lastName": "Brian"}, "role": "Peggy Grant"}},
                        ],
                    },
                    "countries": [{"name": "USA", "alpha3": "USA"}],
                    "genres": ["COMEDY"],
                    "companies": [
                        {"activity": "InternationalDistributionExports", "company": {"name": "United Artists"}},
                        {"activity": "Distribution", "company": {"name": "Swashbuckler Films"}},
                        {"activity": "Distribution", "company": {"name": "Swashbuckler Films"}},
                        {"activity": "Production", "company": {"name": "The Caddo company"}},
                    ],
                }
            },
        ],
    }
}

ALLOCINE_MOVIE_LIST_PAGE_1_UPDATED = copy.deepcopy(ALLOCINE_MOVIE_LIST_PAGE_1)
ALLOCINE_MOVIE_LIST_PAGE_1_UPDATED["movieList"]["edges"][0]["node"]["title"] = "Nouveau titre pour ceux de chez nous"

ALLOCINE_MOVIE_LIST_PAGE_2 = {
    "movieList": {
        "totalCount": 4,
        "pageInfo": {"hasNextPage": False, "endCursor": "YXJyYXljb25uZWN0aW9uOjQ6"},
        "edges": [
            {
                "node": {
                    "id": "TW92aWU6MjE2MQ==",
                    "internalId": 2161,
                    "backlink": {
                        "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=2161.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                    },
                    "data": {"eidr": "10.5240/9CAE-7D43-D0DE-4CCA-B4BE-V", "productionYear": 1935},
                    "title": "Les 39 marches",
                    "originalTitle": "The 39 Steps",
                    "type": "FEATURE_FILM",
                    "runtime": "PT1H21M0S",
                    "poster": {"url": "https://fr.web.img5.acsta.net/medias/nmedia/18/65/53/86/19271340.jpg"},
                    "synopsis": "Canadien install\u00e9 \u00e0 Londres, Richard Hannay assiste \u00e0 un spectacle de music-hall lorsqu\u2019un coup de feu provoque une panique g\u00e9n\u00e9rale. La jeune femme qui l\u2019a d\u00e9clench\u00e9e, Annabella Smith, le supplie de l\u2019h\u00e9berger. Elle se dit espionne, pourchass\u00e9e par une myst\u00e9rieuse organisation : les \u00ab 39 marches \u00bb. Au milieu de la nuit, Annabella se fait assassiner mais parvient \u00e0 avertir de justesse Hannay de fuir chercher la v\u00e9rit\u00e9 en \u00c9cosse. Le jeune homme entreprend alors un voyage \u00e0 la recherche d\u2019un homme \u00e0 qui il manque une phalange...",
                    "releases": [
                        {
                            "name": "ReRelease",
                            "releaseDate": {"date": "2023-11-29"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [12619]"},
                                "visa_number": "11533",
                            },
                            "certificate": None,
                        },
                        {
                            "name": "Released",
                            "releaseDate": {"date": "1935-10-30"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [12620]"},
                                "visa_number": "11533",
                            },
                            "certificate": None,
                        },
                    ],
                    "credits": {
                        "edges": [
                            {
                                "node": {
                                    "person": {"firstName": "Alfred", "lastName": "Hitchcock"},
                                    "position": {"name": "DIRECTOR"},
                                }
                            }
                        ]
                    },
                    "cast": {
                        "backlink": {
                            "url": "https://www.allocine.fr/film/fichefilm-2161/casting/",
                            "label": "Casting complet du film sur AlloCin\u00e9",
                        },
                        "edges": [
                            {"node": {"actor": {"firstName": "Robert", "lastName": "Donat"}, "role": "Richard Hannay"}},
                            {"node": {"actor": {"firstName": "Madeleine", "lastName": "Carroll"}, "role": "Pamela"}},
                            {
                                "node": {
                                    "actor": {"firstName": "Lucie", "lastName": "Mannheim"},
                                    "role": "Annabella Smith",
                                }
                            },
                        ],
                    },
                    "countries": [{"name": "United Kingdom", "alpha3": "GBR"}],
                    "genres": ["DETECTIVE", "COMEDY", "SPY", "THRILLER"],
                    "companies": [
                        {"activity": "Distribution", "company": {"name": "Carlotta Films"}},
                        {"activity": "Distribution", "company": {"name": "Carlotta Films"}},
                        {"activity": "Production", "company": {"name": "Gaumont British Picture Corporation Ltd."}},
                    ],
                }
            },
            {
                "node": {
                    "id": "TW92aWU6NDA3Ng==",
                    "internalId": 4076,
                    "backlink": {
                        "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=4076.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                    },
                    "data": {"eidr": "10.5240/76FD-43FF-DB1D-F072-A9AD-9", "productionYear": 1936},
                    "title": "Le Roman d'un tricheur",
                    "originalTitle": "Le Roman d'un tricheur",
                    "type": "FEATURE_FILM",
                    "runtime": "PT1H20M0S",
                    "poster": {"url": "https://fr.web.img3.acsta.net/pictures/23/10/09/17/02/1997806.jpg"},
                    "synopsis": "Depuis son enfance, un homme n'a qu'une seule ambition, devenir riche. Pour cela, il d\u00e9cide de devenir tricheur et voleur professionnel.",
                    "releases": [
                        {
                            "name": "ReRelease",
                            "releaseDate": {"date": "2023-11-01"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [411396]"},
                                "visa_number": "2004",
                            },
                            "certificate": None,
                        },
                        {
                            "name": "Released",
                            "releaseDate": {"date": "1936-09-18"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [14292]"},
                                "visa_number": "2004",
                            },
                            "certificate": None,
                        },
                    ],
                    "credits": {
                        "edges": [
                            {
                                "node": {
                                    "person": {"firstName": "Sacha", "lastName": "Guitry"},
                                    "position": {"name": "DIRECTOR"},
                                }
                            }
                        ]
                    },
                    "cast": {
                        "backlink": {
                            "url": "https://www.allocine.fr/film/fichefilm-4076/casting/",
                            "label": "Casting complet du film sur AlloCin\u00e9",
                        },
                        "edges": [
                            {"node": {"actor": {"firstName": "Sacha", "lastName": "Guitry"}, "role": "le tricheur"}},
                            {
                                "node": {
                                    "actor": {"firstName": "Marguerite", "lastName": "Moreno"},
                                    "role": "l'aventuri\u00e8re",
                                }
                            },
                            {"node": {"actor": {"firstName": "Jacqueline", "lastName": "Delubac"}, "role": "la femme"}},
                        ],
                    },
                    "countries": [{"name": "France", "alpha3": "FRA"}],
                    "genres": ["COMEDY"],
                    "companies": [
                        {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                        {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                        {"activity": "Production", "company": {"name": "Cineas"}},
                    ],
                }
            },
        ],
    }
}
