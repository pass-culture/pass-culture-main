import difflib
import json


def test_public_api(client):
    response = client.get("/native/v1/openapi.json")
    assert response.status_code == 200
    expected = {
        "components": {
            "schemas": {
                "AccountRequest": {
                    "properties": {
                        "appsFlyerPlatform": {"nullable": True, "title": "Appsflyerplatform", "type": "string"},
                        "appsFlyerUserId": {"nullable": True, "title": "Appsflyeruserid", "type": "string"},
                        "birthdate": {"format": "date", "title": "Birthdate", "type": "string"},
                        "email": {"title": "Email", "type": "string"},
                        "marketingEmailSubscription": {
                            "default": False,
                            "nullable": True,
                            "title": "Marketingemailsubscription",
                            "type": "boolean",
                        },
                        "password": {"title": "Password", "type": "string"},
                        "token": {"title": "Token", "type": "string"},
                        "trustedDevice": {
                            "anyOf": [{"$ref": "#/components/schemas/TrustedDevice"}],
                            "nullable": True,
                            "title": "TrustedDevice",
                        },
                    },
                    "required": ["email", "password", "birthdate", "token"],
                    "title": "AccountRequest",
                    "type": "object",
                },
                "AccountState": {
                    "description": "An enumeration.",
                    "enum": ["ACTIVE", "INACTIVE", "SUSPENDED", "SUSPENDED_UPON_USER_REQUEST", "DELETED"],
                    "title": "AccountState",
                },
                "ActivityIdEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "MIDDLE_SCHOOL_STUDENT",
                        "HIGH_SCHOOL_STUDENT",
                        "STUDENT",
                        "EMPLOYEE",
                        "APPRENTICE",
                        "APPRENTICE_STUDENT",
                        "VOLUNTEER",
                        "INACTIVE",
                        "UNEMPLOYED",
                    ],
                    "title": "ActivityIdEnum",
                },
                "ActivityResponseModel": {
                    "properties": {
                        "associatedSchoolTypesIds": {
                            "items": {"$ref": "#/components/schemas/SchoolTypesIdEnum"},
                            "nullable": True,
                            "type": "array",
                        },
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "id": {"$ref": "#/components/schemas/ActivityIdEnum"},
                        "label": {"title": "Label", "type": "string"},
                    },
                    "required": ["id", "label"],
                    "title": "ActivityResponseModel",
                    "type": "object",
                },
                "Banner": {
                    "properties": {
                        "name": {"$ref": "#/components/schemas/BannerName"},
                        "text": {"title": "Text", "type": "string"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["name", "title", "text"],
                    "title": "Banner",
                    "type": "object",
                },
                "BannerMetaModel": {
                    "properties": {
                        "image_credit": {
                            "maxLength": 255,
                            "minLength": 1,
                            "nullable": True,
                            "title": "Image Credit",
                            "type": "string",
                        }
                    },
                    "title": "BannerMetaModel",
                    "type": "object",
                },
                "BannerName": {
                    "description": "An enumeration.",
                    "enum": [
                        "geolocation_banner",
                        "activation_banner",
                        "retry_identity_check_banner",
                        "transition_17_18_banner",
                    ],
                    "title": "BannerName",
                },
                "BannerQueryParams": {
                    "properties": {"isGeolocated": {"default": False, "title": "Isgeolocated", "type": "boolean"}},
                    "title": "BannerQueryParams",
                    "type": "object",
                },
                "BannerResponse": {
                    "properties": {"banner": {"anyOf": [{"$ref": "#/components/schemas/Banner"}], "nullable": True}},
                    "title": "BannerResponse",
                    "type": "object",
                },
                "BookOfferRequest": {
                    "properties": {
                        "quantity": {"title": "Quantity", "type": "integer"},
                        "stockId": {"title": "Stockid", "type": "integer"},
                    },
                    "required": ["stockId", "quantity"],
                    "title": "BookOfferRequest",
                    "type": "object",
                },
                "BookOfferResponse": {
                    "properties": {"bookingId": {"title": "Bookingid", "type": "integer"}},
                    "required": ["bookingId"],
                    "title": "BookOfferResponse",
                    "type": "object",
                },
                "BookingActivationCodeResponse": {
                    "properties": {
                        "code": {"title": "Code", "type": "string"},
                        "expirationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Expirationdate",
                            "type": "string",
                        },
                    },
                    "required": ["code"],
                    "title": "BookingActivationCodeResponse",
                    "type": "object",
                },
                "BookingCancellationReasons": {
                    "description": "An enumeration.",
                    "enum": ["OFFERER", "BENEFICIARY", "EXPIRED", "FRAUD", "REFUSED_BY_INSTITUTE"],
                    "title": "BookingCancellationReasons",
                },
                "BookingDisplayStatusRequest": {
                    "properties": {"ended": {"title": "Ended", "type": "boolean"}},
                    "required": ["ended"],
                    "title": "BookingDisplayStatusRequest",
                    "type": "object",
                },
                "BookingOfferExtraData": {
                    "properties": {
                        "ean": {"nullable": True, "title": "Ean", "type": "string"},
                        "isbn": {"nullable": True, "title": "Isbn", "type": "string"},
                    },
                    "title": "BookingOfferExtraData",
                    "type": "object",
                },
                "BookingOfferResponse": {
                    "properties": {
                        "extraData": {
                            "anyOf": [{"$ref": "#/components/schemas/BookingOfferExtraData"}],
                            "nullable": True,
                            "title": "BookingOfferExtraData",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "image": {
                            "anyOf": [{"$ref": "#/components/schemas/OfferImageResponse"}],
                            "nullable": True,
                            "title": "OfferImageResponse",
                        },
                        "isDigital": {"title": "Isdigital", "type": "boolean"},
                        "isPermanent": {"title": "Ispermanent", "type": "boolean"},
                        "name": {"title": "Name", "type": "string"},
                        "subcategoryId": {"$ref": "#/components/schemas/SubcategoryIdEnum"},
                        "url": {"nullable": True, "title": "Url", "type": "string"},
                        "venue": {"$ref": "#/components/schemas/BookingVenueResponse"},
                        "withdrawalDelay": {"nullable": True, "title": "Withdrawaldelay", "type": "integer"},
                        "withdrawalDetails": {"nullable": True, "title": "Withdrawaldetails", "type": "string"},
                        "withdrawalType": {
                            "anyOf": [{"$ref": "#/components/schemas/WithdrawalTypeEnum"}],
                            "nullable": True,
                        },
                    },
                    "required": ["id", "name", "isDigital", "isPermanent", "subcategoryId", "venue"],
                    "title": "BookingOfferResponse",
                    "type": "object",
                },
                "BookingReponse": {
                    "properties": {
                        "activationCode": {
                            "anyOf": [{"$ref": "#/components/schemas/BookingActivationCodeResponse"}],
                            "nullable": True,
                            "title": "BookingActivationCodeResponse",
                        },
                        "cancellationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Cancellationdate",
                            "type": "string",
                        },
                        "cancellationReason": {
                            "anyOf": [{"$ref": "#/components/schemas/BookingCancellationReasons"}],
                            "nullable": True,
                        },
                        "completedUrl": {"nullable": True, "title": "Completedurl", "type": "string"},
                        "confirmationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Confirmationdate",
                            "type": "string",
                        },
                        "dateCreated": {"format": "date-time", "title": "Datecreated", "type": "string"},
                        "dateUsed": {"format": "date-time", "nullable": True, "title": "Dateused", "type": "string"},
                        "expirationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Expirationdate",
                            "type": "string",
                        },
                        "externalBookings": {
                            "items": {"$ref": "#/components/schemas/ExternalBookingResponse"},
                            "nullable": True,
                            "title": "Externalbookings",
                            "type": "array",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "qrCodeData": {"nullable": True, "title": "Qrcodedata", "type": "string"},
                        "quantity": {"title": "Quantity", "type": "integer"},
                        "stock": {"$ref": "#/components/schemas/BookingStockResponse"},
                        "token": {"nullable": True, "title": "Token", "type": "string"},
                        "totalAmount": {"title": "Totalamount", "type": "integer"},
                    },
                    "required": ["id", "dateCreated", "quantity", "stock", "totalAmount"],
                    "title": "BookingReponse",
                    "type": "object",
                },
                "BookingStockResponse": {
                    "properties": {
                        "beginningDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Beginningdatetime",
                            "type": "string",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "offer": {"$ref": "#/components/schemas/BookingOfferResponse"},
                        "price": {"title": "Price", "type": "integer"},
                        "priceCategoryLabel": {"nullable": True, "title": "Pricecategorylabel", "type": "string"},
                    },
                    "required": ["id", "offer", "price"],
                    "title": "BookingStockResponse",
                    "type": "object",
                },
                "BookingVenueResponse": {
                    "properties": {
                        "address": {"nullable": True, "title": "Address", "type": "string"},
                        "city": {"nullable": True, "title": "City", "type": "string"},
                        "coordinates": {"$ref": "#/components/schemas/Coordinates"},
                        "id": {"title": "Id", "type": "integer"},
                        "name": {"title": "Name", "type": "string"},
                        "postalCode": {"nullable": True, "title": "Postalcode", "type": "string"},
                        "publicName": {"nullable": True, "title": "Publicname", "type": "string"},
                    },
                    "required": ["id", "name", "coordinates"],
                    "title": "BookingVenueResponse",
                    "type": "object",
                },
                "BookingsResponse": {
                    "properties": {
                        "ended_bookings": {
                            "items": {"$ref": "#/components/schemas/BookingReponse"},
                            "title": "Ended Bookings",
                            "type": "array",
                        },
                        "hasBookingsAfter18": {"title": "Hasbookingsafter18", "type": "boolean"},
                        "ongoing_bookings": {
                            "items": {"$ref": "#/components/schemas/BookingReponse"},
                            "title": "Ongoing Bookings",
                            "type": "array",
                        },
                    },
                    "required": ["ended_bookings", "ongoing_bookings", "hasBookingsAfter18"],
                    "title": "BookingsResponse",
                    "type": "object",
                },
                "CallToActionIcon": {
                    "description": "An enumeration.",
                    "enum": ["EMAIL", "RETRY", "EXTERNAL"],
                    "title": "CallToActionIcon",
                },
                "CallToActionMessage": {
                    "properties": {
                        "callToActionIcon": {
                            "anyOf": [{"$ref": "#/components/schemas/CallToActionIcon"}],
                            "nullable": True,
                        },
                        "callToActionLink": {"nullable": True, "title": "Calltoactionlink", "type": "string"},
                        "callToActionTitle": {"nullable": True, "title": "Calltoactiontitle", "type": "string"},
                    },
                    "title": "CallToActionMessage",
                    "type": "object",
                },
                "CategoryIdEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "BEAUX_ARTS",
                        "CARTE_JEUNES",
                        "CINEMA",
                        "CONFERENCE",
                        "FILM",
                        "INSTRUMENT",
                        "JEU",
                        "LIVRE",
                        "MEDIA",
                        "MUSEE",
                        "MUSIQUE_ENREGISTREE",
                        "MUSIQUE_LIVE",
                        "PRATIQUE_ART",
                        "SPECTACLE",
                        "TECHNIQUE",
                    ],
                    "title": "CategoryIdEnum",
                },
                "ChangeBeneficiaryEmailBody": {
                    "properties": {"token": {"title": "Token", "type": "string"}},
                    "required": ["token"],
                    "title": "ChangeBeneficiaryEmailBody",
                    "type": "object",
                },
                "ChangePasswordRequest": {
                    "properties": {
                        "currentPassword": {"title": "Currentpassword", "type": "string"},
                        "newPassword": {"title": "Newpassword", "type": "string"},
                    },
                    "required": ["currentPassword", "newPassword"],
                    "title": "ChangePasswordRequest",
                    "type": "object",
                },
                "Consent": {
                    "properties": {
                        "accepted": {
                            "items": {"minLength": 1, "type": "string"},
                            "title": "Accepted",
                            "type": "array",
                            "uniqueItems": True,
                        },
                        "mandatory": {
                            "items": {"minLength": 1, "type": "string"},
                            "title": "Mandatory",
                            "type": "array",
                            "uniqueItems": True,
                        },
                        "refused": {
                            "items": {"minLength": 1, "type": "string"},
                            "title": "Refused",
                            "type": "array",
                            "uniqueItems": True,
                        },
                    },
                    "required": ["mandatory", "accepted", "refused"],
                    "title": "Consent",
                    "type": "object",
                },
                "CookieConsentRequest": {
                    "additionalProperties": False,
                    "properties": {
                        "choiceDatetime": {"format": "date-time", "title": "Choicedatetime", "type": "string"},
                        "consent": {"$ref": "#/components/schemas/Consent"},
                        "deviceId": {"title": "Deviceid", "type": "string"},
                        "userId": {"nullable": True, "title": "Userid", "type": "integer"},
                    },
                    "required": ["consent", "choiceDatetime", "deviceId"],
                    "title": "CookieConsentRequest",
                    "type": "object",
                },
                "Coordinates": {
                    "properties": {
                        "latitude": {"nullable": True, "title": "Latitude", "type": "number"},
                        "longitude": {"nullable": True, "title": "Longitude", "type": "number"},
                    },
                    "title": "Coordinates",
                    "type": "object",
                },
                "Credit": {
                    "properties": {
                        "initial": {"title": "Initial", "type": "integer"},
                        "remaining": {"title": "Remaining", "type": "integer"},
                    },
                    "required": ["initial", "remaining"],
                    "title": "Credit",
                    "type": "object",
                },
                "CulturalSurveyAnswer": {
                    "properties": {
                        "id": {"$ref": "#/components/schemas/CulturalSurveyAnswerEnum"},
                        "sub_question": {
                            "anyOf": [{"$ref": "#/components/schemas/CulturalSurveyQuestionEnum"}],
                            "nullable": True,
                        },
                        "subtitle": {"nullable": True, "title": "Subtitle", "type": "string"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["id", "title"],
                    "title": "CulturalSurveyAnswer",
                    "type": "object",
                },
                "CulturalSurveyAnswerEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "FESTIVAL",
                        "SPECTACLE",
                        "BIBLIOTHEQUE",
                        "EVENEMENT_JEU",
                        "CONCERT",
                        "CINEMA",
                        "MUSEE",
                        "CONFERENCE",
                        "COURS",
                        "SANS_SORTIES",
                        "FESTIVAL_MUSIQUE",
                        "FESTIVAL_AVANT_PREMIERE",
                        "FESTIVAL_SPECTACLE",
                        "FESTIVAL_LIVRE",
                        "FESTIVAL_CINEMA",
                        "FESTIVAL_AUTRE",
                        "SPECTACLE_HUMOUR",
                        "SPECTACLE_THEATRE",
                        "SPECTACLE_RUE",
                        "SPECTACLE_OPERA",
                        "SPECTACLE_CIRQUE",
                        "SPECTACLE_DANSE",
                        "SPECTACLE_AUTRE",
                        "MATERIEL_ART_CREATIF",
                        "PODCAST",
                        "LIVRE",
                        "JOUE_INSTRUMENT",
                        "PRESSE_EN_LIGNE",
                        "JEU_VIDEO",
                        "FILM_DOMICILE",
                        "SANS_ACTIVITES",
                        "PROJECTION_FESTIVAL",
                        "PROJECTION_CINEMA",
                        "PROJECTION_VISITE",
                        "PROJECTION_CONCERT",
                        "PROJECTION_CD_VINYLE",
                        "PROJECTION_SPECTACLE",
                        "PROJECTION_ACTIVITE_ARTISTIQUE",
                        "PROJECTION_LIVRE",
                        "PROJECTION_CONFERENCE",
                        "PROJECTION_JEU",
                        "PROJECTION_AUTRE",
                    ],
                    "title": "CulturalSurveyAnswerEnum",
                },
                "CulturalSurveyAnswersRequest": {
                    "properties": {
                        "answers": {
                            "items": {"$ref": "#/components/schemas/CulturalSurveyUserAnswer"},
                            "title": "Answers",
                            "type": "array",
                        }
                    },
                    "required": ["answers"],
                    "title": "CulturalSurveyAnswersRequest",
                    "type": "object",
                },
                "CulturalSurveyQuestion": {
                    "properties": {
                        "answers": {
                            "items": {"$ref": "#/components/schemas/CulturalSurveyAnswer"},
                            "title": "Answers",
                            "type": "array",
                        },
                        "id": {"$ref": "#/components/schemas/CulturalSurveyQuestionEnum"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["id", "title", "answers"],
                    "title": "CulturalSurveyQuestion",
                    "type": "object",
                },
                "CulturalSurveyQuestionEnum": {
                    "description": "An enumeration.",
                    "enum": ["SORTIES", "FESTIVALS", "SPECTACLES", "ACTIVITES", "PROJECTIONS"],
                    "title": "CulturalSurveyQuestionEnum",
                },
                "CulturalSurveyQuestionsResponse": {
                    "properties": {
                        "questions": {
                            "items": {"$ref": "#/components/schemas/CulturalSurveyQuestion"},
                            "title": "Questions",
                            "type": "array",
                        }
                    },
                    "required": ["questions"],
                    "title": "CulturalSurveyQuestionsResponse",
                    "type": "object",
                },
                "CulturalSurveyUserAnswer": {
                    "properties": {
                        "answerIds": {
                            "items": {"$ref": "#/components/schemas/CulturalSurveyAnswerEnum"},
                            "type": "array",
                        },
                        "questionId": {"$ref": "#/components/schemas/CulturalSurveyQuestionEnum"},
                    },
                    "required": ["questionId", "answerIds"],
                    "title": "CulturalSurveyUserAnswer",
                    "type": "object",
                },
                "DepositAmountsByAge": {
                    "properties": {
                        "age_15": {"default": 2000, "title": "Age 15", "type": "integer"},
                        "age_16": {"default": 3000, "title": "Age 16", "type": "integer"},
                        "age_17": {"default": 3000, "title": "Age 17", "type": "integer"},
                        "age_18": {"default": 30000, "title": "Age 18", "type": "integer"},
                    },
                    "title": "DepositAmountsByAge",
                    "type": "object",
                },
                "DepositType": {
                    "description": "An enumeration.",
                    "enum": ["GRANT_15_17", "GRANT_18"],
                    "title": "DepositType",
                },
                "DomainsCredit": {
                    "properties": {
                        "all": {"$ref": "#/components/schemas/Credit"},
                        "digital": {
                            "anyOf": [{"$ref": "#/components/schemas/Credit"}],
                            "nullable": True,
                            "title": "Credit",
                        },
                        "physical": {
                            "anyOf": [{"$ref": "#/components/schemas/Credit"}],
                            "nullable": True,
                            "title": "Credit",
                        },
                    },
                    "required": ["all"],
                    "title": "DomainsCredit",
                    "type": "object",
                },
                "EligibilityType": {
                    "description": "An enumeration.",
                    "enum": ["underage", "age-18"],
                    "title": "EligibilityType",
                },
                "EmailHistoryEventTypeEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "UPDATE_REQUEST",
                        "CONFIRMATION",
                        "CANCELLATION",
                        "VALIDATION",
                        "ADMIN_VALIDATION",
                        "ADMIN_UPDATE_REQUEST",
                        "ADMIN_UPDATE",
                    ],
                    "title": "EmailHistoryEventTypeEnum",
                },
                "EmailUpdateStatus": {
                    "properties": {
                        "expired": {"title": "Expired", "type": "boolean"},
                        "newEmail": {"title": "Newemail", "type": "string"},
                        "status": {"$ref": "#/components/schemas/EmailHistoryEventTypeEnum"},
                    },
                    "required": ["newEmail", "expired", "status"],
                    "title": "EmailUpdateStatus",
                    "type": "object",
                },
                "ExpenseDomain": {
                    "description": "An enumeration.",
                    "enum": ["all", "digital", "physical"],
                    "title": "ExpenseDomain",
                },
                "ExternalBookingResponse": {
                    "properties": {
                        "barcode": {"title": "Barcode", "type": "string"},
                        "seat": {"nullable": True, "title": "Seat", "type": "string"},
                    },
                    "required": ["barcode"],
                    "title": "ExternalBookingResponse",
                    "type": "object",
                },
                "FavoriteMediationResponse": {
                    "properties": {
                        "credit": {"nullable": True, "title": "Credit", "type": "string"},
                        "url": {"title": "Url", "type": "string"},
                    },
                    "required": ["url"],
                    "title": "FavoriteMediationResponse",
                    "type": "object",
                },
                "FavoriteOfferResponse": {
                    "properties": {
                        "coordinates": {"$ref": "#/components/schemas/Coordinates"},
                        "date": {"format": "date-time", "nullable": True, "title": "Date", "type": "string"},
                        "expenseDomains": {"items": {"$ref": "#/components/schemas/ExpenseDomain"}, "type": "array"},
                        "externalTicketOfficeUrl": {
                            "nullable": True,
                            "title": "Externalticketofficeurl",
                            "type": "string",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "image": {
                            "anyOf": [{"$ref": "#/components/schemas/FavoriteMediationResponse"}],
                            "nullable": True,
                            "title": "FavoriteMediationResponse",
                        },
                        "isExpired": {"default": False, "title": "Isexpired", "type": "boolean"},
                        "isReleased": {"title": "Isreleased", "type": "boolean"},
                        "isSoldOut": {"default": False, "title": "Issoldout", "type": "boolean"},
                        "name": {"title": "Name", "type": "string"},
                        "price": {"nullable": True, "title": "Price", "type": "integer"},
                        "startDate": {"format": "date-time", "nullable": True, "title": "Startdate", "type": "string"},
                        "startPrice": {"nullable": True, "title": "Startprice", "type": "integer"},
                        "subcategoryId": {"$ref": "#/components/schemas/SubcategoryIdEnum"},
                    },
                    "required": ["id", "name", "subcategoryId", "coordinates", "expenseDomains", "isReleased"],
                    "title": "FavoriteOfferResponse",
                    "type": "object",
                },
                "FavoriteRequest": {
                    "properties": {"offerId": {"title": "Offerid", "type": "integer"}},
                    "required": ["offerId"],
                    "title": "FavoriteRequest",
                    "type": "object",
                },
                "FavoriteResponse": {
                    "properties": {
                        "id": {"title": "Id", "type": "integer"},
                        "offer": {"$ref": "#/components/schemas/FavoriteOfferResponse"},
                    },
                    "required": ["id", "offer"],
                    "title": "FavoriteResponse",
                    "type": "object",
                },
                "FavoritesCountResponse": {
                    "properties": {"count": {"title": "Count", "type": "integer"}},
                    "required": ["count"],
                    "title": "FavoritesCountResponse",
                    "type": "object",
                },
                "GenreType": {
                    "description": "An enumeration.",
                    "enum": ["BOOK", "MUSIC", "SHOW", "MOVIE"],
                    "title": "GenreType",
                },
                "GenreTypeContentModel": {
                    "properties": {
                        "name": {"title": "Name", "type": "string"},
                        "value": {"title": "Value", "type": "string"},
                    },
                    "required": ["name", "value"],
                    "title": "GenreTypeContentModel",
                    "type": "object",
                },
                "GenreTypeModel": {
                    "properties": {
                        "name": {"$ref": "#/components/schemas/GenreType"},
                        "values": {
                            "items": {"$ref": "#/components/schemas/GenreTypeContentModel"},
                            "title": "Values",
                            "type": "array",
                        },
                    },
                    "required": ["name", "values"],
                    "title": "GenreTypeModel",
                    "type": "object",
                },
                "HomepageLabelResponseModel": {
                    "properties": {
                        "name": {"$ref": "#/components/schemas/_HomepageLabelNameEnum"},
                        "value": {"nullable": True, "title": "Value", "type": "string"},
                    },
                    "required": ["name"],
                    "title": "HomepageLabelResponseModel",
                    "type": "object",
                },
                "HomepageLabelResponseModelv2": {
                    "properties": {
                        "name": {"$ref": "#/components/schemas/_HomepageLabelNameEnumv2"},
                        "value": {"nullable": True, "title": "Value", "type": "string"},
                    },
                    "required": ["name"],
                    "title": "HomepageLabelResponseModelv2",
                    "type": "object",
                },
                "IdentificationSessionRequest": {
                    "properties": {"redirectUrl": {"title": "Redirecturl", "type": "string"}},
                    "required": ["redirectUrl"],
                    "title": "IdentificationSessionRequest",
                    "type": "object",
                },
                "IdentificationSessionResponse": {
                    "properties": {"identificationUrl": {"title": "Identificationurl", "type": "string"}},
                    "required": ["identificationUrl"],
                    "title": "IdentificationSessionResponse",
                    "type": "object",
                },
                "IdentityCheckMethod": {
                    "description": "An enumeration.",
                    "enum": ["educonnect", "ubble"],
                    "title": "IdentityCheckMethod",
                },
                "MaintenancePageType": {
                    "description": "An enumeration.",
                    "enum": ["with-dms", "without-dms"],
                    "title": "MaintenancePageType",
                },
                "NativeCategoryIdEnumv2": {
                    "description": "An enumeration.",
                    "enum": [
                        "LIVRES_PAPIER",
                        "LIVRES_NUMERIQUE_ET_AUDIO",
                        "LIVRES_AUDIO_PHYSIQUES",
                        "ACHAT_LOCATION_INSTRUMENT",
                        "PARTITIONS_DE_MUSIQUE",
                        "VISITES_CULTURELLES_EN_LIGNE",
                        "VISITES_CULTURELLES",
                        "ABONNEMENTS_MUSEE",
                        "EVENEMENTS_PATRIMOINE",
                        "CARTES_CINEMA",
                        "SEANCES_DE_CINEMA",
                        "FILMS_SERIES_EN_LIGNE",
                        "DVD_BLU_RAY",
                        "CONCERTS_EVENEMENTS",
                        "FESTIVALS",
                        "CONCERTS_EN_LIGNE",
                        "JEUX_PHYSIQUES",
                        "JEUX_EN_LIGNE",
                        "ESCAPE_GAMES",
                        "RENCONTRES_EVENEMENTS",
                        "CONCOURS",
                        "SPECTACLES_REPRESENTATIONS",
                        "ABONNEMENTS_SPECTACLE",
                        "SPECTACLES_ENREGISTRES",
                        "PRATIQUES_ET_ATELIERS_ARTISTIQUES",
                        "MATERIELS_CREATIFS",
                        "CD_VINYLES",
                        "MUSIQUE_EN_LIGNE",
                        "BIBLIOTHEQUE",
                        "MEDIATHEQUE",
                        "LUDOTHEQUE",
                        "RENCONTRES",
                        "RENCONTRES_EN_LIGNE",
                        "CONFERENCES",
                        "SALONS_ET_METIERS",
                        "PRESSE_EN_LIGNE",
                        "PODCAST",
                        "AUTRES_MEDIAS",
                        "CARTES_JEUNES",
                        "EVENEMENTS_CINEMA",
                        "ARTS_VISUELS",
                        "FESTIVAL_DU_LIVRE",
                        "PRATIQUE_ARTISTIQUE_EN_LIGNE",
                        "DEPRECIEE",
                    ],
                    "title": "NativeCategoryIdEnumv2",
                },
                "NativeCategoryResponseModelv2": {
                    "properties": {
                        "genreType": {"anyOf": [{"$ref": "#/components/schemas/GenreType"}], "nullable": True},
                        "name": {"$ref": "#/components/schemas/NativeCategoryIdEnumv2"},
                        "value": {"nullable": True, "title": "Value", "type": "string"},
                    },
                    "required": ["name"],
                    "title": "NativeCategoryResponseModelv2",
                    "type": "object",
                },
                "NextSubscriptionStepResponse": {
                    "properties": {
                        "allowedIdentityCheckMethods": {
                            "items": {"$ref": "#/components/schemas/IdentityCheckMethod"},
                            "type": "array",
                        },
                        "hasIdentityCheckPending": {"title": "Hasidentitycheckpending", "type": "boolean"},
                        "maintenancePageType": {
                            "anyOf": [{"$ref": "#/components/schemas/MaintenancePageType"}],
                            "nullable": True,
                        },
                        "nextSubscriptionStep": {
                            "anyOf": [{"$ref": "#/components/schemas/SubscriptionStep"}],
                            "nullable": True,
                        },
                        "stepperIncludesPhoneValidation": {
                            "title": "Stepperincludesphonevalidation",
                            "type": "boolean",
                        },
                        "subscriptionMessage": {
                            "anyOf": [{"$ref": "#/components/schemas/SubscriptionMessage"}],
                            "nullable": True,
                            "title": "SubscriptionMessage",
                        },
                    },
                    "required": [
                        "stepperIncludesPhoneValidation",
                        "allowedIdentityCheckMethods",
                        "hasIdentityCheckPending",
                    ],
                    "title": "NextSubscriptionStepResponse",
                    "type": "object",
                },
                "NotificationSubscriptions": {
                    "properties": {
                        "marketingEmail": {"title": "Marketingemail", "type": "boolean"},
                        "marketingPush": {"title": "Marketingpush", "type": "boolean"},
                    },
                    "required": ["marketingEmail", "marketingPush"],
                    "title": "NotificationSubscriptions",
                    "type": "object",
                },
                "OfferAccessibilityResponse": {
                    "properties": {
                        "audioDisability": {"nullable": True, "title": "Audiodisability", "type": "boolean"},
                        "mentalDisability": {"nullable": True, "title": "Mentaldisability", "type": "boolean"},
                        "motorDisability": {"nullable": True, "title": "Motordisability", "type": "boolean"},
                        "visualDisability": {"nullable": True, "title": "Visualdisability", "type": "boolean"},
                    },
                    "title": "OfferAccessibilityResponse",
                    "type": "object",
                },
                "OfferExtraData": {
                    "properties": {
                        "author": {"nullable": True, "title": "Author", "type": "string"},
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "ean": {"nullable": True, "title": "Ean", "type": "string"},
                        "isbn": {"nullable": True, "title": "Isbn", "type": "string"},
                        "musicSubType": {"nullable": True, "title": "Musicsubtype", "type": "string"},
                        "musicType": {"nullable": True, "title": "Musictype", "type": "string"},
                        "performer": {"nullable": True, "title": "Performer", "type": "string"},
                        "showSubType": {"nullable": True, "title": "Showsubtype", "type": "string"},
                        "showType": {"nullable": True, "title": "Showtype", "type": "string"},
                        "speaker": {"nullable": True, "title": "Speaker", "type": "string"},
                        "stageDirector": {"nullable": True, "title": "Stagedirector", "type": "string"},
                        "visa": {"nullable": True, "title": "Visa", "type": "string"},
                    },
                    "title": "OfferExtraData",
                    "type": "object",
                },
                "OfferImageResponse": {
                    "properties": {
                        "credit": {"nullable": True, "title": "Credit", "type": "string"},
                        "url": {"title": "Url", "type": "string"},
                    },
                    "required": ["url"],
                    "title": "OfferImageResponse",
                    "type": "object",
                },
                "OfferOffererResponse": {
                    "properties": {"name": {"title": "Name", "type": "string"}},
                    "required": ["name"],
                    "title": "OfferOffererResponse",
                    "type": "object",
                },
                "OfferReportReasons": {
                    "properties": {
                        "reasons": {
                            "additionalProperties": {"$ref": "#/components/schemas/ReasonMeta"},
                            "title": "Reasons",
                            "type": "object",
                        }
                    },
                    "required": ["reasons"],
                    "title": "OfferReportReasons",
                    "type": "object",
                },
                "OfferReportRequest": {
                    "properties": {
                        "customReason": {"nullable": True, "title": "Customreason", "type": "string"},
                        "reason": {"$ref": "#/components/schemas/Reason"},
                    },
                    "required": ["reason"],
                    "title": "OfferReportRequest",
                    "type": "object",
                },
                "OfferResponse": {
                    "properties": {
                        "accessibility": {"$ref": "#/components/schemas/OfferAccessibilityResponse"},
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "expenseDomains": {"items": {"$ref": "#/components/schemas/ExpenseDomain"}, "type": "array"},
                        "externalTicketOfficeUrl": {
                            "nullable": True,
                            "title": "Externalticketofficeurl",
                            "type": "string",
                        },
                        "extraData": {
                            "anyOf": [{"$ref": "#/components/schemas/OfferExtraData"}],
                            "nullable": True,
                            "title": "OfferExtraData",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "image": {
                            "anyOf": [{"$ref": "#/components/schemas/OfferImageResponse"}],
                            "nullable": True,
                            "title": "OfferImageResponse",
                        },
                        "isDigital": {"title": "Isdigital", "type": "boolean"},
                        "isDuo": {"title": "Isduo", "type": "boolean"},
                        "isEducational": {"title": "Iseducational", "type": "boolean"},
                        "isExpired": {"title": "Isexpired", "type": "boolean"},
                        "isForbiddenToUnderage": {"title": "Isforbiddentounderage", "type": "boolean"},
                        "isReleased": {"title": "Isreleased", "type": "boolean"},
                        "isSoldOut": {"title": "Issoldout", "type": "boolean"},
                        "metadata": {"title": "Metadata", "type": "object"},
                        "name": {"title": "Name", "type": "string"},
                        "stocks": {
                            "items": {"$ref": "#/components/schemas/OfferStockResponse"},
                            "title": "Stocks",
                            "type": "array",
                        },
                        "subcategoryId": {"$ref": "#/components/schemas/SubcategoryIdEnum"},
                        "venue": {"$ref": "#/components/schemas/OfferVenueResponse"},
                        "withdrawalDetails": {"nullable": True, "title": "Withdrawaldetails", "type": "string"},
                    },
                    "required": [
                        "id",
                        "accessibility",
                        "expenseDomains",
                        "isExpired",
                        "isForbiddenToUnderage",
                        "isReleased",
                        "isSoldOut",
                        "isDigital",
                        "isDuo",
                        "isEducational",
                        "metadata",
                        "name",
                        "stocks",
                        "subcategoryId",
                        "venue",
                    ],
                    "title": "OfferResponse",
                    "type": "object",
                },
                "OfferStockActivationCodeResponse": {
                    "properties": {
                        "expirationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Expirationdate",
                            "type": "string",
                        }
                    },
                    "title": "OfferStockActivationCodeResponse",
                    "type": "object",
                },
                "OfferStockResponse": {
                    "properties": {
                        "activationCode": {
                            "anyOf": [{"$ref": "#/components/schemas/OfferStockActivationCodeResponse"}],
                            "nullable": True,
                            "title": "OfferStockActivationCodeResponse",
                        },
                        "beginningDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Beginningdatetime",
                            "type": "string",
                        },
                        "bookingLimitDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Bookinglimitdatetime",
                            "type": "string",
                        },
                        "cancellationLimitDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Cancellationlimitdatetime",
                            "type": "string",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "isBookable": {"title": "Isbookable", "type": "boolean"},
                        "isExpired": {"title": "Isexpired", "type": "boolean"},
                        "isForbiddenToUnderage": {"title": "Isforbiddentounderage", "type": "boolean"},
                        "isSoldOut": {"title": "Issoldout", "type": "boolean"},
                        "price": {"title": "Price", "type": "integer"},
                        "priceCategoryLabel": {"nullable": True, "title": "Pricecategorylabel", "type": "string"},
                        "remainingQuantity": {"nullable": True, "title": "Remainingquantity", "type": "integer"},
                    },
                    "required": ["id", "isBookable", "isForbiddenToUnderage", "isSoldOut", "isExpired", "price"],
                    "title": "OfferStockResponse",
                    "type": "object",
                },
                "OfferVenueResponse": {
                    "properties": {
                        "address": {"nullable": True, "title": "Address", "type": "string"},
                        "city": {"nullable": True, "title": "City", "type": "string"},
                        "coordinates": {"$ref": "#/components/schemas/Coordinates"},
                        "id": {"title": "Id", "type": "integer"},
                        "isPermanent": {"title": "Ispermanent", "type": "boolean"},
                        "name": {"title": "Name", "type": "string"},
                        "offerer": {"$ref": "#/components/schemas/OfferOffererResponse"},
                        "postalCode": {"nullable": True, "title": "Postalcode", "type": "string"},
                        "publicName": {"nullable": True, "title": "Publicname", "type": "string"},
                    },
                    "required": ["id", "offerer", "name", "coordinates", "isPermanent"],
                    "title": "OfferVenueResponse",
                    "type": "object",
                },
                "OnlineOfflinePlatformChoicesEnum": {
                    "description": "An enumeration.",
                    "enum": ["OFFLINE", "ONLINE", "ONLINE_OR_OFFLINE"],
                    "title": "OnlineOfflinePlatformChoicesEnum",
                },
                "OnlineOfflinePlatformChoicesEnumv2": {
                    "description": "An enumeration.",
                    "enum": ["OFFLINE", "ONLINE", "ONLINE_OR_OFFLINE"],
                    "title": "OnlineOfflinePlatformChoicesEnumv2",
                },
                "PaginatedFavoritesResponse": {
                    "properties": {
                        "favorites": {
                            "items": {"$ref": "#/components/schemas/FavoriteResponse"},
                            "title": "Favorites",
                            "type": "array",
                        },
                        "nbFavorites": {"title": "Nbfavorites", "type": "integer"},
                        "page": {"title": "Page", "type": "integer"},
                    },
                    "required": ["page", "nbFavorites", "favorites"],
                    "title": "PaginatedFavoritesResponse",
                    "type": "object",
                },
                "PhoneValidationRemainingAttemptsRequest": {
                    "properties": {
                        "counterResetDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Counterresetdatetime",
                            "type": "string",
                        },
                        "remainingAttempts": {"title": "Remainingattempts", "type": "integer"},
                    },
                    "required": ["remainingAttempts"],
                    "title": "PhoneValidationRemainingAttemptsRequest",
                    "type": "object",
                },
                "PopOverIcon": {
                    "description": "An enumeration.",
                    "enum": ["INFO", "ERROR", "WARNING", "CLOCK", "FILE", "MAGNIFYING_GLASS"],
                    "title": "PopOverIcon",
                },
                "ProfileOptionsResponse": {
                    "properties": {
                        "activities": {
                            "items": {"$ref": "#/components/schemas/ActivityResponseModel"},
                            "title": "Activities",
                            "type": "array",
                        },
                        "school_types": {
                            "items": {"$ref": "#/components/schemas/SchoolTypeResponseModel"},
                            "title": "School Types",
                            "type": "array",
                        },
                    },
                    "required": ["activities", "school_types"],
                    "title": "ProfileOptionsResponse",
                    "type": "object",
                },
                "ProfileUpdateRequest": {
                    "properties": {
                        "activityId": {"$ref": "#/components/schemas/ActivityIdEnum"},
                        "address": {"title": "Address", "type": "string"},
                        "city": {"title": "City", "type": "string"},
                        "firstName": {"title": "Firstname", "type": "string"},
                        "lastName": {"title": "Lastname", "type": "string"},
                        "postalCode": {"title": "Postalcode", "type": "string"},
                        "schoolTypeId": {
                            "anyOf": [{"$ref": "#/components/schemas/SchoolTypesIdEnum"}],
                            "nullable": True,
                        },
                    },
                    "required": ["activityId", "address", "city", "firstName", "lastName", "postalCode"],
                    "title": "ProfileUpdateRequest",
                    "type": "object",
                },
                "Reason": {
                    "description": "\n    Describe possible reason codes to used when reporting an offer.\n\n    The whole meta part is only consumed by the api client, it has no meaning\n    inside the whole API code.\n\n    Note: when adding a new enum symbol, do not forget to update the meta\n    method.\n    ",
                    "enum": ["IMPROPER", "PRICE_TOO_HIGH", "INAPPROPRIATE", "OTHER"],
                    "title": "Reason",
                },
                "ReasonMeta": {
                    "properties": {
                        "description": {"title": "Description", "type": "string"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["description", "title"],
                    "title": "ReasonMeta",
                    "type": "object",
                },
                "RefreshResponse": {
                    "properties": {"accessToken": {"title": "Accesstoken", "type": "string"}},
                    "required": ["accessToken"],
                    "title": "RefreshResponse",
                    "type": "object",
                },
                "ReportedOffer": {
                    "properties": {
                        "offerId": {"title": "Offerid", "type": "integer"},
                        "reason": {"$ref": "#/components/schemas/Reason"},
                        "reportedAt": {"format": "date-time", "title": "Reportedat", "type": "string"},
                    },
                    "required": ["offerId", "reportedAt", "reason"],
                    "title": "ReportedOffer",
                    "type": "object",
                },
                "RequestPasswordResetRequest": {
                    "properties": {
                        "email": {"title": "Email", "type": "string"},
                        "token": {"nullable": True, "title": "Token", "type": "string"},
                    },
                    "required": ["email"],
                    "title": "RequestPasswordResetRequest",
                    "type": "object",
                },
                "ResendEmailValidationRequest": {
                    "properties": {"email": {"title": "Email", "type": "string"}},
                    "required": ["email"],
                    "title": "ResendEmailValidationRequest",
                    "type": "object",
                },
                "ResetPasswordRequest": {
                    "properties": {
                        "newPassword": {"title": "Newpassword", "type": "string"},
                        "resetPasswordToken": {"title": "Resetpasswordtoken", "type": "string"},
                    },
                    "required": ["resetPasswordToken", "newPassword"],
                    "title": "ResetPasswordRequest",
                    "type": "object",
                },
                "SchoolTypeResponseModel": {
                    "properties": {
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "id": {"$ref": "#/components/schemas/SchoolTypesIdEnum"},
                        "label": {"title": "Label", "type": "string"},
                    },
                    "required": ["id", "label"],
                    "title": "SchoolTypeResponseModel",
                    "type": "object",
                },
                "SchoolTypesIdEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "AGRICULTURAL_HIGH_SCHOOL",
                        "APPRENTICE_FORMATION_CENTER",
                        "MILITARY_HIGH_SCHOOL",
                        "HOME_OR_REMOTE_SCHOOLING",
                        "NAVAL_HIGH_SCHOOL",
                        "PRIVATE_HIGH_SCHOOL",
                        "PRIVATE_SECONDARY_SCHOOL",
                        "PUBLIC_HIGH_SCHOOL",
                        "PUBLIC_SECONDARY_SCHOOL",
                    ],
                    "title": "SchoolTypesIdEnum",
                },
                "SearchGroupNameEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "FILM",
                        "CINEMA",
                        "CONFERENCE",
                        "JEU",
                        "LIVRE",
                        "VISITE",
                        "MUSIQUE",
                        "COURS",
                        "PRESSE",
                        "SPECTACLE",
                        "INSTRUMENT",
                        "MATERIEL",
                        "CARTE_JEUNES",
                        "NONE",
                    ],
                    "title": "SearchGroupNameEnum",
                },
                "SearchGroupNameEnumv2": {
                    "description": "An enumeration.",
                    "enum": [
                        "ARTS_LOISIRS_CREATIFS",
                        "BIBLIOTHEQUES_MEDIATHEQUE",
                        "CARTES_JEUNES",
                        "CD_VINYLE_MUSIQUE_EN_LIGNE",
                        "CONCERTS_FESTIVALS",
                        "EVENEMENTS_EN_LIGNE",
                        "FILMS_SERIES_CINEMA",
                        "INSTRUMENTS",
                        "JEUX_JEUX_VIDEOS",
                        "LIVRES",
                        "MEDIA_PRESSE",
                        "MUSEES_VISITES_CULTURELLES",
                        "NONE",
                        "RENCONTRES_CONFERENCES",
                        "SPECTACLES",
                    ],
                    "title": "SearchGroupNameEnumv2",
                },
                "SearchGroupResponseModel": {
                    "properties": {
                        "name": {"$ref": "#/components/schemas/SearchGroupNameEnum"},
                        "value": {"nullable": True, "title": "Value", "type": "string"},
                    },
                    "required": ["name"],
                    "title": "SearchGroupResponseModel",
                    "type": "object",
                },
                "SearchGroupResponseModelv2": {
                    "properties": {
                        "name": {"$ref": "#/components/schemas/SearchGroupNameEnumv2"},
                        "value": {"nullable": True, "title": "Value", "type": "string"},
                    },
                    "required": ["name"],
                    "title": "SearchGroupResponseModelv2",
                    "type": "object",
                },
                "SendPhoneValidationRequest": {
                    "properties": {"phoneNumber": {"title": "Phonenumber", "type": "string"}},
                    "required": ["phoneNumber"],
                    "title": "SendPhoneValidationRequest",
                    "type": "object",
                },
                "SettingsResponse": {
                    "properties": {
                        "accountCreationMinimumAge": {"title": "Accountcreationminimumage", "type": "integer"},
                        "accountUnsuspensionLimit": {"title": "Accountunsuspensionlimit", "type": "integer"},
                        "appEnableAutocomplete": {"title": "Appenableautocomplete", "type": "boolean"},
                        "depositAmountsByAge": {
                            "allOf": [{"$ref": "#/components/schemas/DepositAmountsByAge"}],
                            "default": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
                            "title": "Depositamountsbyage",
                        },
                        "displayDmsRedirection": {"title": "Displaydmsredirection", "type": "boolean"},
                        "enableFrontImageResizing": {"title": "Enablefrontimageresizing", "type": "boolean"},
                        "enableNativeCulturalSurvey": {"title": "Enablenativeculturalsurvey", "type": "boolean"},
                        "enableNativeIdCheckVerboseDebugging": {
                            "title": "Enablenativeidcheckverbosedebugging",
                            "type": "boolean",
                        },
                        "enablePhoneValidation": {"title": "Enablephonevalidation", "type": "boolean"},
                        "idCheckAddressAutocompletion": {"title": "Idcheckaddressautocompletion", "type": "boolean"},
                        "isRecaptchaEnabled": {"title": "Isrecaptchaenabled", "type": "boolean"},
                        "objectStorageUrl": {"title": "Objectstorageurl", "type": "string"},
                        "proDisableEventsQrcode": {"title": "Prodisableeventsqrcode", "type": "boolean"},
                    },
                    "required": [
                        "accountCreationMinimumAge",
                        "appEnableAutocomplete",
                        "displayDmsRedirection",
                        "enableFrontImageResizing",
                        "enableNativeCulturalSurvey",
                        "enableNativeIdCheckVerboseDebugging",
                        "enablePhoneValidation",
                        "idCheckAddressAutocompletion",
                        "isRecaptchaEnabled",
                        "objectStorageUrl",
                        "proDisableEventsQrcode",
                        "accountUnsuspensionLimit",
                    ],
                    "title": "SettingsResponse",
                    "type": "object",
                },
                "SigninRequest": {
                    "properties": {
                        "deviceInfo": {
                            "anyOf": [{"$ref": "#/components/schemas/TrustedDevice"}],
                            "nullable": True,
                            "title": "TrustedDevice",
                        },
                        "identifier": {"title": "Identifier", "type": "string"},
                        "password": {"title": "Password", "type": "string"},
                    },
                    "required": ["identifier", "password"],
                    "title": "SigninRequest",
                    "type": "object",
                },
                "SigninResponse": {
                    "properties": {
                        "accessToken": {"title": "Accesstoken", "type": "string"},
                        "accountState": {"$ref": "#/components/schemas/AccountState"},
                        "refreshToken": {"title": "Refreshtoken", "type": "string"},
                    },
                    "required": ["refreshToken", "accessToken", "accountState"],
                    "title": "SigninResponse",
                    "type": "object",
                },
                "SubcategoriesResponseModel": {
                    "properties": {
                        "homepageLabels": {
                            "items": {"$ref": "#/components/schemas/HomepageLabelResponseModel"},
                            "title": "Homepagelabels",
                            "type": "array",
                        },
                        "searchGroups": {
                            "items": {"$ref": "#/components/schemas/SearchGroupResponseModel"},
                            "title": "Searchgroups",
                            "type": "array",
                        },
                        "subcategories": {
                            "items": {"$ref": "#/components/schemas/SubcategoryResponseModel"},
                            "title": "Subcategories",
                            "type": "array",
                        },
                    },
                    "required": ["subcategories", "searchGroups", "homepageLabels"],
                    "title": "SubcategoriesResponseModel",
                    "type": "object",
                },
                "SubcategoriesResponseModelv2": {
                    "properties": {
                        "genreTypes": {
                            "items": {"$ref": "#/components/schemas/GenreTypeModel"},
                            "title": "Genretypes",
                            "type": "array",
                        },
                        "homepageLabels": {
                            "items": {"$ref": "#/components/schemas/HomepageLabelResponseModelv2"},
                            "title": "Homepagelabels",
                            "type": "array",
                        },
                        "nativeCategories": {
                            "items": {"$ref": "#/components/schemas/NativeCategoryResponseModelv2"},
                            "title": "Nativecategories",
                            "type": "array",
                        },
                        "searchGroups": {
                            "items": {"$ref": "#/components/schemas/SearchGroupResponseModelv2"},
                            "title": "Searchgroups",
                            "type": "array",
                        },
                        "subcategories": {
                            "items": {"$ref": "#/components/schemas/SubcategoryResponseModelv2"},
                            "title": "Subcategories",
                            "type": "array",
                        },
                    },
                    "required": ["subcategories", "searchGroups", "homepageLabels", "nativeCategories", "genreTypes"],
                    "title": "SubcategoriesResponseModelv2",
                    "type": "object",
                },
                "SubcategoryIdEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "ABO_BIBLIOTHEQUE",
                        "ABO_CONCERT",
                        "ABO_JEU_VIDEO",
                        "ABO_LIVRE_NUMERIQUE",
                        "ABO_LUDOTHEQUE",
                        "ABO_MEDIATHEQUE",
                        "ABO_MUSEE",
                        "ABO_PLATEFORME_MUSIQUE",
                        "ABO_PLATEFORME_VIDEO",
                        "ABO_PRATIQUE_ART",
                        "ABO_PRESSE_EN_LIGNE",
                        "ABO_SPECTACLE",
                        "ACHAT_INSTRUMENT",
                        "ACTIVATION_EVENT",
                        "ACTIVATION_THING",
                        "APP_CULTURELLE",
                        "ATELIER_PRATIQUE_ART",
                        "AUTRE_SUPPORT_NUMERIQUE",
                        "BON_ACHAT_INSTRUMENT",
                        "CAPTATION_MUSIQUE",
                        "CARTE_CINE_ILLIMITE",
                        "CARTE_CINE_MULTISEANCES",
                        "CARTE_JEUNES",
                        "CARTE_MUSEE",
                        "CINE_PLEIN_AIR",
                        "CINE_VENTE_DISTANCE",
                        "CONCERT",
                        "CONCOURS",
                        "CONFERENCE",
                        "DECOUVERTE_METIERS",
                        "ESCAPE_GAME",
                        "EVENEMENT_CINE",
                        "EVENEMENT_JEU",
                        "EVENEMENT_MUSIQUE",
                        "EVENEMENT_PATRIMOINE",
                        "FESTIVAL_ART_VISUEL",
                        "FESTIVAL_CINE",
                        "FESTIVAL_LIVRE",
                        "FESTIVAL_MUSIQUE",
                        "FESTIVAL_SPECTACLE",
                        "JEU_EN_LIGNE",
                        "JEU_SUPPORT_PHYSIQUE",
                        "LIVESTREAM_EVENEMENT",
                        "LIVESTREAM_MUSIQUE",
                        "LIVESTREAM_PRATIQUE_ARTISTIQUE",
                        "LIVRE_AUDIO_PHYSIQUE",
                        "LIVRE_NUMERIQUE",
                        "LIVRE_PAPIER",
                        "LOCATION_INSTRUMENT",
                        "MATERIEL_ART_CREATIF",
                        "MUSEE_VENTE_DISTANCE",
                        "OEUVRE_ART",
                        "PARTITION",
                        "PLATEFORME_PRATIQUE_ARTISTIQUE",
                        "PRATIQUE_ART_VENTE_DISTANCE",
                        "PODCAST",
                        "RENCONTRE_EN_LIGNE",
                        "RENCONTRE_JEU",
                        "RENCONTRE",
                        "SALON",
                        "SEANCE_CINE",
                        "SEANCE_ESSAI_PRATIQUE_ART",
                        "SPECTACLE_ENREGISTRE",
                        "SPECTACLE_REPRESENTATION",
                        "SPECTACLE_VENTE_DISTANCE",
                        "SUPPORT_PHYSIQUE_FILM",
                        "SUPPORT_PHYSIQUE_MUSIQUE",
                        "TELECHARGEMENT_LIVRE_AUDIO",
                        "TELECHARGEMENT_MUSIQUE",
                        "VISITE_GUIDEE",
                        "VISITE_VIRTUELLE",
                        "VISITE",
                        "VOD",
                    ],
                    "title": "SubcategoryIdEnum",
                },
                "SubcategoryIdEnumv2": {
                    "description": "An enumeration.",
                    "enum": [
                        "ABO_BIBLIOTHEQUE",
                        "ABO_CONCERT",
                        "ABO_JEU_VIDEO",
                        "ABO_LIVRE_NUMERIQUE",
                        "ABO_LUDOTHEQUE",
                        "ABO_MEDIATHEQUE",
                        "ABO_MUSEE",
                        "ABO_PLATEFORME_MUSIQUE",
                        "ABO_PLATEFORME_VIDEO",
                        "ABO_PRATIQUE_ART",
                        "ABO_PRESSE_EN_LIGNE",
                        "ABO_SPECTACLE",
                        "ACHAT_INSTRUMENT",
                        "ACTIVATION_EVENT",
                        "ACTIVATION_THING",
                        "APP_CULTURELLE",
                        "ATELIER_PRATIQUE_ART",
                        "AUTRE_SUPPORT_NUMERIQUE",
                        "BON_ACHAT_INSTRUMENT",
                        "CAPTATION_MUSIQUE",
                        "CARTE_CINE_ILLIMITE",
                        "CARTE_CINE_MULTISEANCES",
                        "CARTE_JEUNES",
                        "CARTE_MUSEE",
                        "CINE_PLEIN_AIR",
                        "CINE_VENTE_DISTANCE",
                        "CONCERT",
                        "CONCOURS",
                        "CONFERENCE",
                        "DECOUVERTE_METIERS",
                        "ESCAPE_GAME",
                        "EVENEMENT_CINE",
                        "EVENEMENT_JEU",
                        "EVENEMENT_MUSIQUE",
                        "EVENEMENT_PATRIMOINE",
                        "FESTIVAL_ART_VISUEL",
                        "FESTIVAL_CINE",
                        "FESTIVAL_LIVRE",
                        "FESTIVAL_MUSIQUE",
                        "FESTIVAL_SPECTACLE",
                        "JEU_EN_LIGNE",
                        "JEU_SUPPORT_PHYSIQUE",
                        "LIVESTREAM_EVENEMENT",
                        "LIVESTREAM_MUSIQUE",
                        "LIVESTREAM_PRATIQUE_ARTISTIQUE",
                        "LIVRE_AUDIO_PHYSIQUE",
                        "LIVRE_NUMERIQUE",
                        "LIVRE_PAPIER",
                        "LOCATION_INSTRUMENT",
                        "MATERIEL_ART_CREATIF",
                        "MUSEE_VENTE_DISTANCE",
                        "OEUVRE_ART",
                        "PARTITION",
                        "PLATEFORME_PRATIQUE_ARTISTIQUE",
                        "PRATIQUE_ART_VENTE_DISTANCE",
                        "PODCAST",
                        "RENCONTRE_EN_LIGNE",
                        "RENCONTRE_JEU",
                        "RENCONTRE",
                        "SALON",
                        "SEANCE_CINE",
                        "SEANCE_ESSAI_PRATIQUE_ART",
                        "SPECTACLE_ENREGISTRE",
                        "SPECTACLE_REPRESENTATION",
                        "SPECTACLE_VENTE_DISTANCE",
                        "SUPPORT_PHYSIQUE_FILM",
                        "SUPPORT_PHYSIQUE_MUSIQUE",
                        "TELECHARGEMENT_LIVRE_AUDIO",
                        "TELECHARGEMENT_MUSIQUE",
                        "VISITE_GUIDEE",
                        "VISITE_VIRTUELLE",
                        "VISITE",
                        "VOD",
                    ],
                    "title": "SubcategoryIdEnumv2",
                },
                "SubcategoryResponseModel": {
                    "properties": {
                        "appLabel": {"title": "Applabel", "type": "string"},
                        "categoryId": {"$ref": "#/components/schemas/CategoryIdEnum"},
                        "homepageLabelName": {"$ref": "#/components/schemas/_HomepageLabelNameEnum"},
                        "id": {"$ref": "#/components/schemas/SubcategoryIdEnum"},
                        "isEvent": {"title": "Isevent", "type": "boolean"},
                        "onlineOfflinePlatform": {"$ref": "#/components/schemas/OnlineOfflinePlatformChoicesEnum"},
                        "searchGroupName": {"$ref": "#/components/schemas/SearchGroupNameEnum"},
                    },
                    "required": [
                        "id",
                        "categoryId",
                        "appLabel",
                        "searchGroupName",
                        "homepageLabelName",
                        "isEvent",
                        "onlineOfflinePlatform",
                    ],
                    "title": "SubcategoryResponseModel",
                    "type": "object",
                },
                "SubcategoryResponseModelv2": {
                    "properties": {
                        "appLabel": {"title": "Applabel", "type": "string"},
                        "categoryId": {"$ref": "#/components/schemas/CategoryIdEnum"},
                        "homepageLabelName": {"$ref": "#/components/schemas/_HomepageLabelNameEnumv2"},
                        "id": {"$ref": "#/components/schemas/SubcategoryIdEnumv2"},
                        "isEvent": {"title": "Isevent", "type": "boolean"},
                        "nativeCategoryId": {"$ref": "#/components/schemas/NativeCategoryIdEnumv2"},
                        "onlineOfflinePlatform": {"$ref": "#/components/schemas/OnlineOfflinePlatformChoicesEnumv2"},
                        "searchGroupName": {"$ref": "#/components/schemas/SearchGroupNameEnumv2"},
                    },
                    "required": [
                        "id",
                        "categoryId",
                        "nativeCategoryId",
                        "appLabel",
                        "searchGroupName",
                        "homepageLabelName",
                        "isEvent",
                        "onlineOfflinePlatform",
                    ],
                    "title": "SubcategoryResponseModelv2",
                    "type": "object",
                },
                "SubscriptionMessage": {
                    "properties": {
                        "callToAction": {
                            "anyOf": [{"$ref": "#/components/schemas/CallToActionMessage"}],
                            "nullable": True,
                            "title": "CallToActionMessage",
                        },
                        "popOverIcon": {"anyOf": [{"$ref": "#/components/schemas/PopOverIcon"}], "nullable": True},
                        "updatedAt": {"format": "date-time", "nullable": True, "title": "Updatedat", "type": "string"},
                        "userMessage": {"title": "Usermessage", "type": "string"},
                    },
                    "required": ["userMessage"],
                    "title": "SubscriptionMessage",
                    "type": "object",
                },
                "SubscriptionStatus": {
                    "description": "An enumeration.",
                    "enum": ["has_to_complete_subscription", "has_subscription_pending", "has_subscription_issues"],
                    "title": "SubscriptionStatus",
                },
                "SubscriptionStep": {
                    "description": "An enumeration.",
                    "enum": [
                        "email-validation",
                        "maintenance",
                        "phone-validation",
                        "profile-completion",
                        "identity-check",
                        "honor-statement",
                    ],
                    "title": "SubscriptionStep",
                },
                "SubscriptionStepCompletionState": {
                    "description": "An enumeration.",
                    "enum": ["completed", "current", "disabled", "retry"],
                    "title": "SubscriptionStepCompletionState",
                },
                "SubscriptionStepDetailsResponse": {
                    "properties": {
                        "completionState": {"$ref": "#/components/schemas/SubscriptionStepCompletionState"},
                        "name": {"$ref": "#/components/schemas/SubscriptionStep"},
                        "subtitle": {"nullable": True, "title": "Subtitle", "type": "string"},
                        "title": {"$ref": "#/components/schemas/SubscriptionStepTitle"},
                    },
                    "required": ["name", "title", "completionState"],
                    "title": "SubscriptionStepDetailsResponse",
                    "type": "object",
                },
                "SubscriptionStepTitle": {
                    "description": "An enumeration.",
                    "enum": ["Numéro de téléphone", "Profil", "Identification", "Confirmation"],
                    "title": "SubscriptionStepTitle",
                },
                "SubscriptionStepperResponse": {
                    "properties": {
                        "allowedIdentityCheckMethods": {
                            "items": {"$ref": "#/components/schemas/IdentityCheckMethod"},
                            "type": "array",
                        },
                        "errorMessage": {"nullable": True, "title": "Errormessage", "type": "string"},
                        "subscriptionStepsToDisplay": {
                            "items": {"$ref": "#/components/schemas/SubscriptionStepDetailsResponse"},
                            "title": "Subscriptionstepstodisplay",
                            "type": "array",
                        },
                        "subtitle": {"nullable": True, "title": "Subtitle", "type": "string"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["subscriptionStepsToDisplay", "allowedIdentityCheckMethods", "title"],
                    "title": "SubscriptionStepperResponse",
                    "type": "object",
                },
                "TrustedDevice": {
                    "properties": {
                        "deviceId": {"title": "Deviceid", "type": "string"},
                        "os": {"nullable": True, "title": "Os", "type": "string"},
                        "source": {"nullable": True, "title": "Source", "type": "string"},
                    },
                    "required": ["deviceId"],
                    "title": "TrustedDevice",
                    "type": "object",
                },
                "UpdateEmailTokenExpiration": {
                    "properties": {
                        "expiration": {"format": "date-time", "nullable": True, "title": "Expiration", "type": "string"}
                    },
                    "title": "UpdateEmailTokenExpiration",
                    "type": "object",
                },
                "UserProfileEmailUpdate": {
                    "properties": {
                        "email": {"format": "email", "title": "Email", "type": "string"},
                        "password": {"minLength": 8, "title": "Password", "type": "string"},
                    },
                    "required": ["email", "password"],
                    "title": "UserProfileEmailUpdate",
                    "type": "object",
                },
                "UserProfileResponse": {
                    "properties": {
                        "birthDate": {"format": "date", "nullable": True, "title": "Birthdate", "type": "string"},
                        "bookedOffers": {
                            "additionalProperties": {"type": "integer"},
                            "title": "Bookedoffers",
                            "type": "object",
                        },
                        "dateOfBirth": {"format": "date", "nullable": True, "title": "Dateofbirth", "type": "string"},
                        "depositExpirationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Depositexpirationdate",
                            "type": "string",
                        },
                        "depositType": {"anyOf": [{"$ref": "#/components/schemas/DepositType"}], "nullable": True},
                        "domainsCredit": {
                            "anyOf": [{"$ref": "#/components/schemas/DomainsCredit"}],
                            "nullable": True,
                            "title": "DomainsCredit",
                        },
                        "eligibility": {"anyOf": [{"$ref": "#/components/schemas/EligibilityType"}], "nullable": True},
                        "eligibilityEndDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Eligibilityenddatetime",
                            "type": "string",
                        },
                        "eligibilityStartDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Eligibilitystartdatetime",
                            "type": "string",
                        },
                        "email": {"title": "Email", "type": "string"},
                        "firstName": {"nullable": True, "title": "Firstname", "type": "string"},
                        "id": {"title": "Id", "type": "integer"},
                        "isBeneficiary": {"title": "Isbeneficiary", "type": "boolean"},
                        "isEligibleForBeneficiaryUpgrade": {
                            "title": "Iseligibleforbeneficiaryupgrade",
                            "type": "boolean",
                        },
                        "lastName": {"nullable": True, "title": "Lastname", "type": "string"},
                        "needsToFillCulturalSurvey": {"title": "Needstofillculturalsurvey", "type": "boolean"},
                        "phoneNumber": {"nullable": True, "title": "Phonenumber", "type": "string"},
                        "recreditAmountToShow": {"nullable": True, "title": "Recreditamounttoshow", "type": "integer"},
                        "requiresIdCheck": {"title": "Requiresidcheck", "type": "boolean"},
                        "roles": {"items": {"$ref": "#/components/schemas/UserRole"}, "type": "array"},
                        "showEligibleCard": {"title": "Showeligiblecard", "type": "boolean"},
                        "status": {"$ref": "#/components/schemas/YoungStatusResponse"},
                        "subscriptionMessage": {
                            "anyOf": [{"$ref": "#/components/schemas/SubscriptionMessage"}],
                            "nullable": True,
                            "title": "SubscriptionMessage",
                        },
                        "subscriptions": {"$ref": "#/components/schemas/NotificationSubscriptions"},
                    },
                    "required": [
                        "bookedOffers",
                        "email",
                        "id",
                        "isBeneficiary",
                        "isEligibleForBeneficiaryUpgrade",
                        "needsToFillCulturalSurvey",
                        "requiresIdCheck",
                        "roles",
                        "showEligibleCard",
                        "subscriptions",
                        "status",
                    ],
                    "title": "UserProfileResponse",
                    "type": "object",
                },
                "UserProfileUpdateRequest": {
                    "properties": {
                        "subscriptions": {
                            "anyOf": [{"$ref": "#/components/schemas/NotificationSubscriptions"}],
                            "nullable": True,
                            "title": "NotificationSubscriptions",
                        }
                    },
                    "title": "UserProfileUpdateRequest",
                    "type": "object",
                },
                "UserReportedOffersResponse": {
                    "properties": {
                        "reportedOffers": {
                            "items": {"$ref": "#/components/schemas/ReportedOffer"},
                            "title": "Reportedoffers",
                            "type": "array",
                        }
                    },
                    "required": ["reportedOffers"],
                    "title": "UserReportedOffersResponse",
                    "type": "object",
                },
                "UserRole": {
                    "description": "An enumeration.",
                    "enum": ["ADMIN", "BENEFICIARY", "PRO", "NON_ATTACHED_PRO", "UNDERAGE_BENEFICIARY", "TEST"],
                    "title": "UserRole",
                },
                "UserSuspensionDateResponse": {
                    "properties": {
                        "date": {"format": "date-time", "nullable": True, "title": "Date", "type": "string"}
                    },
                    "title": "UserSuspensionDateResponse",
                    "type": "object",
                },
                "UserSuspensionStatusResponse": {
                    "properties": {"status": {"$ref": "#/components/schemas/AccountState"}},
                    "required": ["status"],
                    "title": "UserSuspensionStatusResponse",
                    "type": "object",
                },
                "ValidateEmailRequest": {
                    "properties": {"emailValidationToken": {"title": "Emailvalidationtoken", "type": "string"}},
                    "required": ["emailValidationToken"],
                    "title": "ValidateEmailRequest",
                    "type": "object",
                },
                "ValidateEmailResponse": {
                    "properties": {
                        "accessToken": {"title": "Accesstoken", "type": "string"},
                        "refreshToken": {"title": "Refreshtoken", "type": "string"},
                    },
                    "required": ["accessToken", "refreshToken"],
                    "title": "ValidateEmailResponse",
                    "type": "object",
                },
                "ValidatePhoneNumberRequest": {
                    "properties": {"code": {"title": "Code", "type": "string"}},
                    "required": ["code"],
                    "title": "ValidatePhoneNumberRequest",
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
                "VenueAccessibilityModel": {
                    "properties": {
                        "audioDisability": {"nullable": True, "title": "Audiodisability", "type": "boolean"},
                        "mentalDisability": {"nullable": True, "title": "Mentaldisability", "type": "boolean"},
                        "motorDisability": {"nullable": True, "title": "Motordisability", "type": "boolean"},
                        "visualDisability": {"nullable": True, "title": "Visualdisability", "type": "boolean"},
                    },
                    "title": "VenueAccessibilityModel",
                    "type": "object",
                },
                "VenueContactModel": {
                    "additionalProperties": False,
                    "properties": {
                        "email": {"format": "email", "nullable": True, "title": "Email", "type": "string"},
                        "phoneNumber": {"nullable": True, "title": "Phonenumber", "type": "string"},
                        "socialMedias": {
                            "additionalProperties": {
                                "format": "uri",
                                "maxLength": 2083,
                                "minLength": 1,
                                "type": "string",
                            },
                            "nullable": True,
                            "title": "Socialmedias",
                            "type": "object",
                        },
                        "website": {"nullable": True, "title": "Website", "type": "string"},
                    },
                    "title": "VenueContactModel",
                    "type": "object",
                },
                "VenueResponse": {
                    "properties": {
                        "accessibility": {"$ref": "#/components/schemas/VenueAccessibilityModel"},
                        "address": {"nullable": True, "title": "Address", "type": "string"},
                        "bannerMeta": {"anyOf": [{"$ref": "#/components/schemas/BannerMetaModel"}], "nullable": True},
                        "bannerUrl": {"nullable": True, "title": "Bannerurl", "type": "string"},
                        "city": {"nullable": True, "title": "City", "type": "string"},
                        "contact": {
                            "anyOf": [{"$ref": "#/components/schemas/VenueContactModel"}],
                            "nullable": True,
                            "title": "VenueContactModel",
                        },
                        "description": {"maxLength": 1000, "nullable": True, "title": "Description", "type": "string"},
                        "id": {"title": "Id", "type": "integer"},
                        "isPermanent": {"nullable": True, "title": "Ispermanent", "type": "boolean"},
                        "isVirtual": {"title": "Isvirtual", "type": "boolean"},
                        "latitude": {"nullable": True, "title": "Latitude", "type": "number"},
                        "longitude": {"nullable": True, "title": "Longitude", "type": "number"},
                        "name": {"title": "Name", "type": "string"},
                        "postalCode": {"nullable": True, "title": "Postalcode", "type": "string"},
                        "publicName": {"nullable": True, "title": "Publicname", "type": "string"},
                        "venueTypeCode": {"$ref": "#/components/schemas/VenueTypeCodeKey"},
                        "withdrawalDetails": {"nullable": True, "title": "Withdrawaldetails", "type": "string"},
                    },
                    "required": ["isVirtual", "name", "id", "accessibility", "venueTypeCode"],
                    "title": "VenueResponse",
                    "type": "object",
                },
                "VenueTypeCodeKey": {
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
                    "title": "VenueTypeCodeKey",
                },
                "WithdrawalTypeEnum": {
                    "description": "An enumeration.",
                    "enum": ["by_email", "no_ticket", "on_site"],
                    "title": "WithdrawalTypeEnum",
                },
                "YoungStatusResponse": {
                    "properties": {
                        "statusType": {"$ref": "#/components/schemas/YoungStatusType"},
                        "subscriptionStatus": {
                            "anyOf": [{"$ref": "#/components/schemas/SubscriptionStatus"}],
                            "nullable": True,
                        },
                    },
                    "required": ["statusType"],
                    "title": "YoungStatusResponse",
                    "type": "object",
                },
                "YoungStatusType": {
                    "description": "An enumeration.",
                    "enum": ["eligible", "non_eligible", "beneficiary", "ex_beneficiary", "suspended"],
                    "title": "YoungStatusType",
                },
                "_HomepageLabelNameEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "FILM",
                        "CINEMA",
                        "CONFERENCE",
                        "JEU",
                        "LIVRE",
                        "VISITE",
                        "MUSIQUE",
                        "COURS",
                        "PRESSE",
                        "SPECTACLE",
                        "MATERIEL",
                        "CARTE_JEUNES",
                        "NONE",
                    ],
                    "title": "(HomepageLabelNameEnum",
                },
                "_HomepageLabelNameEnumv2": {
                    "description": "An enumeration.",
                    "enum": [
                        "BEAUX_ARTS",
                        "CARTE_JEUNES",
                        "CINEMA",
                        "CONCERT",
                        "COURS",
                        "FESTIVAL",
                        "FILMS",
                        "INSTRUMENT",
                        "JEUX",
                        "LIVRES",
                        "MEDIAS",
                        "MUSEE",
                        "MUSIQUE",
                        "NONE",
                        "PLATEFORME",
                        "RENCONTRES",
                        "SPECTACLES",
                        "VISITES",
                    ],
                    "title": "(HomepageLabelNameEnumv2",
                },
            },
            "securitySchemes": {"JWTAuth": {"bearerFormat": "JWT", "scheme": "bearer", "type": "http"}},
        },
        "info": {"title": "Service API Document", "version": "0.1.0"},
        "openapi": "3.0.3",
        "paths": {
            "/native/v1/account": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/account",
                    "parameters": [],
                    "requestBody": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AccountRequest"}}}
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "create_account <POST>",
                    "tags": [],
                }
            },
            "/native/v1/account/suspend": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/account/suspend",
                    "parameters": [],
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "suspend_account <POST>",
                    "tags": [],
                }
            },
            "/native/v1/account/suspend/token_validation/{token}": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/account/suspend/token_validation/{token}",
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
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "account_suspension_token_validation <GET>",
                    "tags": [],
                }
            },
            "/native/v1/account/suspension_date": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/account/suspension_date",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UserSuspensionDateResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_account_suspension_date <GET>",
                    "tags": [],
                }
            },
            "/native/v1/account/suspension_status": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/account/suspension_status",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UserSuspensionStatusResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_account_suspension_status <GET>",
                    "tags": [],
                }
            },
            "/native/v1/account/unsuspend": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/account/unsuspend",
                    "parameters": [],
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "unsuspend_account <POST>",
                    "tags": [],
                }
            },
            "/native/v1/banner": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/banner",
                    "parameters": [
                        {
                            "description": "",
                            "in": "query",
                            "name": "isGeolocated",
                            "required": False,
                            "schema": {"default": False, "title": "Isgeolocated", "type": "boolean"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/BannerResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_banner <GET>",
                    "tags": [],
                }
            },
            "/native/v1/bookings": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/bookings",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/BookingsResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_bookings <GET>",
                    "tags": [],
                },
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/bookings",
                    "parameters": [],
                    "requestBody": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BookOfferRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/BookOfferResponse"}}
                            },
                            "description": "OK",
                        },
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "book_offer <POST>",
                    "tags": [],
                },
            },
            "/native/v1/bookings/{booking_id}/cancel": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/bookings/{booking_id}/cancel",
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
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not Found"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "cancel_booking <POST>",
                    "tags": [],
                }
            },
            "/native/v1/bookings/{booking_id}/toggle_display": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/bookings/{booking_id}/toggle_display",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "booking_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/BookingDisplayStatusRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "flag_booking_as_used <POST>",
                    "tags": [],
                }
            },
            "/native/v1/change_password": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/change_password",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ChangePasswordRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "change_password <POST>",
                    "tags": [],
                }
            },
            "/native/v1/cookies_consent": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/cookies_consent",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/CookieConsentRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "cookies_consent <POST>",
                    "tags": [],
                }
            },
            "/native/v1/cultural_survey/answers": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/cultural_survey/answers",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CulturalSurveyAnswersRequest"}
                            }
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "post_cultural_survey_answers <POST>",
                    "tags": [],
                }
            },
            "/native/v1/cultural_survey/questions": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/cultural_survey/questions",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CulturalSurveyQuestionsResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_cultural_survey_questions <GET>",
                    "tags": [],
                }
            },
            "/native/v1/me": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/me",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/UserProfileResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_user_profile <GET>",
                    "tags": [],
                }
            },
            "/native/v1/me/favorites": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/me/favorites",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PaginatedFavoritesResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_favorites <GET>",
                    "tags": [],
                },
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/me/favorites",
                    "parameters": [],
                    "requestBody": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FavoriteRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/FavoriteResponse"}}
                            },
                            "description": "OK",
                        },
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "create_favorite <POST>",
                    "tags": [],
                },
            },
            "/native/v1/me/favorites/count": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/me/favorites/count",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/FavoritesCountResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_favorites_count <GET>",
                    "tags": [],
                }
            },
            "/native/v1/me/favorites/{favorite_id}": {
                "delete": {
                    "description": "",
                    "operationId": "delete_/native/v1/me/favorites/{favorite_id}",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "favorite_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        }
                    ],
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "delete_favorite <DELETE>",
                    "tags": [],
                }
            },
            "/native/v1/offer/report/reasons": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/offer/report/reasons",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/OfferReportReasons"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "report_offer_reasons <GET>",
                    "tags": [],
                }
            },
            "/native/v1/offer/{offer_id}": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/offer/{offer_id}",
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
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OfferResponse"}}},
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not Found"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "get_offer <GET>",
                    "tags": [],
                }
            },
            "/native/v1/offer/{offer_id}/report": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/offer/{offer_id}/report",
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
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OfferReportRequest"}}}
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "report_offer <POST>",
                    "tags": [],
                }
            },
            "/native/v1/offers/reports": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/offers/reports",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UserReportedOffersResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "user_reported_offers <GET>",
                    "tags": [],
                }
            },
            "/native/v1/phone_validation/remaining_attempts": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/phone_validation/remaining_attempts",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PhoneValidationRemainingAttemptsRequest"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "phone_validation_remaining_attempts <GET>",
                    "tags": [],
                }
            },
            "/native/v1/profile": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/profile",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/UserProfileUpdateRequest"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/UserProfileResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "update_user_profile <POST>",
                    "tags": [],
                }
            },
            "/native/v1/profile/email_update/status": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/profile/email_update/status",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/EmailUpdateStatus"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ValidationError"},
                                },
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_email_update_status <GET>",
                    "tags": [],
                },
            },
            "/native/v1/profile/token_expiration": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/profile/token_expiration",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UpdateEmailTokenExpiration"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_email_update_token_expiration_date <GET>",
                    "tags": [],
                }
            },
            "/native/v1/profile/update_email": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/profile/update_email",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/UserProfileEmailUpdate"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "update_user_email <POST>",
                    "tags": [],
                }
            },
            "/native/v1/profile/email_update/confirm": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/profile/email_update/confirm",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ChangeBeneficiaryEmailBody"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "confirm_email_update <POST>",
                    "tags": [],
                }
            },
            "/native/v1/profile/email_update/validate": {
                "put": {
                    "description": "",
                    "operationId": "put_/native/v1/profile/email_update/validate",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ChangeBeneficiaryEmailBody"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "validate_user_email <PUT>",
                    "tags": [],
                }
            },
            "/native/v1/refresh_access_token": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/refresh_access_token",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/RefreshResponse"}}
                            },
                            "description": "OK",
                        },
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "refresh <POST>",
                    "tags": [],
                }
            },
            "/native/v1/request_password_reset": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/request_password_reset",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/RequestPasswordResetRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "request_password_reset <POST>",
                    "tags": [],
                }
            },
            "/native/v1/resend_email_validation": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/resend_email_validation",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ResendEmailValidationRequest"}
                            }
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "resend_email_validation <POST>",
                    "tags": [],
                }
            },
            "/native/v1/reset_password": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/reset_password",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ResetPasswordRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "reset_password <POST>",
                    "tags": [],
                }
            },
            "/native/v1/reset_recredit_amount_to_show": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/reset_recredit_amount_to_show",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/UserProfileResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "reset_recredit_amount_to_show <POST>",
                    "tags": [],
                }
            },
            "/native/v1/send_offer_link_by_push/{offer_id}": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/send_offer_link_by_push/{offer_id}",
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
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "send_offer_link_by_push <POST>",
                    "tags": [],
                }
            },
            "/native/v1/send_offer_webapp_link_by_email/{offer_id}": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/send_offer_webapp_link_by_email/{offer_id}",
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
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "On iOS native app, users cannot book numeric offers with price > 0, so give them webapp link.",
                    "tags": [],
                }
            },
            "/native/v1/send_phone_validation_code": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/send_phone_validation_code",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/SendPhoneValidationRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "send_phone_validation_code <POST>",
                    "tags": [],
                }
            },
            "/native/v1/settings": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/settings",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/SettingsResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "get_settings <GET>",
                    "tags": [],
                }
            },
            "/native/v1/signin": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/signin",
                    "parameters": [],
                    "requestBody": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SigninRequest"}}}
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/SigninResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "signin <POST>",
                    "tags": [],
                }
            },
            "/native/v1/subcategories": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/subcategories",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SubcategoriesResponseModel"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "get_subcategories <GET>",
                    "tags": [],
                }
            },
            "/native/v1/subcategories/v2": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/subcategories/v2",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SubcategoriesResponseModelv2"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "get_subcategories_v2 <GET>",
                    "tags": [],
                }
            },
            "/native/v1/subscription/honor_statement": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/subscription/honor_statement",
                    "parameters": [],
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "create_honor_statement_fraud_check <POST>",
                    "tags": [],
                }
            },
            "/native/v1/subscription/next_step": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/subscription/next_step",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/NextSubscriptionStepResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "next_subscription_step <GET>",
                    "tags": [],
                }
            },
            "/native/v1/subscription/profile": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/subscription/profile",
                    "parameters": [],
                    "responses": {
                        "200": {"description": "OK"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not Found"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_profile <GET>",
                    "tags": [],
                },
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/subscription/profile",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ProfileUpdateRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "complete_profile <POST>",
                    "tags": [],
                },
            },
            "/native/v1/subscription/profile_options": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/subscription/profile_options",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ProfileOptionsResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "get_profile_options <GET>",
                    "tags": [],
                }
            },
            "/native/v1/subscription/stepper": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/subscription/stepper",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SubscriptionStepperResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_subscription_stepper <GET>",
                    "tags": [],
                }
            },
            "/native/v1/ubble_identification": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/ubble_identification",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/IdentificationSessionRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/IdentificationSessionResponse"}
                                }
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "start_identification_session <POST>",
                    "tags": [],
                }
            },
            "/native/v1/validate_email": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/validate_email",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ValidateEmailRequest"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidateEmailResponse"}}
                            },
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "validate_email <POST>",
                    "tags": [],
                }
            },
            "/native/v1/validate_phone_number": {
                "post": {
                    "description": "",
                    "operationId": "post_/native/v1/validate_phone_number",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ValidatePhoneNumberRequest"}}
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "validate_phone_number <POST>",
                    "tags": [],
                }
            },
            "/native/v1/venue/{venue_id}": {
                "get": {
                    "description": "",
                    "operationId": "get_/native/v1/venue/{venue_id}",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "venue_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/VenueResponse"}}},
                            "description": "OK",
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not Found"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "get_venue <GET>",
                    "tags": [],
                }
            },
        },
        "security": [],
        "tags": [],
    }
    got_lines = json.dumps(response.json, indent=2, sort_keys=True).splitlines()
    expected_lines = json.dumps(expected, indent=2, sort_keys=True).splitlines()
    diff = "\n".join(difflib.unified_diff(got_lines, expected_lines))
    assert response.json == expected, f"Got diff from expected schema: {diff}"
