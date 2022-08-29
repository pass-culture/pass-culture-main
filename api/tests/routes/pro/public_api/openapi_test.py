def test_public_api(client, app):
    response = client.get("/v2/openapi.json")
    assert response.status_code == 200
    assert response.json == {
        "components": {
            "schemas": {
                "AuthErrorResponseModel": {
                    "properties": {
                        "errors": {"additionalProperties": {"type": "string"}, "title": "Errors", "type": "object"}
                    },
                    "required": ["errors"],
                    "title": "AuthErrorResponseModel",
                    "type": "object",
                },
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
                "CollectiveOffersEducationalInstitutionResponseModel": {
                    "properties": {
                        "city": {"title": "City", "type": "string"},
                        "id": {"title": "Id", "type": "integer"},
                        "institutionType": {"title": "Institutiontype", "type": "string"},
                        "name": {"title": "Name", "type": "string"},
                        "postalCode": {"title": "Postalcode", "type": "string"},
                    },
                    "required": ["id", "name", "institutionType", "city", "postalCode"],
                    "title": "CollectiveOffersEducationalInstitutionResponseModel",
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
                "CollectiveOffersListEducationalInstitutionResponseModel": {
                    "items": {"$ref": "#/components/schemas/CollectiveOffersEducationalInstitutionResponseModel"},
                    "title": "CollectiveOffersListEducationalInstitutionResponseModel",
                    "type": "array",
                },
                "CollectiveOffersListResponseModel": {
                    "items": {"$ref": "#/components/schemas/CollectiveOffersResponseModel"},
                    "title": "CollectiveOffersListResponseModel",
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
                "CollectiveOffersResponseModel": {
                    "properties": {
                        "beginningDatetime": {"title": "Beginningdatetime", "type": "string"},
                        "id": {"title": "Id", "type": "integer"},
                        "status": {"title": "Status", "type": "string"},
                        "venueId": {"title": "Venueid", "type": "integer"},
                    },
                    "required": ["id", "beginningDatetime", "status", "venueId"],
                    "title": "CollectiveOffersResponseModel",
                    "type": "object",
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
                "ErrorResponseModel": {
                    "properties": {
                        "errors": {
                            "additionalProperties": {"items": {"type": "string"}, "type": "array"},
                            "title": "Errors",
                            "type": "object",
                        }
                    },
                    "required": ["errors"],
                    "title": "ErrorResponseModel",
                    "type": "object",
                },
                "GetBookingResponse": {
                    "properties": {
                        "bookingId": {"title": "Bookingid", "type": "string"},
                        "dateOfBirth": {"title": "Dateofbirth", "type": "string"},
                        "datetime": {"title": "Datetime", "type": "string"},
                        "ean13": {"nullable": True, "title": "Ean13", "type": "string"},
                        "email": {"title": "Email", "type": "string"},
                        "formula": {"anyOf": [{"$ref": "#/components/schemas/BookingFormula"}], "nullable": True},
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
                "GetListEducationalInstitutionsQueryModel": {
                    "additionalProperties": False,
                    "properties": {
                        "city": {"nullable": True, "title": "City", "type": "string"},
                        "id": {"nullable": True, "title": "Id", "type": "integer"},
                        "institutionType": {"nullable": True, "title": "Institutiontype", "type": "string"},
                        "limit": {"default": 20, "title": "Limit", "type": "integer"},
                        "name": {"nullable": True, "title": "Name", "type": "string"},
                        "postalCode": {"nullable": True, "title": "Postalcode", "type": "string"},
                    },
                    "title": "GetListEducationalInstitutionsQueryModel",
                    "type": "object",
                },
                "GetPublicCollectiveOfferResponseModel": {
                    "additionalProperties": False,
                    "properties": {
                        "audioDisabilityCompliant": {
                            "nullable": True,
                            "title": "Audiodisabilitycompliant",
                            "type": "boolean",
                        },
                        "beginningDatetime": {"title": "Beginningdatetime", "type": "string"},
                        "bookingEmail": {"nullable": True, "title": "Bookingemail", "type": "string"},
                        "bookingLimitDatetime": {"title": "Bookinglimitdatetime", "type": "string"},
                        "contactEmail": {"title": "Contactemail", "type": "string"},
                        "contactPhone": {"title": "Contactphone", "type": "string"},
                        "dateCreated": {"title": "Datecreated", "type": "string"},
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "domains": {"items": {"type": "string"}, "title": "Domains", "type": "array"},
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "educationalInstitution": {
                            "nullable": True,
                            "title": "Educationalinstitution",
                            "type": "string",
                        },
                        "educationalPriceDetail": {
                            "nullable": True,
                            "title": "Educationalpricedetail",
                            "type": "string",
                        },
                        "hasBookingLimitDatetimesPassed": {
                            "title": "Hasbookinglimitdatetimespassed",
                            "type": "boolean",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "interventionArea": {"items": {"type": "string"}, "title": "Interventionarea", "type": "array"},
                        "isActive": {"nullable": True, "title": "Isactive", "type": "boolean"},
                        "isSoldOut": {"title": "Issoldout", "type": "boolean"},
                        "mentalDisabilityCompliant": {
                            "nullable": True,
                            "title": "Mentaldisabilitycompliant",
                            "type": "boolean",
                        },
                        "motorDisabilityCompliant": {
                            "nullable": True,
                            "title": "Motordisabilitycompliant",
                            "type": "boolean",
                        },
                        "name": {"title": "Name", "type": "string"},
                        "numberOfTickets": {"title": "Numberoftickets", "type": "integer"},
                        "offerVenue": {"$ref": "#/components/schemas/OfferVenueModel"},
                        "status": {"title": "Status", "type": "string"},
                        "students": {"items": {"type": "string"}, "title": "Students", "type": "array"},
                        "subcategoryId": {"title": "Subcategoryid", "type": "string"},
                        "totalPrice": {"title": "Totalprice", "type": "integer"},
                        "venueId": {"title": "Venueid", "type": "integer"},
                        "visualDisabilityCompliant": {
                            "nullable": True,
                            "title": "Visualdisabilitycompliant",
                            "type": "boolean",
                        },
                    },
                    "required": [
                        "id",
                        "status",
                        "name",
                        "subcategoryId",
                        "contactEmail",
                        "contactPhone",
                        "domains",
                        "interventionArea",
                        "students",
                        "dateCreated",
                        "hasBookingLimitDatetimesPassed",
                        "isSoldOut",
                        "venueId",
                        "beginningDatetime",
                        "bookingLimitDatetime",
                        "totalPrice",
                        "numberOfTickets",
                        "offerVenue",
                    ],
                    "title": "GetPublicCollectiveOfferResponseModel",
                    "type": "object",
                },
                "ListCollectiveOffersQueryModel": {
                    "additionalProperties": False,
                    "properties": {
                        "periodBeginningDate": {"nullable": True, "title": "Periodbeginningdate", "type": "string"},
                        "periodEndingDate": {"nullable": True, "title": "Periodendingdate", "type": "string"},
                        "status": {"anyOf": [{"$ref": "#/components/schemas/OfferStatus"}], "nullable": True},
                        "venueId": {"nullable": True, "title": "Venueid", "type": "integer"},
                    },
                    "title": "ListCollectiveOffersQueryModel",
                    "type": "object",
                },
                "OfferAddressType": {
                    "description": "An enumeration.",
                    "enum": ["offererVenue", "school", "other"],
                    "title": "OfferAddressType",
                },
                "OfferStatus": {
                    "description": "An enumeration.",
                    "enum": ["ACTIVE", "PENDING", "EXPIRED", "REJECTED", "SOLD_OUT", "INACTIVE", "DRAFT"],
                    "title": "OfferStatus",
                },
                "OfferVenueModel": {
                    "additionalProperties": False,
                    "properties": {
                        "addressType": {"$ref": "#/components/schemas/OfferAddressType"},
                        "otherAddress": {"nullable": True, "title": "Otheraddress", "type": "string"},
                        "venueId": {"nullable": True, "title": "Venueid", "type": "integer"},
                    },
                    "required": ["addressType"],
                    "title": "OfferVenueModel",
                    "type": "object",
                },
                "PatchCollectiveOfferBodyModel": {
                    "additionalProperties": False,
                    "properties": {
                        "beginningDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Beginningdatetime",
                            "type": "string",
                        },
                        "bookingEmail": {"nullable": True, "title": "Bookingemail", "type": "string"},
                        "bookingLimitDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Bookinglimitdatetime",
                            "type": "string",
                        },
                        "contactEmail": {"nullable": True, "title": "Contactemail", "type": "string"},
                        "contactPhone": {"nullable": True, "title": "Contactphone", "type": "string"},
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "domains": {"items": {"type": "string"}, "nullable": True, "title": "Domains", "type": "array"},
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "educationalInstitutionId": {
                            "nullable": True,
                            "title": "Educationalinstitutionid",
                            "type": "integer",
                        },
                        "educationalPriceDetail": {
                            "nullable": True,
                            "title": "Educationalpricedetail",
                            "type": "string",
                        },
                        "interventionArea": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Interventionarea",
                            "type": "array",
                        },
                        "name": {"nullable": True, "title": "Name", "type": "string"},
                        "numberOfTickets": {"nullable": True, "title": "Numberoftickets", "type": "integer"},
                        "offerVenue": {
                            "anyOf": [{"$ref": "#/components/schemas/OfferVenueModel"}],
                            "nullable": True,
                            "title": "OfferVenueModel",
                        },
                        "priceDetail": {"nullable": True, "title": "Pricedetail", "type": "string"},
                        "students": {
                            "items": {"$ref": "#/components/schemas/StudentLevels"},
                            "nullable": True,
                            "type": "array",
                        },
                        "subcategoryId": {"nullable": True, "title": "Subcategoryid", "type": "string"},
                        "totalPrice": {"nullable": True, "title": "Totalprice", "type": "number"},
                    },
                    "title": "PatchCollectiveOfferBodyModel",
                    "type": "object",
                },
                "PostCollectiveOfferBodyModel": {
                    "additionalProperties": False,
                    "properties": {
                        "audioDisabilityCompliant": {
                            "default": False,
                            "title": "Audiodisabilitycompliant",
                            "type": "boolean",
                        },
                        "beginningDatetime": {"format": "date-time", "title": "Beginningdatetime", "type": "string"},
                        "bookingEmail": {"nullable": True, "title": "Bookingemail", "type": "string"},
                        "bookingLimitDatetime": {
                            "format": "date-time",
                            "title": "Bookinglimitdatetime",
                            "type": "string",
                        },
                        "contactEmail": {"title": "Contactemail", "type": "string"},
                        "contactPhone": {"title": "Contactphone", "type": "string"},
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "domains": {"items": {"type": "string"}, "title": "Domains", "type": "array"},
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "educationalInstitutionId": {
                            "nullable": True,
                            "title": "Educationalinstitutionid",
                            "type": "integer",
                        },
                        "interventionArea": {"items": {"type": "string"}, "title": "Interventionarea", "type": "array"},
                        "mentalDisabilityCompliant": {
                            "default": False,
                            "title": "Mentaldisabilitycompliant",
                            "type": "boolean",
                        },
                        "motorDisabilityCompliant": {
                            "default": False,
                            "title": "Motordisabilitycompliant",
                            "type": "boolean",
                        },
                        "name": {"title": "Name", "type": "string"},
                        "numberOfTickets": {"title": "Numberoftickets", "type": "integer"},
                        "offerVenue": {"$ref": "#/components/schemas/OfferVenueModel"},
                        "priceDetail": {"nullable": True, "title": "Pricedetail", "type": "string"},
                        "students": {"items": {"$ref": "#/components/schemas/StudentLevels"}, "type": "array"},
                        "subcategoryId": {"title": "Subcategoryid", "type": "string"},
                        "totalPrice": {"title": "Totalprice", "type": "integer"},
                        "venueId": {"title": "Venueid", "type": "integer"},
                        "visualDisabilityCompliant": {
                            "default": False,
                            "title": "Visualdisabilitycompliant",
                            "type": "boolean",
                        },
                    },
                    "required": [
                        "venueId",
                        "name",
                        "subcategoryId",
                        "contactEmail",
                        "contactPhone",
                        "domains",
                        "students",
                        "offerVenue",
                        "interventionArea",
                        "beginningDatetime",
                        "bookingLimitDatetime",
                        "totalPrice",
                        "numberOfTickets",
                    ],
                    "title": "PostCollectiveOfferBodyModel",
                    "type": "object",
                },
                "StudentLevels": {
                    "description": "An enumeration.",
                    "enum": [
                        "Collège - 4e",
                        "Collège - 3e",
                        "CAP - 1re année",
                        "CAP - 2e année",
                        "Lycée - Seconde",
                        "Lycée - Première",
                        "Lycée - Terminale",
                    ],
                    "title": "StudentLevels",
                },
                "UpdateVenueStockBodyModel": {
                    "description": "Available stock quantity for a book",
                    "properties": {
                        "available": {"minimum": 0, "title": "Available", "type": "integer"},
                        "price": {
                            "description": "(Optionnel) Prix en Euros avec 2 décimales possibles",
                            "nullable": True,
                            "title": "Price",
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
                "ValidationError": {
                    "description": "Model of a validation error response.",
                    "items": {"$ref": "#/components/schemas/ValidationErrorElement"},
                    "title": "ValidationError",
                    "type": "array",
                },
                "ValidationErrorElement": {
                    "description": "Model of a validation error response element.",
                    "properties": {
                        "ctx": {"title": "Error context", "type": "object"},
                        "loc": {"items": {"type": "string"}, "title": "Missing field name", "type": "array"},
                        "msg": {"title": "Error message", "type": "string"},
                        "type": {"title": "Error type", "type": "string"},
                    },
                    "required": ["loc", "msg", "type"],
                    "title": "ValidationErrorElement",
                    "type": "object",
                },
            },
            "securitySchemes": {
                "ApiKeyAuth": {"description": "Api key issued by passculture", "scheme": "bearer", "type": "http"},
                "SessionAuth": {"in": "cookie", "name": "session", "type": "apiKey"},
            },
        },
        "info": {"title": "pass Culture pro public API v2", "version": "2"},
        "openapi": "3.0.3",
        "paths": {
            "/v2/bookings/cancel/token/{token}": {
                "patch": {
                    "description": "Bien que, dans le cas d’un événement, l’utilisateur ne peut plus annuler sa réservation 72h avant le début de ce dernier, cette API permet d’annuler la réservation d’un utilisateur si elle n’a pas encore été validé.",
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
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
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
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Annulation de la validation d'une réservation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/bookings/token/{token}": {
                "get": {
                    "description": "Le code “contremarque” ou \"token\" est une chaîne de caractères permettant d’identifier la réservation et qui sert de preuve de réservation. Ce code unique est généré pour chaque réservation d'un utilisateur sur l'application et lui est transmis à cette occasion.",
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
                            "description": "La contremarque existe et n’est pas validée",
                        },
                        "401": {"description": "Authentification nécessaire"},
                        "403": {"description": "Vous n'avez pas les droits nécessaires pour voir cette contremarque"},
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {
                            "description": "La contremarque n'est plus valide car elle a déjà été validée ou a été annulée"
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
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
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
                    "summary": "Validation d'une réservation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/collective/categories": {
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
                            "description": "La liste des catégories éligibles existantes.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Récupération de la liste des catégories d'offres proposées.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/educational-domains": {
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
                            "description": "La liste des domaines d'éducation.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Récupération de la liste des domaines d'éducation pouvant être associés aux offres collectives.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/educational-institutions/": {
                "get": {
                    "description": "",
                    "operationId": "ListEducationalInstitutions",
                    "parameters": [
                        {
                            "description": "",
                            "in": "query",
                            "name": "id",
                            "required": False,
                            "schema": {"nullable": True, "title": "Id", "type": "integer"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "name",
                            "required": False,
                            "schema": {"nullable": True, "title": "Name", "type": "string"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "institutionType",
                            "required": False,
                            "schema": {"nullable": True, "title": "Institutiontype", "type": "string"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "city",
                            "required": False,
                            "schema": {"nullable": True, "title": "City", "type": "string"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "postalCode",
                            "required": False,
                            "schema": {"nullable": True, "title": "Postalcode", "type": "string"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "limit",
                            "required": False,
                            "schema": {"default": 20, "title": "Limit", "type": "integer"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CollectiveOffersListEducationalInstitutionResponseModel"
                                    }
                                }
                            },
                            "description": "La liste des établissement scolaires éligibles.",
                        },
                        "400": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Requête malformée",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Récupération de la liste établissements scolaires.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/offers/": {
                "get": {
                    "description": "",
                    "operationId": "GetCollectiveOffersPublic",
                    "parameters": [
                        {
                            "description": "",
                            "in": "query",
                            "name": "status",
                            "required": False,
                            "schema": {"anyOf": [{"$ref": "#/components/schemas/OfferStatus"}], "nullable": True},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "venueId",
                            "required": False,
                            "schema": {"nullable": True, "title": "Venueid", "type": "integer"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "periodBeginningDate",
                            "required": False,
                            "schema": {"nullable": True, "title": "Periodbeginningdate", "type": "string"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "periodEndingDate",
                            "required": False,
                            "schema": {"nullable": True, "title": "Periodendingdate", "type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CollectiveOffersListResponseModel"}
                                }
                            },
                            "description": "L'offre collective existe",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Vous n'avez pas les droits nécessaires pour voir cette offre collective",
                        },
                        "404": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "L'offre collective n'existe pas",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Récuperation de l'offre collective avec l'identifiant offer_id. Cette api ignore les offre vitrines et les offres commencées sur l'interface web et non finalisées.",
                    "tags": ["API offres collectives"],
                },
                "post": {
                    "description": "",
                    "operationId": "PostCollectiveOfferPublic",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PostCollectiveOfferBodyModel"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/GetPublicCollectiveOfferResponseModel"}
                                }
                            },
                            "description": "L'offre collective à été créée avec succes",
                        },
                        "400": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Requête malformée",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Non éligible pour les offres collectives",
                        },
                        "404": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "L'une des resources pour la création de l'offre n'a pas été trouvée",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Création d'une offre collective.",
                    "tags": ["API offres collectives"],
                },
            },
            "/v2/collective/offers/{offer_id}": {
                "get": {
                    "description": "",
                    "operationId": "GetCollectiveOfferPublic",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "offer_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/GetPublicCollectiveOfferResponseModel"}
                                }
                            },
                            "description": "L'offre collective existe",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Vous n'avez pas les droits nécessaires pour voir cette offre collective",
                        },
                        "404": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "L'offre collective n'existe pas",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Récuperation de l'offre collective avec l'identifiant offer_id.",
                    "tags": ["API offres collectives"],
                },
                "patch": {
                    "description": "",
                    "operationId": "PatchCollectiveOfferPublic",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "offer_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PatchCollectiveOfferBodyModel"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/GetPublicCollectiveOfferResponseModel"}
                                }
                            },
                            "description": "L'offre collective à été édité avec succes",
                        },
                        "400": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Requête malformée",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Vous n'avez pas les droits nécessaires pour éditer cette offre collective",
                        },
                        "404": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "L'une des resources pour la création de l'offre n'a pas été trouvée",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Cetains champs ne peuvent pas être édités selon l'état de l'offre",
                        },
                    },
                    "summary": "Édition d'une offre collective.",
                    "tags": ["API offres collectives"],
                },
            },
            "/v2/collective/student-levels": {
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
                            "description": "La liste des domaines d'éducation.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Récupération de la liste des publics cibles pour lesquelles des offres collectives peuvent être proposées.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/venues": {
                "get": {
                    "description": "Tous les lieux enregistrés, sont listés ici avec leurs coordonnées.",
                    "operationId": "ListVenues",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CollectiveOffersListVenuesResponseModel"}
                                }
                            },
                            "description": "La liste des lieux ou vous pouvez créer une offre.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification nécessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Récupération de la liste des lieux associés à la structure authentifiée par le jeton d'API.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/venue/{venue_id}/stocks": {
                "post": {
                    "description": 'Seuls les livres, préalablement présents dans le catalogue du pass Culture seront pris en compte, tous les autres stocks seront filtrés. Les stocks sont référencés par leur isbn au format EAN13. Le champ "available" représente la quantité de stocks disponible en librairie. Le champ "price" (optionnel) correspond au prix en euros. Le paramètre {venue_id} correspond à un lieu qui doit être attaché à la structure à laquelle la clé d\'API utilisée est reliée.',
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
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "Mise à jour des stocks d'un lieu enregistré auprès du pass Culture.",
                    "tags": ["API Stocks"],
                }
            },
        },
        "security": [],
        "tags": [{"name": "API offres collectives"}, {"name": "API Contremarque"}, {"name": "API Stocks"}],
    }
