import copy


USER_INCLUDES = [
    "-culturalSurveyId",
    "-culturalSurveyFilledDate",
    "-extraData",
    "-hasSeenTutorials",
    "-isActive",
    "-password",
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
            "-educationalPriceDetail",
            {
                "key": "offer",
                "includes": [
                    "thumbUrl",
                    "hasBookingLimitDatetimesPassed",
                    "isBookable",
                    "isDigital",
                    "isEvent",
                    "-idAtProvider",
                    "-authorId",
                    "-lastValidationDate",
                    "-rankingWeight",
                    "-dateUpdated",
                    "-type",
                    {
                        "key": "stocks",
                        "includes": [
                            "isBookable",
                            "isEventExpired",
                            "remainingQuantity",
                            "-dnBookedQuantity",
                            "-rawProviderQuantity",
                            "-educationalPriceDetail",
                        ],
                    },
                    {"key": "venue", "includes": ["-validationToken", "-businessUnitId"]},
                ],
            },
        ],
    },
    {"key": "mediation", "includes": ["thumbUrl"]},
]

WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES = copy.deepcopy(WEBAPP_GET_BOOKING_INCLUDES)
WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES.append("qrCode")

FEATURE_INCLUDES = ["nameKey"]
