import difflib
import json


def test_public_api(client):
    response = client.get("/native/openapi.json")
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
                        "firebasePseudoId": {"nullable": True, "title": "Firebasepseudoid", "type": "string"},
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
                    "required": ["birthdate", "token", "email", "password"],
                    "title": "AccountRequest",
                    "type": "object",
                },
                "AccountState": {
                    "description": "An enumeration.",
                    "enum": [
                        "ACTIVE",
                        "ANONYMIZED",
                        "INACTIVE",
                        "SUSPENDED",
                        "SUSPENDED_UPON_USER_REQUEST",
                        "SUSPICIOUS_LOGIN_REPORTED_BY_USER",
                        "DELETED",
                    ],
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
                        "description": {"nullable": True, "title": "Description", "type": "string"},
                        "id": {"$ref": "#/components/schemas/ActivityIdEnum"},
                        "label": {"title": "Label", "type": "string"},
                    },
                    "required": ["id", "label"],
                    "title": "ActivityResponseModel",
                    "type": "object",
                },
                "ActivityTypesResponse": {
                    "properties": {
                        "activities": {
                            "items": {"$ref": "#/components/schemas/ActivityResponseModel"},
                            "title": "Activities",
                            "type": "array",
                        }
                    },
                    "required": ["activities"],
                    "title": "ActivityTypesResponse",
                    "type": "object",
                },
                "AudioDisabilityModel": {
                    "properties": {
                        "deafAndHardOfHearing": {
                            "default": ["Non renseigné"],
                            "items": {"type": "string"},
                            "title": "Deafandhardofhearing",
                            "type": "array",
                        }
                    },
                    "title": "AudioDisabilityModel",
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
                        },
                        "image_credit_url": {"nullable": True, "title": "Image Credit Url", "type": "string"},
                        "is_from_google": {"nullable": True, "title": "Is From Google", "type": "boolean"},
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
                "BookSubType": {
                    "properties": {
                        "gtls": {"items": {"$ref": "#/components/schemas/GTL"}, "title": "Gtls", "type": "array"},
                        "label": {"title": "Label", "type": "string"},
                        "position": {"title": "Position", "type": "integer"},
                    },
                    "required": ["label", "gtls", "position"],
                    "title": "BookSubType",
                    "type": "object",
                },
                "BookType": {
                    "properties": {
                        "children": {
                            "items": {"$ref": "#/components/schemas/BookSubType"},
                            "title": "Children",
                            "type": "array",
                        },
                        "gtls": {"items": {"$ref": "#/components/schemas/GTL"}, "title": "Gtls", "type": "array"},
                        "label": {"title": "Label", "type": "string"},
                        "position": {"title": "Position", "type": "integer"},
                    },
                    "required": ["children", "gtls", "label", "position"],
                    "title": "BookType",
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
                    "enum": [
                        "OFFERER",
                        "BENEFICIARY",
                        "EXPIRED",
                        "FRAUD",
                        "REFUSED_BY_INSTITUTE",
                        "FINANCE_INCIDENT",
                        "BACKOFFICE",
                    ],
                    "title": "BookingCancellationReasons",
                },
                "BookingDisplayStatusRequest": {
                    "properties": {"ended": {"title": "Ended", "type": "boolean"}},
                    "required": ["ended"],
                    "title": "BookingDisplayStatusRequest",
                    "type": "object",
                },
                "BookingOfferExtraData": {
                    "properties": {"ean": {"nullable": True, "title": "Ean", "type": "string"}},
                    "title": "BookingOfferExtraData",
                    "type": "object",
                },
                "BookingOfferResponse": {
                    "properties": {
                        "bookingContact": {"nullable": True, "title": "Bookingcontact", "type": "string"},
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
                        "userReaction": {
                            "anyOf": [{"$ref": "#/components/schemas/ReactionTypeEnum"}],
                            "nullable": True,
                        },
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
                        "features": {"items": {"type": "string"}, "title": "Features", "type": "array"},
                        "id": {"title": "Id", "type": "integer"},
                        "offer": {"$ref": "#/components/schemas/BookingOfferResponse"},
                        "price": {"title": "Price", "type": "integer"},
                        "priceCategoryLabel": {"nullable": True, "title": "Pricecategorylabel", "type": "string"},
                    },
                    "required": ["id", "features", "offer", "price"],
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
                        "timezone": {"title": "Timezone", "type": "string"},
                    },
                    "required": ["id", "name", "coordinates", "timezone"],
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
                    "properties": {
                        "deviceInfo": {
                            "anyOf": [{"$ref": "#/components/schemas/TrustedDevice"}],
                            "nullable": True,
                            "title": "TrustedDevice",
                        },
                        "token": {"title": "Token", "type": "string"},
                    },
                    "required": ["token"],
                    "title": "ChangeBeneficiaryEmailBody",
                    "type": "object",
                },
                "ChangeBeneficiaryEmailResponse": {
                    "properties": {
                        "accessToken": {"title": "Accesstoken", "type": "string"},
                        "refreshToken": {"title": "Refreshtoken", "type": "string"},
                    },
                    "required": ["accessToken", "refreshToken"],
                    "title": "ChangeBeneficiaryEmailResponse",
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
                "E2EUbbleIdCheck": {
                    "properties": {
                        "errors": {
                            "items": {"$ref": "#/components/schemas/UbbleError"},
                            "nullable": True,
                            "type": "array",
                        }
                    },
                    "title": "E2EUbbleIdCheck",
                    "type": "object",
                },
                "EligibilityType": {
                    "description": "An enumeration.",
                    "enum": ["underage", "age-18"],
                    "title": "EligibilityType",
                },
                "EmailChangeConfirmationResponse": {
                    "properties": {
                        "accessToken": {"title": "Accesstoken", "type": "string"},
                        "newEmailSelectionToken": {"title": "Newemailselectiontoken", "type": "string"},
                        "refreshToken": {"title": "Refreshtoken", "type": "string"},
                        "resetPasswordToken": {"nullable": True, "title": "Resetpasswordtoken", "type": "string"},
                    },
                    "required": ["accessToken", "refreshToken", "newEmailSelectionToken"],
                    "title": "EmailChangeConfirmationResponse",
                    "type": "object",
                },
                "EmailHistoryEventTypeEnum": {
                    "description": "An enumeration.",
                    "enum": [
                        "UPDATE_REQUEST",
                        "CONFIRMATION",
                        "CANCELLATION",
                        "NEW_EMAIL_SELECTION",
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
                "EmailUpdateStatusResponse": {
                    "properties": {
                        "expired": {"title": "Expired", "type": "boolean"},
                        "hasRecentlyResetPassword": {"title": "Hasrecentlyresetpassword", "type": "boolean"},
                        "newEmail": {"nullable": True, "title": "Newemail", "type": "string"},
                        "resetPasswordToken": {"nullable": True, "title": "Resetpasswordtoken", "type": "string"},
                        "status": {"$ref": "#/components/schemas/EmailHistoryEventTypeEnum"},
                        "token": {"nullable": True, "title": "Token", "type": "string"},
                    },
                    "required": ["expired", "status", "hasRecentlyResetPassword"],
                    "title": "EmailUpdateStatusResponse",
                    "type": "object",
                },
                "EmailValidationRemainingResendsResponse": {
                    "properties": {
                        "counterResetDatetime": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Counterresetdatetime",
                            "type": "string",
                        },
                        "remainingResends": {"title": "Remainingresends", "type": "integer"},
                    },
                    "required": ["remainingResends"],
                    "title": "EmailValidationRemainingResendsResponse",
                    "type": "object",
                },
                "ExpenseDomain": {
                    "description": "An enumeration.",
                    "enum": ["all", "digital", "physical"],
                    "title": "ExpenseDomain",
                },
                "ExternalAccessibilityDataModel": {
                    "properties": {
                        "audioDisability": {
                            "allOf": [{"$ref": "#/components/schemas/AudioDisabilityModel"}],
                            "default": {"deafAndHardOfHearing": ["Non renseigné"]},
                            "title": "Audiodisability",
                        },
                        "isAccessibleAudioDisability": {
                            "default": False,
                            "title": "Isaccessibleaudiodisability",
                            "type": "boolean",
                        },
                        "isAccessibleMentalDisability": {
                            "default": False,
                            "title": "Isaccessiblementaldisability",
                            "type": "boolean",
                        },
                        "isAccessibleMotorDisability": {
                            "default": False,
                            "title": "Isaccessiblemotordisability",
                            "type": "boolean",
                        },
                        "isAccessibleVisualDisability": {
                            "default": False,
                            "title": "Isaccessiblevisualdisability",
                            "type": "boolean",
                        },
                        "mentalDisability": {
                            "allOf": [{"$ref": "#/components/schemas/MentalDisabilityModel"}],
                            "default": {"trainedPersonnel": "Non renseigné"},
                            "title": "Mentaldisability",
                        },
                        "motorDisability": {
                            "allOf": [{"$ref": "#/components/schemas/MotorDisabilityModel"}],
                            "default": {
                                "entrance": "Non renseigné",
                                "exterior": "Non renseigné",
                                "facilities": "Non renseigné",
                                "parking": "Non renseigné",
                            },
                            "title": "Motordisability",
                        },
                        "visualDisability": {
                            "allOf": [{"$ref": "#/components/schemas/VisualDisabilityModel"}],
                            "default": {"audioDescription": ["Non renseigné"], "soundBeacon": "Non renseigné"},
                            "title": "Visualdisability",
                        },
                    },
                    "title": "ExternalAccessibilityDataModel",
                    "type": "object",
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
                        "venueName": {"title": "Venuename", "type": "string"},
                    },
                    "required": [
                        "id",
                        "name",
                        "subcategoryId",
                        "coordinates",
                        "expenseDomains",
                        "isReleased",
                        "venueName",
                    ],
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
                "GTL": {
                    "properties": {
                        "code": {"title": "Code", "type": "string"},
                        "label": {"title": "Label", "type": "string"},
                        "level": {"title": "Level", "type": "integer"},
                    },
                    "required": ["code", "label", "level"],
                    "title": "GTL",
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
                        "trees": {
                            "anyOf": [
                                {"items": {"$ref": "#/components/schemas/BookType"}, "type": "array"},
                                {"items": {"$ref": "#/components/schemas/MusicType"}, "type": "array"},
                                {"items": {"$ref": "#/components/schemas/ShowType"}, "type": "array"},
                                {"items": {"$ref": "#/components/schemas/MovieType"}, "type": "array"},
                            ],
                            "title": "Trees",
                        },
                        "values": {
                            "items": {"$ref": "#/components/schemas/GenreTypeContentModel"},
                            "title": "Values",
                            "type": "array",
                        },
                    },
                    "required": ["name", "values", "trees"],
                    "title": "GenreTypeModel",
                    "type": "object",
                },
                "GoogleAccountRequest": {
                    "properties": {
                        "accountCreationToken": {"title": "Accountcreationtoken", "type": "string"},
                        "appsFlyerPlatform": {"nullable": True, "title": "Appsflyerplatform", "type": "string"},
                        "appsFlyerUserId": {"nullable": True, "title": "Appsflyeruserid", "type": "string"},
                        "birthdate": {"format": "date", "title": "Birthdate", "type": "string"},
                        "firebasePseudoId": {"nullable": True, "title": "Firebasepseudoid", "type": "string"},
                        "marketingEmailSubscription": {
                            "default": False,
                            "nullable": True,
                            "title": "Marketingemailsubscription",
                            "type": "boolean",
                        },
                        "token": {"title": "Token", "type": "string"},
                        "trustedDevice": {
                            "anyOf": [{"$ref": "#/components/schemas/TrustedDevice"}],
                            "nullable": True,
                            "title": "TrustedDevice",
                        },
                    },
                    "required": ["birthdate", "token", "accountCreationToken"],
                    "title": "GoogleAccountRequest",
                    "type": "object",
                },
                "GoogleSigninRequest": {
                    "properties": {
                        "authorizationCode": {"title": "Authorizationcode", "type": "string"},
                        "deviceInfo": {
                            "anyOf": [{"$ref": "#/components/schemas/TrustedDevice"}],
                            "nullable": True,
                            "title": "TrustedDevice",
                        },
                        "oauthStateToken": {"title": "Oauthstatetoken", "type": "string"},
                    },
                    "required": ["authorizationCode", "oauthStateToken"],
                    "title": "GoogleSigninRequest",
                    "type": "object",
                },
                "GtlLabels": {
                    "properties": {
                        "label": {"title": "Label", "type": "string"},
                        "level01Label": {"nullable": True, "title": "Level01Label", "type": "string"},
                        "level02Label": {"nullable": True, "title": "Level02Label", "type": "string"},
                        "level03Label": {"nullable": True, "title": "Level03Label", "type": "string"},
                        "level04Label": {"nullable": True, "title": "Level04Label", "type": "string"},
                    },
                    "required": ["label"],
                    "title": "GtlLabels",
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
                "MentalDisabilityModel": {
                    "properties": {
                        "trainedPersonnel": {"default": "Non renseigné", "title": "Trainedpersonnel", "type": "string"}
                    },
                    "title": "MentalDisabilityModel",
                    "type": "object",
                },
                "MotorDisabilityModel": {
                    "properties": {
                        "entrance": {"default": "Non renseigné", "title": "Entrance", "type": "string"},
                        "exterior": {"default": "Non renseigné", "title": "Exterior", "type": "string"},
                        "facilities": {"default": "Non renseigné", "title": "Facilities", "type": "string"},
                        "parking": {"default": "Non renseigné", "title": "Parking", "type": "string"},
                    },
                    "title": "MotorDisabilityModel",
                    "type": "object",
                },
                "MovieType": {
                    "properties": {
                        "label": {"title": "Label", "type": "string"},
                        "name": {"title": "Name", "type": "string"},
                    },
                    "required": ["label", "name"],
                    "title": "MovieType",
                    "type": "object",
                },
                "MusicSubType": {
                    "properties": {
                        "code": {"title": "Code", "type": "integer"},
                        "label": {"title": "Label", "type": "string"},
                        "slug": {"title": "Slug", "type": "string"},
                    },
                    "required": ["code", "label", "slug"],
                    "title": "MusicSubType",
                    "type": "object",
                },
                "MusicType": {
                    "properties": {
                        "children": {
                            "items": {"$ref": "#/components/schemas/MusicSubType"},
                            "title": "Children",
                            "type": "array",
                        },
                        "code": {"title": "Code", "type": "integer"},
                        "label": {"title": "Label", "type": "string"},
                    },
                    "required": ["code", "label", "children"],
                    "title": "MusicType",
                    "type": "object",
                },
                "NativeCategoryIdEnumv2": {
                    "description": "An enumeration.",
                    "enum": [
                        "ABONNEMENTS_MUSEE",
                        "ABONNEMENTS_SPECTACLE",
                        "ACHAT_LOCATION_INSTRUMENT",
                        "ARTS_VISUELS",
                        "AUTRES_MEDIAS",
                        "BIBLIOTHEQUE_MEDIATHEQUE",
                        "CARTES_CINEMA",
                        "CARTES_JEUNES",
                        "CD",
                        "CONCERTS_EN_LIGNE",
                        "CONCERTS_EVENEMENTS",
                        "CONCOURS",
                        "CONFERENCES",
                        "DEPRECIEE",
                        "DVD_BLU_RAY",
                        "ESCAPE_GAMES",
                        "EVENEMENTS_CINEMA",
                        "EVENEMENTS_PATRIMOINE",
                        "FESTIVALS",
                        "FESTIVAL_DU_LIVRE",
                        "FILMS_SERIES_EN_LIGNE",
                        "JEUX_EN_LIGNE",
                        "JEUX_PHYSIQUES",
                        "LIVRES_AUDIO_PHYSIQUES",
                        "LIVRES_NUMERIQUE_ET_AUDIO",
                        "LIVRES_PAPIER",
                        "LUDOTHEQUE",
                        "MATERIELS_CREATIFS",
                        "MUSIQUE_EN_LIGNE",
                        "PARTITIONS_DE_MUSIQUE",
                        "PODCAST",
                        "PRATIQUES_ET_ATELIERS_ARTISTIQUES",
                        "PRATIQUE_ARTISTIQUE_EN_LIGNE",
                        "PRESSE_EN_LIGNE",
                        "RENCONTRES",
                        "RENCONTRES_EN_LIGNE",
                        "RENCONTRES_EVENEMENTS",
                        "SALONS_ET_METIERS",
                        "SEANCES_DE_CINEMA",
                        "SPECTACLES_ENREGISTRES",
                        "SPECTACLES_REPRESENTATIONS",
                        "VINYLES",
                        "VISITES_CULTURELLES",
                        "VISITES_CULTURELLES_EN_LIGNE",
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
                "NewEmailSelectionRequest": {
                    "properties": {
                        "newEmail": {"format": "email", "title": "Newemail", "type": "string"},
                        "token": {"title": "Token", "type": "string"},
                    },
                    "required": ["token", "newEmail"],
                    "title": "NewEmailSelectionRequest",
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
                        "subscriptionMessage": {
                            "anyOf": [{"$ref": "#/components/schemas/SubscriptionMessage"}],
                            "nullable": True,
                            "title": "SubscriptionMessage",
                        },
                    },
                    "required": ["allowedIdentityCheckMethods", "hasIdentityCheckPending"],
                    "title": "NextSubscriptionStepResponse",
                    "type": "object",
                },
                "NotificationSubscriptions": {
                    "properties": {
                        "marketingEmail": {"title": "Marketingemail", "type": "boolean"},
                        "marketingPush": {"title": "Marketingpush", "type": "boolean"},
                        "subscribedThemes": {
                            "default": [],
                            "items": {"type": "string"},
                            "title": "Subscribedthemes",
                            "type": "array",
                        },
                    },
                    "required": ["marketingEmail", "marketingPush"],
                    "title": "NotificationSubscriptions",
                    "type": "object",
                },
                "OauthStateResponse": {
                    "properties": {"oauthStateToken": {"title": "Oauthstatetoken", "type": "string"}},
                    "required": ["oauthStateToken"],
                    "title": "OauthStateResponse",
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
                        "allocineId": {"nullable": True, "title": "Allocineid", "type": "integer"},
                        "author": {"nullable": True, "title": "Author", "type": "string"},
                        "cast": {"items": {"type": "string"}, "nullable": True, "title": "Cast", "type": "array"},
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
                        "ean": {"nullable": True, "title": "Ean", "type": "string"},
                        "editeur": {"nullable": True, "title": "Editeur", "type": "string"},
                        "genres": {"items": {"type": "string"}, "nullable": True, "title": "Genres", "type": "array"},
                        "gtlLabels": {
                            "anyOf": [{"$ref": "#/components/schemas/GtlLabels"}],
                            "nullable": True,
                            "title": "GtlLabels",
                        },
                        "musicSubType": {"nullable": True, "title": "Musicsubtype", "type": "string"},
                        "musicType": {"nullable": True, "title": "Musictype", "type": "string"},
                        "performer": {"nullable": True, "title": "Performer", "type": "string"},
                        "releaseDate": {"format": "date", "nullable": True, "title": "Releasedate", "type": "string"},
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
                "OfferPreviewResponse": {
                    "properties": {
                        "durationMinutes": {"nullable": True, "title": "Durationminutes", "type": "integer"},
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
                        "last30DaysBookings": {"nullable": True, "title": "Last30Daysbookings", "type": "integer"},
                        "name": {"title": "Name", "type": "string"},
                        "stocks": {
                            "items": {"$ref": "#/components/schemas/OfferStockResponse"},
                            "title": "Stocks",
                            "type": "array",
                        },
                    },
                    "required": ["id", "name", "stocks"],
                    "title": "OfferPreviewResponse",
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
                        "isExternalBookingsDisabled": {"title": "Isexternalbookingsdisabled", "type": "boolean"},
                        "isForbiddenToUnderage": {"title": "Isforbiddentounderage", "type": "boolean"},
                        "isReleased": {"title": "Isreleased", "type": "boolean"},
                        "isSoldOut": {"title": "Issoldout", "type": "boolean"},
                        "last30DaysBookings": {"nullable": True, "title": "Last30Daysbookings", "type": "integer"},
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
                        "isExternalBookingsDisabled",
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
                "OfferResponseV2": {
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
                        "images": {
                            "additionalProperties": {"$ref": "#/components/schemas/OfferImageResponse"},
                            "nullable": True,
                            "title": "Images",
                            "type": "object",
                        },
                        "isDigital": {"title": "Isdigital", "type": "boolean"},
                        "isDuo": {"title": "Isduo", "type": "boolean"},
                        "isEducational": {"title": "Iseducational", "type": "boolean"},
                        "isExpired": {"title": "Isexpired", "type": "boolean"},
                        "isExternalBookingsDisabled": {"title": "Isexternalbookingsdisabled", "type": "boolean"},
                        "isForbiddenToUnderage": {"title": "Isforbiddentounderage", "type": "boolean"},
                        "isReleased": {"title": "Isreleased", "type": "boolean"},
                        "isSoldOut": {"title": "Issoldout", "type": "boolean"},
                        "last30DaysBookings": {"nullable": True, "title": "Last30Daysbookings", "type": "integer"},
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
                        "isExternalBookingsDisabled",
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
                    "title": "OfferResponseV2",
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
                        "features": {"items": {"type": "string"}, "title": "Features", "type": "array"},
                        "id": {"title": "Id", "type": "integer"},
                        "isBookable": {"title": "Isbookable", "type": "boolean"},
                        "isExpired": {"title": "Isexpired", "type": "boolean"},
                        "isForbiddenToUnderage": {"title": "Isforbiddentounderage", "type": "boolean"},
                        "isSoldOut": {"title": "Issoldout", "type": "boolean"},
                        "price": {"title": "Price", "type": "integer"},
                        "priceCategoryLabel": {"nullable": True, "title": "Pricecategorylabel", "type": "string"},
                        "remainingQuantity": {"nullable": True, "title": "Remainingquantity", "type": "integer"},
                    },
                    "required": [
                        "id",
                        "features",
                        "isBookable",
                        "isForbiddenToUnderage",
                        "isSoldOut",
                        "isExpired",
                        "price",
                    ],
                    "title": "OfferStockResponse",
                    "type": "object",
                },
                "OfferVenueResponse": {
                    "properties": {
                        "address": {"nullable": True, "title": "Address", "type": "string"},
                        "bannerUrl": {"nullable": True, "title": "Bannerurl", "type": "string"},
                        "city": {"nullable": True, "title": "City", "type": "string"},
                        "coordinates": {"$ref": "#/components/schemas/Coordinates"},
                        "id": {"title": "Id", "type": "integer"},
                        "isPermanent": {"title": "Ispermanent", "type": "boolean"},
                        "name": {"title": "Name", "type": "string"},
                        "offerer": {"$ref": "#/components/schemas/OfferOffererResponse"},
                        "postalCode": {"nullable": True, "title": "Postalcode", "type": "string"},
                        "publicName": {"nullable": True, "title": "Publicname", "type": "string"},
                        "timezone": {"title": "Timezone", "type": "string"},
                    },
                    "required": ["id", "offerer", "name", "coordinates", "isPermanent", "timezone"],
                    "title": "OfferVenueResponse",
                    "type": "object",
                },
                "OffersStocksRequest": {
                    "properties": {"offer_ids": {"items": {"type": "integer"}, "title": "Offer Ids", "type": "array"}},
                    "required": ["offer_ids"],
                    "title": "OffersStocksRequest",
                    "type": "object",
                },
                "OffersStocksResponse": {
                    "properties": {
                        "offers": {
                            "items": {"$ref": "#/components/schemas/OfferPreviewResponse"},
                            "title": "Offers",
                            "type": "array",
                        }
                    },
                    "required": ["offers"],
                    "title": "OffersStocksResponse",
                    "type": "object",
                },
                "OffersStocksResponseV2": {
                    "properties": {
                        "offers": {
                            "items": {"$ref": "#/components/schemas/OfferResponseV2"},
                            "title": "Offers",
                            "type": "array",
                        }
                    },
                    "required": ["offers"],
                    "title": "OffersStocksResponseV2",
                    "type": "object",
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
                "PlaylistRequestBody": {
                    "additionalProperties": False,
                    "properties": {
                        "categories": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Categories",
                            "type": "array",
                        },
                        "endDate": {"nullable": True, "title": "Enddate", "type": "string"},
                        "isDuo": {"nullable": True, "title": "Isduo", "type": "boolean"},
                        "isEvent": {"nullable": True, "title": "Isevent", "type": "boolean"},
                        "isRecoShuffled": {"nullable": True, "title": "Isrecoshuffled", "type": "boolean"},
                        "offerTypeList": {
                            "items": {"additionalProperties": {"type": "string"}, "type": "object"},
                            "nullable": True,
                            "title": "Offertypelist",
                            "type": "array",
                        },
                        "priceMax": {"nullable": True, "title": "Pricemax", "type": "number"},
                        "priceMin": {"nullable": True, "title": "Pricemin", "type": "number"},
                        "startDate": {"nullable": True, "title": "Startdate", "type": "string"},
                        "subcategories": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Subcategories",
                            "type": "array",
                        },
                    },
                    "title": "PlaylistRequestBody",
                    "type": "object",
                },
                "PlaylistRequestQuery": {
                    "additionalProperties": False,
                    "properties": {
                        "latitude": {"nullable": True, "title": "Latitude", "type": "number"},
                        "longitude": {"nullable": True, "title": "Longitude", "type": "number"},
                        "modelEndpoint": {"nullable": True, "title": "Modelendpoint", "type": "string"},
                    },
                    "title": "PlaylistRequestQuery",
                    "type": "object",
                },
                "PlaylistResponse": {
                    "properties": {
                        "params": {"$ref": "#/components/schemas/RecommendationApiParams"},
                        "playlistRecommendedOffers": {
                            "items": {"type": "string"},
                            "title": "Playlistrecommendedoffers",
                            "type": "array",
                        },
                    },
                    "required": ["playlistRecommendedOffers", "params"],
                    "title": "PlaylistResponse",
                    "type": "object",
                },
                "PopOverIcon": {
                    "description": "An enumeration.",
                    "enum": ["INFO", "ERROR", "WARNING", "CLOCK", "FILE", "MAGNIFYING_GLASS"],
                    "title": "PopOverIcon",
                },
                "PostReactionRequest": {
                    "properties": {
                        "offerId": {"title": "Offerid", "type": "integer"},
                        "reactionType": {"$ref": "#/components/schemas/ReactionTypeEnum"},
                    },
                    "required": ["offerId", "reactionType"],
                    "title": "PostReactionRequest",
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
                "ReactionTypeEnum": {
                    "description": "An enumeration.",
                    "enum": ["LIKE", "DISLIKE", "NO_REACTION"],
                    "title": "ReactionTypeEnum",
                },
                "Reason": {
                    "description": "Describe possible reason codes to used when reporting an offer.\n\nThe whole meta part is only consumed by the api client, it has no meaning\ninside the whole API code.\n\nNote: when adding a new enum symbol, do not forget to update the meta method.",
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
                "RecommendationApiParams": {
                    "properties": {
                        "ab_test": {"nullable": True, "title": "Ab Test", "type": "string"},
                        "call_id": {"nullable": True, "title": "Call Id", "type": "string"},
                        "filtered": {"nullable": True, "title": "Filtered", "type": "boolean"},
                        "geo_located": {"nullable": True, "title": "Geo Located", "type": "boolean"},
                        "model_endpoint": {"nullable": True, "title": "Model Endpoint", "type": "string"},
                        "model_name": {"nullable": True, "title": "Model Name", "type": "string"},
                        "model_version": {"nullable": True, "title": "Model Version", "type": "string"},
                        "reco_origin": {"nullable": True, "title": "Reco Origin", "type": "string"},
                    },
                    "title": "RecommendationApiParams",
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
                        "deviceInfo": {
                            "anyOf": [{"$ref": "#/components/schemas/TrustedDevice"}],
                            "nullable": True,
                            "title": "TrustedDevice",
                        },
                        "newPassword": {"title": "Newpassword", "type": "string"},
                        "resetPasswordToken": {"title": "Resetpasswordtoken", "type": "string"},
                    },
                    "required": ["resetPasswordToken", "newPassword"],
                    "title": "ResetPasswordRequest",
                    "type": "object",
                },
                "ResetPasswordResponse": {
                    "properties": {
                        "accessToken": {"title": "Accesstoken", "type": "string"},
                        "refreshToken": {"title": "Refreshtoken", "type": "string"},
                    },
                    "required": ["accessToken", "refreshToken"],
                    "title": "ResetPasswordResponse",
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
                "SearchGroupNameEnumv2": {
                    "description": "An enumeration.",
                    "enum": [
                        "ARTS_LOISIRS_CREATIFS",
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
                        "enablePhoneValidation": {"title": "Enablephonevalidation", "type": "boolean"},
                        "idCheckAddressAutocompletion": {"title": "Idcheckaddressautocompletion", "type": "boolean"},
                        "isRecaptchaEnabled": {"title": "Isrecaptchaenabled", "type": "boolean"},
                        "objectStorageUrl": {"title": "Objectstorageurl", "type": "string"},
                    },
                    "required": [
                        "accountCreationMinimumAge",
                        "appEnableAutocomplete",
                        "displayDmsRedirection",
                        "enableFrontImageResizing",
                        "enableNativeCulturalSurvey",
                        "enablePhoneValidation",
                        "idCheckAddressAutocompletion",
                        "isRecaptchaEnabled",
                        "objectStorageUrl",
                        "accountUnsuspensionLimit",
                    ],
                    "title": "SettingsResponse",
                    "type": "object",
                },
                "ShowSubType": {
                    "properties": {
                        "code": {"title": "Code", "type": "integer"},
                        "label": {"title": "Label", "type": "string"},
                        "slug": {"title": "Slug", "type": "string"},
                    },
                    "required": ["code", "label", "slug"],
                    "title": "ShowSubType",
                    "type": "object",
                },
                "ShowType": {
                    "properties": {
                        "children": {
                            "items": {"$ref": "#/components/schemas/ShowSubType"},
                            "title": "Children",
                            "type": "array",
                        },
                        "code": {"title": "Code", "type": "integer"},
                        "label": {"title": "Label", "type": "string"},
                    },
                    "required": ["children", "code", "label"],
                    "title": "ShowType",
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
                        "token": {"nullable": True, "title": "Token", "type": "string"},
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
                "SimilarOffersRequestQuery": {
                    "additionalProperties": False,
                    "properties": {
                        "categories": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Categories",
                            "type": "array",
                        },
                        "latitude": {"nullable": True, "title": "Latitude", "type": "number"},
                        "longitude": {"nullable": True, "title": "Longitude", "type": "number"},
                        "subcategories": {
                            "items": {"type": "string"},
                            "nullable": True,
                            "title": "Subcategories",
                            "type": "array",
                        },
                    },
                    "title": "SimilarOffersRequestQuery",
                    "type": "object",
                },
                "SimilarOffersResponse": {
                    "properties": {
                        "params": {"$ref": "#/components/schemas/RecommendationApiParams"},
                        "results": {"items": {"type": "string"}, "title": "Results", "type": "array"},
                    },
                    "required": ["params"],
                    "title": "SimilarOffersResponse",
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
                        "SUPPORT_PHYSIQUE_MUSIQUE_CD",
                        "SUPPORT_PHYSIQUE_MUSIQUE_VINYLE",
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
                        "SUPPORT_PHYSIQUE_MUSIQUE_CD",
                        "SUPPORT_PHYSIQUE_MUSIQUE_VINYLE",
                        "TELECHARGEMENT_LIVRE_AUDIO",
                        "TELECHARGEMENT_MUSIQUE",
                        "VISITE_GUIDEE",
                        "VISITE_VIRTUELLE",
                        "VISITE",
                        "VOD",
                    ],
                    "title": "SubcategoryIdEnumv2",
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
                "SubscriptionMessageV2": {
                    "properties": {
                        "callToAction": {
                            "anyOf": [{"$ref": "#/components/schemas/CallToActionMessage"}],
                            "nullable": True,
                            "title": "CallToActionMessage",
                        },
                        "messageSummary": {"nullable": True, "title": "Messagesummary", "type": "string"},
                        "popOverIcon": {"anyOf": [{"$ref": "#/components/schemas/PopOverIcon"}], "nullable": True},
                        "updatedAt": {"format": "date-time", "nullable": True, "title": "Updatedat", "type": "string"},
                        "userMessage": {"title": "Usermessage", "type": "string"},
                    },
                    "required": ["userMessage"],
                    "title": "SubscriptionMessageV2",
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
                        "maintenancePageType": {
                            "anyOf": [{"$ref": "#/components/schemas/MaintenancePageType"}],
                            "nullable": True,
                        },
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
                "SubscriptionStepperResponseV2": {
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
                        "subscriptionMessage": {
                            "anyOf": [{"$ref": "#/components/schemas/SubscriptionMessageV2"}],
                            "nullable": True,
                            "title": "SubscriptionMessageV2",
                        },
                        "subscriptionStepsToDisplay": {
                            "items": {"$ref": "#/components/schemas/SubscriptionStepDetailsResponse"},
                            "title": "Subscriptionstepstodisplay",
                            "type": "array",
                        },
                        "subtitle": {"nullable": True, "title": "Subtitle", "type": "string"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": [
                        "subscriptionStepsToDisplay",
                        "allowedIdentityCheckMethods",
                        "hasIdentityCheckPending",
                        "title",
                    ],
                    "title": "SubscriptionStepperResponseV2",
                    "type": "object",
                },
                "SuspendAccountForSuspiciousLoginRequest": {
                    "properties": {"token": {"title": "Token", "type": "string"}},
                    "required": ["token"],
                    "title": "SuspendAccountForSuspiciousLoginRequest",
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
                "UbbleError": {
                    "description": "An enumeration.",
                    "enum": [1201, 1301, 1320, 2101, 2102, 2103, 2201],
                    "title": "UbbleError",
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
                        "depositActivationDate": {
                            "format": "date-time",
                            "nullable": True,
                            "title": "Depositactivationdate",
                            "type": "string",
                        },
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
                        "hasPassword": {"title": "Haspassword", "type": "boolean"},
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
                        "hasPassword",
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
                        "origin": {"nullable": True, "title": "Origin", "type": "string"},
                        "subscriptions": {
                            "anyOf": [{"$ref": "#/components/schemas/NotificationSubscriptions"}],
                            "nullable": True,
                            "title": "NotificationSubscriptions",
                        },
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
                    "enum": [
                        "ADMIN",
                        "ANONYMIZED",
                        "BENEFICIARY",
                        "PRO",
                        "NON_ATTACHED_PRO",
                        "UNDERAGE_BENEFICIARY",
                        "TEST",
                    ],
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
                    "properties": {
                        "deviceInfo": {
                            "anyOf": [{"$ref": "#/components/schemas/TrustedDevice"}],
                            "nullable": True,
                            "title": "TrustedDevice",
                        },
                        "emailValidationToken": {"title": "Emailvalidationtoken", "type": "string"},
                    },
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
                        "externalAccessibilityData": {
                            "anyOf": [{"$ref": "#/components/schemas/ExternalAccessibilityDataModel"}],
                            "nullable": True,
                            "title": "ExternalAccessibilityDataModel",
                        },
                        "externalAccessibilityId": {
                            "nullable": True,
                            "title": "Externalaccessibilityid",
                            "type": "string",
                        },
                        "externalAccessibilityUrl": {
                            "nullable": True,
                            "title": "Externalaccessibilityurl",
                            "type": "string",
                        },
                        "id": {"title": "Id", "type": "integer"},
                        "isPermanent": {"nullable": True, "title": "Ispermanent", "type": "boolean"},
                        "isVirtual": {"title": "Isvirtual", "type": "boolean"},
                        "latitude": {"nullable": True, "title": "Latitude", "type": "number"},
                        "longitude": {"nullable": True, "title": "Longitude", "type": "number"},
                        "name": {"title": "Name", "type": "string"},
                        "openingHours": {"nullable": True, "title": "Openinghours", "type": "object"},
                        "postalCode": {"nullable": True, "title": "Postalcode", "type": "string"},
                        "publicName": {"nullable": True, "title": "Publicname", "type": "string"},
                        "street": {"nullable": True, "title": "Street", "type": "string"},
                        "timezone": {"title": "Timezone", "type": "string"},
                        "venueTypeCode": {"$ref": "#/components/schemas/VenueTypeCodeKey"},
                        "withdrawalDetails": {"nullable": True, "title": "Withdrawaldetails", "type": "string"},
                    },
                    "required": ["isVirtual", "name", "id", "accessibility", "venueTypeCode", "timezone"],
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
                "VisualDisabilityModel": {
                    "properties": {
                        "audioDescription": {
                            "default": ["Non renseigné"],
                            "items": {"type": "string"},
                            "title": "Audiodescription",
                            "type": "array",
                        },
                        "soundBeacon": {"default": "Non renseigné", "title": "Soundbeacon", "type": "string"},
                    },
                    "title": "VisualDisabilityModel",
                    "type": "object",
                },
                "WithdrawalTypeEnum": {
                    "description": "An enumeration.",
                    "enum": ["by_email", "in_app", "no_ticket", "on_site"],
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
                    "operationId": "post__native_v1_account",
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
                    "operationId": "post__native_v1_account_suspend",
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
                    "operationId": "get__native_v1_account_suspend_token_validation_{token}",
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
                        "401": {"description": "Unauthorized"},
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
            "/native/v1/account/suspend_for_suspicious_login": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_account_suspend_for_suspicious_login",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SuspendAccountForSuspiciousLoginRequest"}
                            }
                        }
                    },
                    "responses": {
                        "204": {"description": "No Content"},
                        "400": {"description": "Bad Request"},
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
                    "summary": "suspend_account_for_suspicious_login <POST>",
                    "tags": [],
                }
            },
            "/native/v1/account/suspension_date": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_account_suspension_date",
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
                    "operationId": "get__native_v1_account_suspension_status",
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
                    "operationId": "post__native_v1_account_unsuspend",
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
                    "operationId": "get__native_v1_banner",
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
                    "operationId": "get__native_v1_bookings",
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
                    "operationId": "post__native_v1_bookings",
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
                    "operationId": "post__native_v1_bookings_{booking_id}_cancel",
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
                    "operationId": "post__native_v1_bookings_{booking_id}_toggle_display",
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
                    "operationId": "post__native_v1_change_password",
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
                    "operationId": "post__native_v1_cookies_consent",
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
                    "operationId": "post__native_v1_cultural_survey_answers",
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
                    "operationId": "get__native_v1_cultural_survey_questions",
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
            "/native/v1/email_validation_remaining_resends/{email}": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_email_validation_remaining_resends_{email}",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "email",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EmailValidationRemainingResendsResponse"}
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
                    "summary": "email_validation_remaining_resends <GET>",
                    "tags": [],
                }
            },
            "/native/v1/me": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_me",
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
                    "operationId": "get__native_v1_me_favorites",
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
                    "operationId": "post__native_v1_me_favorites",
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
                    "operationId": "get__native_v1_me_favorites_count",
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
                    "operationId": "delete__native_v1_me_favorites_{favorite_id}",
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
            "/native/v1/oauth/google/account": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_oauth_google_account",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/GoogleAccountRequest"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/SigninResponse"}}
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
                    "summary": "create_account_with_google_sso <POST>",
                    "tags": [],
                }
            },
            "/native/v1/oauth/google/authorize": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_oauth_google_authorize",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/GoogleSigninRequest"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/SigninResponse"}}
                            },
                            "description": "OK",
                        },
                        "400": {"description": "Bad Request"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "summary": "google_auth <POST>",
                    "tags": [],
                }
            },
            "/native/v1/oauth/state": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_oauth_state",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/OauthStateResponse"}}
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
                    "summary": "google_oauth_state <GET>",
                    "tags": [],
                }
            },
            "/native/v1/offer/report/reasons": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_offer_report_reasons",
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
                    "deprecated": True,
                    "description": "",
                    "operationId": "get__native_v1_offer_{offer_id}",
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
                    "operationId": "post__native_v1_offer_{offer_id}_report",
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
                    "operationId": "get__native_v1_offers_reports",
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
            "/native/v1/offers/stocks": {
                "post": {
                    "deprecated": True,
                    "description": "",
                    "operationId": "post__native_v1_offers_stocks",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/OffersStocksRequest"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/OffersStocksResponse"}}
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
                    "summary": "get_offers_showtimes <POST>",
                    "tags": [],
                }
            },
            "/native/v1/phone_validation/remaining_attempts": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_phone_validation_remaining_attempts",
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
                    "operationId": "post__native_v1_profile",
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
            "/native/v1/profile/email_update/cancel": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_profile_email_update_cancel",
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
                    "summary": "cancel_email_update <POST>",
                    "tags": [],
                }
            },
            "/native/v1/profile/email_update/confirm": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_profile_email_update_confirm",
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
                    "summary": "confirm_email_update <POST>",
                    "tags": [],
                }
            },
            "/native/v1/profile/email_update/status": {
                "get": {
                    "deprecated": True,
                    "description": "",
                    "operationId": "get__native_v1_profile_email_update_status",
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
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                    },
                    "security": [{"JWTAuth": []}],
                    "summary": "get_email_update_status <GET>",
                    "tags": [],
                }
            },
            "/native/v1/profile/email_update/validate": {
                "put": {
                    "description": "",
                    "operationId": "put__native_v1_profile_email_update_validate",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ChangeBeneficiaryEmailBody"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ChangeBeneficiaryEmailResponse"}
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
                    "summary": "validate_user_email <PUT>",
                    "tags": [],
                }
            },
            "/native/v1/profile/token_expiration": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_profile_token_expiration",
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
                    "deprecated": True,
                    "description": "",
                    "operationId": "post__native_v1_profile_update_email",
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
            "/native/v1/reaction": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_reaction",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/PostReactionRequest"}}
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
                    "summary": "post_reaction <POST>",
                    "tags": [],
                }
            },
            "/native/v1/recommendation/playlist": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_recommendation_playlist",
                    "parameters": [
                        {
                            "description": "",
                            "in": "query",
                            "name": "modelEndpoint",
                            "required": False,
                            "schema": {"nullable": True, "title": "Modelendpoint", "type": "string"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "longitude",
                            "required": False,
                            "schema": {"nullable": True, "title": "Longitude", "type": "number"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "latitude",
                            "required": False,
                            "schema": {"nullable": True, "title": "Latitude", "type": "number"},
                        },
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/PlaylistRequestBody"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/PlaylistResponse"}}
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
                    "summary": "playlist <POST>",
                    "tags": [],
                }
            },
            "/native/v1/recommendation/similar_offers/{offer_id}": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_recommendation_similar_offers_{offer_id}",
                    "parameters": [
                        {
                            "description": "",
                            "in": "path",
                            "name": "offer_id",
                            "required": True,
                            "schema": {"format": "int32", "type": "integer"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "longitude",
                            "required": False,
                            "schema": {"nullable": True, "title": "Longitude", "type": "number"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "latitude",
                            "required": False,
                            "schema": {"nullable": True, "title": "Latitude", "type": "number"},
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "categories",
                            "required": False,
                            "schema": {
                                "items": {"type": "string"},
                                "nullable": True,
                                "title": "Categories",
                                "type": "array",
                            },
                        },
                        {
                            "description": "",
                            "in": "query",
                            "name": "subcategories",
                            "required": False,
                            "schema": {
                                "items": {"type": "string"},
                                "nullable": True,
                                "title": "Subcategories",
                                "type": "array",
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/SimilarOffersResponse"}}
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
                    "summary": "similar_offers <GET>",
                    "tags": [],
                }
            },
            "/native/v1/refresh_access_token": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_refresh_access_token",
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
                    "operationId": "post__native_v1_request_password_reset",
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
                    "operationId": "post__native_v1_resend_email_validation",
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
                        "400": {"description": "Bad Request"},
                        "403": {"description": "Forbidden"},
                        "422": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
                            },
                            "description": "Unprocessable Entity",
                        },
                        "429": {"description": "Too Many Requests"},
                    },
                    "summary": "resend_email_validation <POST>",
                    "tags": [],
                }
            },
            "/native/v1/reset_password": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_reset_password",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ResetPasswordRequest"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ResetPasswordResponse"}}
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
                    "summary": "reset_password <POST>",
                    "tags": [],
                }
            },
            "/native/v1/reset_recredit_amount_to_show": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_reset_recredit_amount_to_show",
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
                    "operationId": "post__native_v1_send_offer_link_by_push_{offer_id}",
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
                    "operationId": "post__native_v1_send_offer_webapp_link_by_email_{offer_id}",
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
                    "operationId": "post__native_v1_send_phone_validation_code",
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
                    "operationId": "get__native_v1_settings",
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
                    "operationId": "post__native_v1_signin",
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
                        "400": {"description": "Bad Request"},
                        "401": {"description": "Unauthorized"},
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
            "/native/v1/subcategories/v2": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_subcategories_v2",
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
            "/native/v1/subscription/activity_types": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v1_subscription_activity_types",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/ActivityTypesResponse"}}
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
                    "summary": "get_activity_types <GET>",
                    "tags": [],
                }
            },
            "/native/v1/subscription/honor_statement": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_subscription_honor_statement",
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
                    "deprecated": True,
                    "description": "",
                    "operationId": "get__native_v1_subscription_next_step",
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
                    "operationId": "get__native_v1_subscription_profile",
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
                    "operationId": "post__native_v1_subscription_profile",
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
            "/native/v1/subscription/stepper": {
                "get": {
                    "deprecated": True,
                    "description": "",
                    "operationId": "get__native_v1_subscription_stepper",
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
                    "summary": "get_subscription_stepper_deprecated <GET>",
                    "tags": [],
                }
            },
            "/native/v1/ubble_identification": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_ubble_identification",
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
            "/native/v1/ubble_identification/e2e": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_ubble_identification_e2e",
                    "parameters": [],
                    "requestBody": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/E2EUbbleIdCheck"}}}
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
                    "summary": "ubble_identification <POST>",
                    "tags": [],
                }
            },
            "/native/v1/validate_email": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v1_validate_email",
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
                    "operationId": "post__native_v1_validate_phone_number",
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
                    "operationId": "get__native_v1_venue_{venue_id}",
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
            "/native/v2/offer/{offer_id}": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v2_offer_{offer_id}",
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
                                "application/json": {"schema": {"$ref": "#/components/schemas/OfferResponseV2"}}
                            },
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
                    "summary": "get_offer_v2 <GET>",
                    "tags": [],
                }
            },
            "/native/v2/offers/stocks": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v2_offers_stocks",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/OffersStocksRequest"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/OffersStocksResponseV2"}}
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
                    "summary": "get_offers_and_stocks <POST>",
                    "tags": [],
                }
            },
            "/native/v2/profile/email_update/confirm": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v2_profile_email_update_confirm",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ChangeBeneficiaryEmailBody"}}
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EmailChangeConfirmationResponse"}
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
                    "summary": "confirm_email_update <POST>",
                    "tags": [],
                }
            },
            "/native/v2/profile/email_update/new_email": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v2_profile_email_update_new_email",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/NewEmailSelectionRequest"}}
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
                    "summary": "select_new_email <POST>",
                    "tags": [],
                }
            },
            "/native/v2/profile/email_update/new_password": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v2_profile_email_update_new_password",
                    "parameters": [],
                    "requestBody": {
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ResetPasswordRequest"}}
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
                    "summary": "select_new_password <POST>",
                    "tags": [],
                }
            },
            "/native/v2/profile/email_update/status": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v2_profile_email_update_status",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EmailUpdateStatusResponse"}
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
                    "summary": "get_email_update_status <GET>",
                    "tags": [],
                }
            },
            "/native/v2/profile/update_email": {
                "post": {
                    "description": "",
                    "operationId": "post__native_v2_profile_update_email",
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
                    "summary": "update_user_email <POST>",
                    "tags": [],
                }
            },
            "/native/v2/subscription/stepper": {
                "get": {
                    "description": "",
                    "operationId": "get__native_v2_subscription_stepper",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SubscriptionStepperResponseV2"}
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
        },
        "security": [],
        "tags": [],
    }
    got_lines = json.dumps(response.json, indent=2, sort_keys=True).splitlines()
    expected_lines = json.dumps(expected, indent=2, sort_keys=True).splitlines()
    diff = "\n".join(difflib.unified_diff(got_lines, expected_lines))
    assert response.json == expected, f"Got diff from expected schema: {diff}"
