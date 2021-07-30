import copy


BENEFICIARY_INCLUDES = [
    "-culturalSurveyId",
    "-culturalSurveyFilledDate",
    "-hasSeenTutorials",
    "-lastConnectionDate",
    "-password",
    "-resetPasswordToken",
    "-resetPasswordTokenValidityLimit",
    "-validationToken",
    "wallet_balance",
    "wallet_is_activated",
    "deposit_expiration_date",
    "needsToSeeTutorials",
]

OFFERER_INCLUDES = [
    {"key": "managedVenues", "includes": ["-validationToken", "nOffers", "iban", "bic"]},
    "nOffers",
    "isValidated",
    "userHasAccess",
    "bic",
    "iban",
    "demarchesSimplifieesApplicationId",
    "-validationToken",
]

USER_INCLUDES = [
    "-culturalSurveyId",
    "-culturalSurveyFilledDate",
    "-hasSeenTutorials",
    "-isActive",
    "-password",
    "-resetPasswordToken",
    "-resetPasswordTokenValidityLimit",
    "-suspensionReason",
    "-validationToken",
    "hasPhysicalVenues",
]

WEBAPP_GET_BOOKING_INCLUDES = [
    "completedUrl",
    "-displayAsEnded",
    "isEventExpired",
    "-educationalBookingId",
    "-individualBookingId",
    "-status",
    {
        "key": "stock",
        "includes": [
            "isBookable",
            "isEventExpired",
            "remainingQuantity",
            "-dnBookedQuantity",
            "-rawProviderQuantity",
            {
                "key": "offer",
                "includes": [
                    "thumbUrl",
                    "hasBookingLimitDatetimesPassed",
                    "isBookable",
                    "isDigital",
                    "isEvent",
                    "-idAtProvider",
                    "offerType",
                    "-authorId",
                    "-lastValidationDate",
                    "-rankingWeight",
                    {
                        "key": "stocks",
                        "includes": [
                            "isBookable",
                            "isEventExpired",
                            "remainingQuantity",
                            "-dnBookedQuantity",
                            "-rawProviderQuantity",
                        ],
                    },
                    {"key": "venue", "includes": ["-validationToken"]},
                ],
            },
        ],
    },
    {"key": "mediation", "includes": ["thumbUrl"]},
]

WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES = copy.deepcopy(WEBAPP_GET_BOOKING_INCLUDES)
WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES.append("qrCode")

FEATURE_INCLUDES = ["nameKey"]

USER_OFFERER_INCLUDES = ["-validationToken"]
