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
    "hasOffers",
]

WEBAPP_GET_BOOKING_INCLUDES = [
    "completedUrl",
    "isEventExpired",
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
                    "offerType",
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

VENUE_INCLUDES = [
    "isValidated",
    "bic",
    "iban",
    "demarchesSimplifieesApplicationId",
    "-validationToken",
    {"key": "managingOfferer", "includes": ["-validationToken", "bic", "iban"]},
]

VENUE_PROVIDER_INCLUDES = ["provider", "nOffers", "-_sa_polymorphic_on"]

FEATURE_INCLUDES = ["nameKey"]

USER_OFFERER_INCLUDES = ["-validationToken"]
