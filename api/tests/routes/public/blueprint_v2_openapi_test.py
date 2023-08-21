from pcapi import settings


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
                    "type": "string",
                },
                "BookingOfferType": {
                    "description": "An enumeration.",
                    "enum": ["BIEN", "EVENEMENT"],
                    "title": "BookingOfferType",
                    "type": "string",
                },
                "CollectiveBookingResponseModel": {
                    "properties": {
                        "cancellationLimitDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Cancellationlimitdate",
                            "type": "string",
                        },
                        "confirmationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Confirmationdate",
                            "type": "string",
                        },
                        "dateCreated": {"format": "date-time", "title": "Datecreated", "type": "string"},
                        "dateUsed": {"format": "date-time", "nullable": True, "title": "Dateused", "type": "string"},
                        "educationalYear": {"$ref": "#/components/schemas/EducationalYearModel"},
                        "id": {"title": "Id", "type": "integer"},
                        "status": {"$ref": "#/components/schemas/CollectiveBookingStatus"},
                        "venueId": {"title": "Venueid", "type": "integer"},
                    },
                    "required": ["id", "status", "dateCreated", "educationalYear", "venueId"],
                    "title": "CollectiveBookingResponseModel",
                    "type": "object",
                },
                "CollectiveBookingStatus": {
                    "description": "An enumeration.",
                    "enum": ["PENDING", "CONFIRMED", "USED", "CANCELLED", "REIMBURSED"],
                    "title": "CollectiveBookingStatus",
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
                        "uai": {"title": "Uai", "type": "string"},
                    },
                    "required": ["id", "uai", "name", "institutionType", "city", "postalCode"],
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
                "CollectiveOffersListSubCategoriesResponseModel": {
                    "items": {"$ref": "#/components/schemas/CollectiveOffersSubCategoryResponseModel"},
                    "title": "CollectiveOffersListSubCategoriesResponseModel",
                    "type": "array",
                },
                "CollectiveOffersListVenuesResponseModel": {
                    "items": {"$ref": "#/components/schemas/VenueResponse"},
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
                "CollectiveOffersSubCategoryResponseModel": {
                    "properties": {
                        "category": {"title": "Category", "type": "string"},
                        "categoryId": {"title": "Categoryid", "type": "string"},
                        "id": {"title": "Id", "type": "string"},
                        "label": {"title": "Label", "type": "string"},
                    },
                    "required": ["id", "label", "category", "categoryId"],
                    "title": "CollectiveOffersSubCategoryResponseModel",
                    "type": "object",
                },
                "EducationalYearModel": {
                    "properties": {
                        "adageId": {"title": "Adageid", "type": "string"},
                        "beginningDate": {"format": "date-time", "title": "Beginningdate", "type": "string"},
                        "expirationDate": {"format": "date-time", "title": "Expirationdate", "type": "string"},
                    },
                    "required": ["adageId", "beginningDate", "expirationDate"],
                    "title": "EducationalYearModel",
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
                        "dateOfBirth": {"nullable": True, "title": "Dateofbirth", "type": "string"},
                        "datetime": {"title": "Datetime", "type": "string"},
                        "ean13": {"nullable": True, "title": "Ean13", "type": "string"},
                        "email": {"title": "Email", "type": "string"},
                        "formula": {
                            "allOf": [{"$ref": "#/components/schemas/BookingFormula"}],
                            "description": "S'applique uniquement aux offres de cat\u00e9gorie Cin\u00e9ma. Abonnement (ABO) ou place (PLACE).",
                            "nullable": True,
                        },
                        "isUsed": {"title": "Isused", "type": "boolean"},
                        "offerId": {"title": "Offerid", "type": "integer"},
                        "offerName": {"title": "Offername", "type": "string"},
                        "offerType": {"$ref": "#/components/schemas/BookingOfferType"},
                        "phoneNumber": {"nullable": True, "title": "Phonenumber", "type": "string"},
                        "price": {"title": "Price", "type": "number"},
                        "priceCategoryLabel": {"nullable": True, "title": "Pricecategorylabel", "type": "string"},
                        "publicOfferId": {"title": "Publicofferid", "type": "string"},
                        "quantity": {"title": "Quantity", "type": "integer"},
                        "theater": {
                            "description": "Identifiant du film et de la salle dans le cas d\u2019une offre synchronis\u00e9e par Allocin\u00e9.",
                            "example": {"film_id": "...", "salle_id": "..."},
                            "title": "Theater",
                            "type": "object",
                        },
                        "userName": {"title": "Username", "type": "string"},
                        "venueAddress": {"nullable": True, "title": "Venueaddress", "type": "string"},
                        "venueDepartmentCode": {"nullable": True, "title": "Venuedepartmentcode", "type": "string"},
                        "venueName": {"title": "Venuename", "type": "string"},
                    },
                    "required": [
                        "bookingId",
                        "datetime",
                        "email",
                        "isUsed",
                        "offerId",
                        "publicOfferId",
                        "offerName",
                        "offerType",
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
                        "uai": {"nullable": True, "title": "Uai", "type": "string"},
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
                        "bookingEmails": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Bookingemails",
                            "type": "array",
                        },
                        "bookingLimitDatetime": {"title": "Bookinglimitdatetime", "type": "string"},
                        "contactEmail": {"title": "Contactemail", "type": "string"},
                        "contactPhone": {"title": "Contactphone", "type": "string"},
                        "dateCreated": {"title": "Datecreated", "type": "string"},
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "domains": {"items": {"type": "integer"}, "title": "Domains", "type": "array"},
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "educationalInstitution": {
                            "nullable": True,
                            "title": "Educationalinstitution",
                            "type": "string",
                        },
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
                        "hasBookingLimitDatetimesPassed": {
                            "title": "Hasbookinglimitdatetimespassed",
                            "type": "boolean",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "imageCredit": {"nullable": True, "title": "Imagecredit", "type": "string"},
                        "imageUrl": {"nullable": True, "title": "Imageurl", "type": "string"},
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
                        "totalPrice": {"title": "Totalprice", "type": "number"},
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
                    "type": "string",
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
                "PartialAccessibility": {
                    "description": "Accessibility for people with disabilities. Fields are null for digital venues.",
                    "properties": {
                        "audioDisabilityCompliant": {
                            "nullable": True,
                            "title": "Audiodisabilitycompliant",
                            "type": "boolean",
                        },
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
                        "visualDisabilityCompliant": {
                            "nullable": True,
                            "title": "Visualdisabilitycompliant",
                            "type": "boolean",
                        },
                    },
                    "title": "PartialAccessibility",
                    "type": "object",
                },
                "PatchCollectiveOfferBodyModel": {
                    "additionalProperties": False,
                    "properties": {
                        "audioDisabilityCompliant": {
                            "nullable": True,
                            "title": "Audiodisabilitycompliant",
                            "type": "boolean",
                        },
                        "beginningDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Beginningdatetime",
                            "type": "string",
                        },
                        "bookingEmails": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Bookingemails",
                            "type": "array",
                        },
                        "bookingLimitDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Bookinglimitdatetime",
                            "type": "string",
                        },
                        "contactEmail": {"nullable": True, "title": "Contactemail", "type": "string"},
                        "contactPhone": {"nullable": True, "title": "Contactphone", "type": "string"},
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "domains": {
                            "items": {"type": "integer"},
                            "nullable": True,
                            "title": "Domains",
                            "type": "array",
                        },
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "educationalInstitution": {
                            "nullable": True,
                            "title": "Educationalinstitution",
                            "type": "string",
                        },
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
                        "imageCredit": {"nullable": True, "title": "Imagecredit", "type": "string"},
                        "imageFile": {"nullable": True, "title": "Imagefile", "type": "string"},
                        "interventionArea": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Interventionarea",
                            "type": "array",
                        },
                        "isActive": {"nullable": True, "title": "Isactive", "type": "boolean"},
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
                        "name": {"nullable": True, "title": "Name", "type": "string"},
                        "numberOfTickets": {"nullable": True, "title": "Numberoftickets", "type": "integer"},
                        "offerVenue": {
                            "anyOf": [{"$ref": "#/components/schemas/OfferVenueModel"}],
                            "nullable": True,
                            "title": "OfferVenueModel",
                        },
                        "students": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Students",
                            "type": "array",
                        },
                        "subcategoryId": {"nullable": True, "title": "Subcategoryid", "type": "string"},
                        "totalPrice": {"nullable": True, "title": "Totalprice", "type": "number"},
                        "venueId": {"nullable": True, "title": "Venueid", "type": "integer"},
                        "visualDisabilityCompliant": {
                            "nullable": True,
                            "title": "Visualdisabilitycompliant",
                            "type": "boolean",
                        },
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
                        "bookingEmails": {"items": {"type": "string"}, "title": "Bookingemails", "type": "array"},
                        "bookingLimitDatetime": {
                            "format": "date-time",
                            "title": "Bookinglimitdatetime",
                            "type": "string",
                        },
                        "contactEmail": {"title": "Contactemail", "type": "string"},
                        "contactPhone": {"title": "Contactphone", "type": "string"},
                        "description": {"title": "Description", "type": "string"},
                        "domains": {"items": {"type": "integer"}, "title": "Domains", "type": "array"},
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "educationalInstitution": {
                            "nullable": True,
                            "title": "Educationalinstitution",
                            "type": "string",
                        },
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
                        "imageCredit": {"nullable": True, "title": "Imagecredit", "type": "string"},
                        "imageFile": {"nullable": True, "title": "Imagefile", "type": "string"},
                        "isActive": {"title": "Isactive", "type": "boolean"},
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
                        "students": {"items": {"type": "string"}, "title": "Students", "type": "array"},
                        "subcategoryId": {"title": "Subcategoryid", "type": "string"},
                        "totalPrice": {"title": "Totalprice", "type": "number"},
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
                        "description",
                        "subcategoryId",
                        "bookingEmails",
                        "contactEmail",
                        "contactPhone",
                        "domains",
                        "students",
                        "offerVenue",
                        "isActive",
                        "beginningDatetime",
                        "bookingLimitDatetime",
                        "totalPrice",
                        "numberOfTickets",
                    ],
                    "title": "PostCollectiveOfferBodyModel",
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
                "VenueDigitalLocation": {
                    "properties": {
                        "type": {"default": "digital", "enum": ["digital"], "title": "Type", "type": "string"}
                    },
                    "title": "VenueDigitalLocation",
                    "type": "object",
                },
                "VenuePhysicalLocation": {
                    "properties": {
                        "address": {
                            "example": "55 rue du Faubourg-Saint-Honor\u00e9",
                            "nullable": True,
                            "title": "Address",
                            "type": "string",
                        },
                        "city": {"example": "Paris", "nullable": True, "title": "City", "type": "string"},
                        "postalCode": {"example": "75008", "nullable": True, "title": "Postalcode", "type": "string"},
                        "type": {"default": "physical", "enum": ["physical"], "title": "Type", "type": "string"},
                    },
                    "title": "VenuePhysicalLocation",
                    "type": "object",
                },
                "VenueResponse": {
                    "properties": {
                        "accessibility": {"$ref": "#/components/schemas/PartialAccessibility"},
                        "activityDomain": {"$ref": "#/components/schemas/VenueTypeEnum"},
                        "createdDatetime": {"format": "date-time", "title": "Createddatetime", "type": "string"},
                        "id": {"title": "Id", "type": "integer"},
                        "legalName": {
                            "example": "Palais de l'\u00c9lys\u00e9e",
                            "title": "Legalname",
                            "type": "string",
                        },
                        "location": {
                            "description": "Location where the offers will be available or will take place. There is exactly one digital venue per offerer, which is listed although its id is not required to create a digital offer (see DigitalLocation model).",
                            "discriminator": {
                                "mapping": {
                                    "digital": "#/components/schemas/VenueDigitalLocation",
                                    "physical": "#/components/schemas/VenuePhysicalLocation",
                                },
                                "propertyName": "type",
                            },
                            "oneOf": [
                                {"$ref": "#/components/schemas/VenuePhysicalLocation"},
                                {"$ref": "#/components/schemas/VenueDigitalLocation"},
                            ],
                            "title": "Location",
                        },
                        "publicName": {
                            "description": "If null, legalName is used.",
                            "example": "\u00c9lys\u00e9e",
                            "nullable": True,
                            "title": "Publicname",
                            "type": "string",
                        },
                        "siret": {
                            "description": "Null when venue is digital or when siretComment field is not null.",
                            "example": "12345678901234",
                            "nullable": True,
                            "title": "Siret",
                            "type": "string",
                        },
                        "siretComment": {
                            "description": "Applicable if siret is null and venue is physical.",
                            "example": None,
                            "nullable": True,
                            "title": "Siretcomment",
                            "type": "string",
                        },
                    },
                    "required": [
                        "createdDatetime",
                        "id",
                        "location",
                        "legalName",
                        "publicName",
                        "activityDomain",
                        "accessibility",
                    ],
                    "title": "VenueResponse",
                    "type": "object",
                },
                "VenueTypeEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "ADMINISTRATIVE",
                        "ARTISTIC_COURSE",
                        "BOOKSTORE",
                        "CONCERT_HALL",
                        "CREATIVE_ARTS_STORE",
                        "CULTURAL_CENTRE",
                        "DIGITAL",
                        "DISTRIBUTION_STORE",
                        "FESTIVAL",
                        "GAMES",
                        "LIBRARY",
                        "MOVIE",
                        "MUSEUM",
                        "MUSICAL_INSTRUMENT_STORE",
                        "OTHER",
                        "PATRIMONY_TOURISM",
                        "PERFORMING_ARTS",
                        "RECORD_STORE",
                        "SCIENTIFIC_CULTURE",
                        "TRAVELING_CINEMA",
                        "VISUAL_ARTS",
                    ],
                    "title": "VenueTypeEnum",
                    "type": "string",
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
                    "description": "Bien que, dans le cas d\u2019un \u00e9v\u00e8nement, l\u2019utilisateur ne peut plus annuler sa r\u00e9servation 72h avant le d\u00e9but de ce dernier, cette API permet d\u2019annuler la r\u00e9servation d\u2019un utilisateur si elle n\u2019a pas encore \u00e9t\u00e9 valid\u00e9.",
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
                        "204": {"description": "La contremarque a \u00e9t\u00e9 annul\u00e9e avec succ\u00e8s"},
                        "401": {"description": "Authentification n\u00e9cessaire"},
                        "403": {
                            "description": "Vous n'avez pas les droits n\u00e9cessaires pour annuler cette contremarque ou la r\u00e9servation a d\u00e9j\u00e0 \u00e9t\u00e9 valid\u00e9e"
                        },
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {"description": "La contremarque a d\u00e9j\u00e0 \u00e9t\u00e9 annul\u00e9e"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
                    "summary": "Annulation d'une r\u00e9servation.",
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
                        "204": {
                            "description": "L'annulation de la validation de la contremarque a bien \u00e9t\u00e9 effectu\u00e9e"
                        },
                        "401": {"description": "Authentification n\u00e9cessaire"},
                        "403": {
                            "description": "Vous n'avez pas les droits n\u00e9cessaires pour voir cette contremarque"
                        },
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {
                            "description": "La requ\u00eate est refus\u00e9e car la contremarque n'a pas encore \u00e9t\u00e9 valid\u00e9e, a \u00e9t\u00e9 annul\u00e9e, ou son remboursement a \u00e9t\u00e9 initi\u00e9"
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
                    "summary": "Annulation de la validation d'une r\u00e9servation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/bookings/token/{token}": {
                "get": {
                    "description": "Le code \u201ccontremarque\u201d ou \"token\" est une cha\u00eene de caract\u00e8res permettant d\u2019identifier la r\u00e9servation et qui sert de preuve de r\u00e9servation. Ce code unique est g\u00e9n\u00e9r\u00e9 pour chaque r\u00e9servation d'un utilisateur sur l'application et lui est transmis \u00e0 cette occasion.",
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
                            "description": "La contremarque existe et n\u2019est pas valid\u00e9e",
                        },
                        "401": {"description": "Authentification n\u00e9cessaire"},
                        "403": {
                            "description": "Vous n'avez pas les droits n\u00e9cessaires pour voir cette contremarque"
                        },
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {
                            "description": "Cette contremarque a \u00e9t\u00e9 valid\u00e9e.\n En l\u2019invalidant vous indiquez qu\u2019elle n\u2019a pas \u00e9t\u00e9 utilis\u00e9e et vous ne serez pas rembours\u00e9."
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
                    "summary": "Consultation d'une r\u00e9servation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/bookings/use/token/{token}": {
                "patch": {
                    "description": "Pour confirmer que la r\u00e9servation a bien \u00e9t\u00e9 utilis\u00e9e par le jeune.",
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
                        "204": {"description": "La contremarque a bien \u00e9t\u00e9 valid\u00e9e"},
                        "401": {"description": "Authentification n\u00e9cessaire"},
                        "403": {
                            "description": "Vous n'avez pas les droits n\u00e9cessaires pour voir cette contremarque"
                        },
                        "404": {"description": "La contremarque n'existe pas"},
                        "410": {
                            "description": "Cette contremarque a \u00e9t\u00e9 valid\u00e9e.\n En l\u2019invalidant vous indiquez qu\u2019elle n\u2019a pas \u00e9t\u00e9 utilis\u00e9e et vous ne serez pas rembours\u00e9."
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
                    "summary": "Validation d'une r\u00e9servation.",
                    "tags": ["API Contremarque"],
                }
            },
            "/v2/collective/bookings/{booking_id}": {
                "get": {
                    "description": "",
                    "operationId": "GetCollectiveBooking",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "booking_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CollectiveBookingResponseModel"}
                                }
                            },
                            "description": "Les informations d'une r\u00e9servation collective",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cup\u00e9ration les informations d'une r\u00e9servation collective",
                    "tags": ["API offres collectives"],
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
                            "description": "La liste des cat\u00e9gories \u00e9ligibles existantes.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cup\u00e9ration de la liste des cat\u00e9gories d'offres propos\u00e9es.",
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
                            "description": "La liste des domaines d'\u00e9ducation.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cup\u00e9ration de la liste des domaines d'\u00e9ducation pouvant \u00eatre associ\u00e9s aux offres collectives.",
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
                            "name": "uai",
                            "required": False,
                            "schema": {"nullable": True, "title": "Uai", "type": "string"},
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
                            "description": "La liste des \u00e9tablissement scolaires \u00e9ligibles.",
                        },
                        "400": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Requ\u00eate malform\u00e9e",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cup\u00e9ration de la liste \u00e9tablissements scolaires.",
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
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Vous n'avez pas les droits n\u00e9cessaires pour voir cette offre collective",
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cuperation de l'offre collective avec l'identifiant offer_id. Cette api ignore les offre vitrines et les offres commenc\u00e9es sur l'interface web et non finalis\u00e9es.",
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
                            "description": "L'offre collective \u00e0 \u00e9t\u00e9 cr\u00e9\u00e9e avec succes",
                        },
                        "400": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Requ\u00eate malform\u00e9e",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Non \u00e9ligible pour les offres collectives",
                        },
                        "404": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "L'une des resources pour la cr\u00e9ation de l'offre n'a pas \u00e9t\u00e9 trouv\u00e9e",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Cr\u00e9ation d'une offre collective.",
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
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Vous n'avez pas les droits n\u00e9cessaires pour voir cette offre collective",
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cuperation de l'offre collective avec l'identifiant offer_id.",
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
                            "description": "L'offre collective \u00e0 \u00e9t\u00e9 \u00e9dit\u00e9 avec succes",
                        },
                        "400": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Requ\u00eate malform\u00e9e",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "403": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Vous n'avez pas les droits n\u00e9cessaires pour \u00e9diter cette offre collective",
                        },
                        "404": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "L'une des resources pour la cr\u00e9ation de l'offre n'a pas \u00e9t\u00e9 trouv\u00e9e",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponseModel"}}
                            },
                            "description": "Cetains champs ne peuvent pas \u00eatre \u00e9dit\u00e9s selon l'\u00e9tat de l'offre",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "\u00c9dition d'une offre collective.",
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
                            "description": "La liste des domaines d'\u00e9ducation.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cup\u00e9ration de la liste des publics cibles pour lesquelles des offres collectives peuvent \u00eatre propos\u00e9es.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/subcategories": {
                "get": {
                    "description": "",
                    "operationId": "ListSubcategories",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CollectiveOffersListSubCategoriesResponseModel"
                                    }
                                }
                            },
                            "description": "La liste des sous-cat\u00e9gories \u00e9ligibles existantes.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cup\u00e9ration de la liste des sous-cat\u00e9gories d'offres propos\u00e9es a un public collectif.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/venues": {
                "get": {
                    "description": "Tous les lieux enregistr\u00e9s, sont list\u00e9s ici avec leurs coordonn\u00e9es.",
                    "operationId": "ListVenues",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CollectiveOffersListVenuesResponseModel"}
                                }
                            },
                            "description": "La liste des lieux ou vous pouvez cr\u00e9er une offre.",
                        },
                        "401": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/AuthErrorResponseModel"}}
                            },
                            "description": "Authentification n\u00e9cessaire",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "R\u00e9cup\u00e9ration de la liste des lieux associ\u00e9s au fournisseur authentifi\u00e9e par le jeton d'API.",
                    "tags": ["API offres collectives"],
                }
            },
        },
        "security": [],
        "servers": [{"url": settings.API_URL}],
        "tags": [{"name": "API offres collectives"}, {"name": "API Contremarque"}],
    }
