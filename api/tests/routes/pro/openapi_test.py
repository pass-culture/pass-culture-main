def test_public_api(client, app):
    response = client.get("/v2/openapi.json")
    assert response.status_code == 200
    assert response.json == {
        "components": {
            "schemas": {
                "BookingFormula": {
                    "description": "An enumeration.",
                    "enum": ["PLACE", "ABO"],
                    "title": "BookingFormula",
                },
                "BookingOfferType": {
                    "description": "An enumeration.",
                    "enum": ["BIEN", "EVENEMENT"],
                    "title": "BookingOfferType",
                },
                "CollectiveOffersCategoryResponseModel": {
                    "properties": {
                        "id": {"title": "Id", "type": "string"},
                        "name": {"title": "Name", "type": "string"},
                    },
                    "required": ["id", "name"],
                    "title": "CollectiveOffersCategoryResponseModel",
                    "type": "object",
                },
                "CollectiveOffersDomainResponseModel": {
                    "properties": {
                        "id": {"title": "Id", "type": "integer"},
                        "name": {"title": "Name", "type": "string"},
                    },
                    "required": ["id", "name"],
                    "title": "CollectiveOffersDomainResponseModel",
                    "type": "object",
                },
                "CollectiveOffersListCategoriesResponseModel": {
                    "items": {"$ref": "#/components/schemas/CollectiveOffersCategoryResponseModel"},
                    "title": "CollectiveOffersListCategoriesResponseModel",
                    "type": "array",
                },
                "CollectiveOffersListDomainsResponseModel": {
                    "items": {"$ref": "#/components/schemas/CollectiveOffersDomainResponseModel"},
                    "title": "CollectiveOffersListDomainsResponseModel",
                    "type": "array",
                },
                "CollectiveOffersListStudentLevelsResponseModel": {
                    "items": {"$ref": "#/components/schemas/CollectiveOffersStudentLevelResponseModel"},
                    "title": "CollectiveOffersListStudentLevelsResponseModel",
                    "type": "array",
                },
                "CollectiveOffersListVenuesResponseModel": {
                    "items": {"$ref": "#/components/schemas/CollectiveOffersVenueResponseModel"},
                    "title": "CollectiveOffersListVenuesResponseModel",
                    "type": "array",
                },
                "CollectiveOffersStudentLevelResponseModel": {
                    "properties": {
                        "id": {"title": "Id", "type": "string"},
                        "name": {"title": "Name", "type": "string"},
                    },
                    "required": ["id", "name"],
                    "title": "CollectiveOffersStudentLevelResponseModel",
                    "type": "object",
                },
                "CollectiveOffersVenueResponseModel": {
                    "properties": {
                        "address": {"nullable": True, "title": "Address", "type": "string"},
                        "city": {"nullable": True, "title": "City", "type": "string"},
                        "id": {"title": "Id", "type": "integer"},
                        "name": {"title": "Name", "type": "string"},
                        "postalCode": {"nullable": True, "title": "Postalcode", "type": "string"},
                    },
                    "required": ["id", "name"],
                    "title": "CollectiveOffersVenueResponseModel",
                    "type": "object",
                },
                "ValidationError": {
                    "description": "Model " "of a " "validation " "error " "response.",
                    "items": {"$ref": "#/components/schemas/ValidationErrorElement"},
                    "title": "ValidationError",
                    "type": "array",
                },
                "ValidationErrorElement": {
                    "description": "Model " "of " "a " "validation " "error " "response " "element.",
                    "properties": {
                        "ctx": {"title": "Error " "context", "type": "object"},
                        "loc": {"items": {"type": "string"}, "title": "Missing " "field " "name", "type": "array"},
                        "msg": {"title": "Error " "message", "type": "string"},
                        "type": {"title": "Error " "type", "type": "string"},
                    },
                    "required": ["loc", "msg", "type"],
                    "title": "ValidationErrorElement",
                    "type": "object",
                },
                "GetBookingResponse": {
                    "properties": {
                        "bookingId": {"title": "Bookingid", "type": "string"},
                        "dateOfBirth": {"title": "Dateofbirth", "type": "string"},
                        "datetime": {"title": "Datetime", "type": "string"},
                        "ean13": {"nullable": True, "title": "Ean13", "type": "string"},
                        "email": {"title": "Email", "type": "string"},
                        "formula": {"nullable": True, "anyOf": [{"$ref": "#/components/schemas/BookingFormula"}]},
                        "isUsed": {"title": "Isused", "type": "boolean"},
                        "offerId": {"title": "Offerid", "type": "integer"},
                        "offerName": {"title": "Offername", "type": "string"},
                        "offerType": {"$ref": "#/components/schemas/BookingOfferType"},
                        "phoneNumber": {"title": "Phonenumber", "type": "string"},
                        "price": {"title": "Price", "type": "number"},
                        "publicOfferId": {"title": "Publicofferid", "type": "string"},
                        "quantity": {"title": "Quantity", "type": "integer"},
                        "theater": {"title": "Theater", "type": "object"},
                        "userName": {"title": "Username", "type": "string"},
                        "venueAddress": {"nullable": True, "title": "Venueaddress", "type": "string"},
                        "venueDepartmentCode": {"nullable": True, "title": "Venuedepartmentcode", "type": "string"},
                        "venueName": {"title": "Venuename", "type": "string"},
                    },
                    "required": [
                        "bookingId",
                        "dateOfBirth",
                        "datetime",
                        "email",
                        "isUsed",
                        "offerId",
                        "publicOfferId",
                        "offerName",
                        "offerType",
                        "phoneNumber",
                        "price",
                        "quantity",
                        "theater",
                        "userName",
                        "venueName",
                    ],
                    "title": "GetBookingResponse",
                    "type": "object",
                },
                "UpdateVenueStockBodyModel": {
                    "description": "Available stock quantity for a book",
                    "properties": {
                        "available": {"minimum": 0, "title": "Available", "type": "integer"},
                        "price": {
                            "description": "(Optionnel) Prix en Euros avec 2 décimales possibles",
                            "title": "Price",
                            "nullable": True,
                            "type": "number",
                        },
                        "ref": {"description": "Format: EAN13", "title": "ISBN", "type": "string"},
                    },
                    "required": ["ref", "available"],
                    "title": "Stock",
                    "type": "object",
                },
                "UpdateVenueStocksBodyModel": {
                    "properties": {
                        "stocks": {
                            "items": {"$ref": "#/components/schemas/UpdateVenueStockBodyModel"},
                            "title": "Stocks",
                            "type": "array",
                        }
                    },
                    "required": ["stocks"],
                    "title": "Venue's stocks update body",
                    "type": "object",
                },
            },
            "securitySchemes": {
                "ApiKeyAuth": {"description": "Api key issued by passculture", "scheme": "bearer", "type": "http"},
                "SessionAuth": {
                    "in": "cookie",
                    "name": "session",
                    "type": "apiKey",
                },
            },
        },
        "info": {"title": "pass Culture pro public API v2", "version": "2"},
        "openapi": "3.0.3",
        "paths": {
            "/v2/bookings/cancel/token/{token}": {
                "patch": {
                    "description": "Bien que, dans le cas d’un événement, l\u2019utilisateur ne peut plus annuler sa réservation 72h avant le début de ce dernier, cette API permet d\u2019annuler la réservation d\u2019un utilisateur si elle n\u2019a pas encore été validé.",
                    "operationId": "PatchCancelBookingByToken",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "token",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "204": {"description": "La contremarque a été annulée avec succès"},
                        "401": {"description": "Authentification nécessaire"},
                        "403": {
                            "description": "Vous n'avez pas les droits nécessaires pour annuler cette contremarque ou la réservation a déjà été validée"
                        },
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {"description": "La contremarque a déjà été annulée"},
                        "422": {
                            "description": "Unprocessable Entity",
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                        },
                    },
                    "summary": "Annulation d'une réservation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/bookings/keep/token/{token}": {
                "patch": {
                    "description": "",
                    "operationId": "PatchBookingKeepByToken",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "token",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "204": {"description": "L'annulation de la validation de la contremarque a bien été effectuée"},
                        "401": {"description": "Authentification nécessaire"},
                        "403": {"description": "Vous n'avez pas les droits nécessaires pour voir cette contremarque"},
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {
                            "description": "La requête est refusée car la contremarque n'a pas encore été validée, a été annulée, ou son remboursement a été initié"
                        },
                        "422": {
                            "description": "Unprocessable Entity",
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                        },
                    },
                    "summary": "Annulation de la validation d'une réservation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/bookings/token/{token}": {
                "get": {
                    "description": "Le code \u201ccontremarque\u201d ou \"token\" est une cha\u00eene de caractères permettant d\u2019identifier la réservation et qui sert de preuve de réservation. Ce code unique est généré pour chaque réservation d'un utilisateur sur l'application et lui est transmis à cette occasion.",
                    "operationId": "GetBookingByTokenV2",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "token",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/GetBookingResponse"}}
                            },
                            "description": "La contremarque existe et n\u2019est pas validée",
                        },
                        "401": {"description": "Authentification nécessaire"},
                        "403": {"description": "Vous n'avez pas les droits nécessaires pour voir cette contremarque"},
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {
                            "description": "La contremarque n'est plus valide car elle a déjà été validée ou a été annulée"
                        },
                        "422": {
                            "description": "Unprocessable Entity",
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                        },
                    },
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
                    "summary": "Consultation d'une réservation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/bookings/use/token/{token}": {
                "patch": {
                    "description": "Pour confirmer que la réservation a bien été utilisée par le jeune.",
                    "operationId": "PatchBookingUseByToken",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "token",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "204": {"description": "La contremarque a bien été validée"},
                        "401": {"description": "Authentification nécessaire"},
                        "403": {"description": "Vous n'avez pas les droits nécessaires pour voir cette contremarque"},
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {
                            "description": "La contremarque n'est plus valide car elle a déjà été validée ou a été annulée"
                        },
                        "422": {
                            "description": "Unprocessable Entity",
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                        },
                    },
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
                    "summary": "Validation d'une réservation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/collective-offers/categories": {
                "get": {
                    "description": "",
                    "operationId": "ListCategories",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CollectiveOffersListCategoriesResponseModel"
                                    }
                                }
                            },
                            "description": "OK",
                        },
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable " "Entity",
                        },
                    },
                    "summary": "Récupération de la liste des catégories d'offres proposées.",
                    "tags": [],
                }
            },
            "/v2/collective-offers/educational-domains": {
                "get": {
                    "description": "",
                    "operationId": "ListEducationalDomains",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CollectiveOffersListDomainsResponseModel"}
                                }
                            },
                            "description": "OK",
                        },
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable " "Entity",
                        },
                    },
                    "summary": "Récupération de la liste des domaines d'éducation pouvant être associés aux offres collectives.",
                    "tags": [],
                }
            },
            "/v2/collective-offers/student-levels": {
                "get": {
                    "description": "",
                    "operationId": "ListStudentsLevels",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CollectiveOffersListStudentLevelsResponseModel"
                                    }
                                }
                            },
                            "description": "OK",
                        },
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable " "Entity",
                        },
                    },
                    "summary": "Récupération de la liste des publics cibles pour lesquelles des offres collectives peuvent être proposées.",
                    "tags": [],
                }
            },
            "/v2/collective-offers/venues": {
                "get": {
                    "description": "Tous les "
                    "lieux "
                    "enregistrés, "
                    "physiques "
                    "ou "
                    "virtuels, "
                    "sont "
                    "listés ici "
                    "avec leurs "
                    "coordonnées.",
                    "operationId": "ListVenues",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CollectiveOffersListVenuesResponseModel"}
                                }
                            },
                            "description": "OK",
                        },
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable " "Entity",
                        },
                    },
                    "summary": "Récupération "
                    "de la liste "
                    "des lieux "
                    "associés à la "
                    "structure "
                    "authentifiée "
                    "par le jeton "
                    "d'API.",
                    "tags": [],
                }
            },
            "/v2/venue/{venue_id}/stocks": {
                "post": {
                    "description": """Seuls les livres, préalablement présents dans le catalogue du pass Culture seront pris en compte, tous les autres stocks seront filtrés. Les stocks sont référencés par leur isbn au format EAN13. Le champ "available" représente la quantité de stocks disponible en librairie. Le champ "price" (optionnel) correspond au prix en euros. Le paramètre {venue_id} correspond à un lieu qui doit être attaché à la structure à laquelle la clé d'API utilisée est reliée.""",
                    "operationId": "UpdateStocks",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "venue_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/UpdateVenueStocksBodyModel"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not Found"},
                        "422": {
                            "description": "Unprocessable Entity",
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                        },
                    },
                    "summary": "Mise à jour des stocks d'un lieu enregistré auprès du pass Culture.",
                    "tags": ["API Stocks"],
                }
            },
        },
        "security": [],
        "tags": [{"name": "API Contremarque"}, {"name": "API Stocks"}],
    }
