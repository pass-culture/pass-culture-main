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
                        "id": {"title": "Id", "type": "integer"},
                        "reimbursementDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Reimbursementdate",
                            "type": "string",
                        },
                        "status": {"$ref": "#/components/schemas/CollectiveBookingStatus"},
                    },
                    "required": ["id", "status", "dateCreated"],
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
                        "bookings": {
                            "items": {"$ref": "#/components/schemas/CollectiveBookingResponseModel"},
                            "title": "Bookings",
                            "type": "array",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "status": {"title": "Status", "type": "string"},
                        "venueId": {"title": "Venueid", "type": "integer"},
                    },
                    "required": ["id", "beginningDatetime", "status", "venueId", "bookings"],
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
                        "firstName": {"nullable": True, "title": "Firstname", "type": "string"},
                        "formula": {
                            "allOf": [{"$ref": "#/components/schemas/BookingFormula"}],
                            "description": "S'applique uniquement aux offres de catégorie Cinéma. Abonnement (ABO) ou place (PLACE).",
                            "nullable": True,
                        },
                        "isUsed": {"title": "Isused", "type": "boolean"},
                        "lastName": {"nullable": True, "title": "Lastname", "type": "string"},
                        "offerId": {"title": "Offerid", "type": "integer"},
                        "offerName": {"title": "Offername", "type": "string"},
                        "offerType": {"$ref": "#/components/schemas/BookingOfferType"},
                        "phoneNumber": {"nullable": True, "title": "Phonenumber", "type": "string"},
                        "price": {"title": "Price", "type": "number"},
                        "priceCategoryLabel": {"nullable": True, "title": "Pricecategorylabel", "type": "string"},
                        "publicOfferId": {"title": "Publicofferid", "type": "string"},
                        "quantity": {"title": "Quantity", "type": "integer"},
                        "theater": {
                            "description": "Identifiant du film et de la salle dans le cas d’une offre synchronisée par Allociné.",
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
                "GetOffererVenuesResponse": {
                    "properties": {
                        "offerer": {
                            "allOf": [{"$ref": "#/components/schemas/OffererResponse"}],
                            "description": "Offerer to which the venues belong. Entity linked to the api key used.",
                            "title": "Offerer",
                        },
                        "venues": {
                            "items": {"$ref": "#/components/schemas/VenueResponse"},
                            "title": "Venues",
                            "type": "array",
                        },
                    },
                    "required": ["offerer", "venues"],
                    "title": "GetOffererVenuesResponse",
                    "type": "object",
                },
                "GetOfferersVenuesQuery": {
                    "properties": {
                        "siren": {
                            "example": "123456789",
                            "nullable": True,
                            "pattern": "^\\d{9}$",
                            "title": "Siren",
                            "type": "string",
                        }
                    },
                    "title": "GetOfferersVenuesQuery",
                    "type": "object",
                },
                "GetOfferersVenuesResponse": {
                    "items": {"$ref": "#/components/schemas/GetOffererVenuesResponse"},
                    "title": "GetOfferersVenuesResponse",
                    "type": "array",
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
                        "bookings": {
                            "items": {"$ref": "#/components/schemas/CollectiveBookingResponseModel"},
                            "title": "Bookings",
                            "type": "array",
                        },
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
                        "nationalProgram": {
                            "anyOf": [{"$ref": "#/components/schemas/NationalProgramModel"}],
                            "nullable": True,
                            "title": "NationalProgramModel",
                        },
                        "numberOfTickets": {"title": "Numberoftickets", "type": "integer"},
                        "offerVenue": {"$ref": "#/components/schemas/OfferVenueModel"},
                        "status": {"title": "Status", "type": "string"},
                        "students": {"items": {"type": "string"}, "title": "Students", "type": "array"},
                        "subcategoryId": {"nullable": True, "title": "Subcategoryid", "type": "string"},
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
                        "bookings",
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
                "ListNationalProgramsResponseModel": {
                    "items": {"$ref": "#/components/schemas/NationalProgramModel"},
                    "title": "ListNationalProgramsResponseModel",
                    "type": "array",
                },
                "NationalProgramModel": {
                    "properties": {
                        "id": {"title": "Id", "type": "integer"},
                        "name": {"title": "Name", "type": "string"},
                    },
                    "required": ["id", "name"],
                    "title": "NationalProgramModel",
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
                "OffererResponse": {
                    "properties": {
                        "createdDatetime": {"format": "date-time", "title": "Createddatetime", "type": "string"},
                        "id": {"title": "Id", "type": "integer"},
                        "name": {"example": "Structure A", "title": "Name", "type": "string"},
                        "siren": {"example": "123456789", "nullable": True, "title": "Siren", "type": "string"},
                    },
                    "required": ["id", "createdDatetime", "name"],
                    "title": "OffererResponse",
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
                        "nationalProgramId": {"nullable": True, "title": "Nationalprogramid", "type": "integer"},
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
                        "nationalProgramId": {"nullable": True, "title": "Nationalprogramid", "type": "integer"},
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
                            "example": "55 rue du Faubourg-Saint-Honoré",
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
                        "legalName": {"example": "Palais de l'Élysée", "title": "Legalname", "type": "string"},
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
                            "example": "Élysée",
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
                    "description": "Bien que, dans le cas d’un évènement, l’utilisateur ne peut plus annuler sa réservation 72h avant le début de ce dernier, cette API permet d’annuler la réservation d’un utilisateur si elle n’a pas encore été validé.",
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
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
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
                    "security": [{"ApiKeyAuth": []}, {"SessionAuth": []}],
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
                            "description": "Cette contremarque a été validée.\n En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé."
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
                            "description": "Cette contremarque a été validée.\n En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé."
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
            "/v2/collective/bookings/{booking_id}": {
                "patch": {
                    "description": "",
                    "operationId": "CancelCollectiveBooking",
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
                        "204": {"description": "Annuler une réservation collective"},
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Annuler une réservation collective",
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
                    "security": [{"ApiKeyAuth": []}],
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
                    "security": [{"ApiKeyAuth": []}],
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Récupération de la liste établissements scolaires.",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/national-programs/": {
                "get": {
                    "description": "",
                    "operationId": "GetNationalPrograms",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ListNationalProgramsResponseModel"}
                                }
                            },
                            "description": "Il n'y a pas de dispositifs nationaux",
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
                            "description": "Vous n'avez pas les droits nécessaires pour voir ces informations",
                        },
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Liste de tous les dispositifs nationaux connus",
                    "tags": ["API offres collectives"],
                }
            },
            "/v2/collective/offerer_venues": {
                "get": {
                    "description": "Tous les lieux enregistrés, sont listés ici avec leurs coordonnées.",
                    "operationId": "GetOffererVenues",
                    "parameters": [
                        {
                            "description": "",
                            "in": "query",
                            "name": "siren",
                            "required": False,
                            "schema": {
                                "example": "123456789",
                                "nullable": True,
                                "pattern": "^\\d{9}$",
                                "title": "Siren",
                                "type": "string",
                            },
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/GetOfferersVenuesResponse"}
                                }
                            },
                            "description": "La liste des lieux, groupés par structures",
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Récupération des lieux associés au fournisseur authentifié par le jeton d'API; groupés par structures.",
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Récuperation des offres collectives Cette api ignore les offre vitrines et les offres commencées sur l'interface web et non finalisées.",
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
                    "security": [{"ApiKeyAuth": []}],
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
                    "security": [{"ApiKeyAuth": []}],
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
                    "security": [{"ApiKeyAuth": []}],
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Récupération de la liste des publics cibles pour lesquelles des offres collectives peuvent être proposées.",
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
                            "description": "La liste des sous-catégories éligibles existantes.",
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Récupération de la liste des sous-catégories d'offres proposées a un public collectif.",
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
                    "security": [{"ApiKeyAuth": []}],
                    "summary": "Récupération de la liste des lieux associés au fournisseur authentifiée par le jeton d'API.",
                    "tags": ["API offres collectives"],
                }
            },
        },
        "security": [],
        "servers": [{"url": settings.API_URL}],
        "tags": [{"name": "API offres collectives"}, {"name": "API Contremarque"}],
    }
