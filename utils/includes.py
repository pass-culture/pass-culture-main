import copy

BENEFICIARY_INCLUDES = [
    '-culturalSurveyId',
    '-culturalSurveyFilledDate',
    '-hasSeenTutorials',
    '-lastConnectionDate',
    '-password',
    '-resetPasswordToken',
    '-resetPasswordTokenValidityLimit',
    '-validationToken',
    'expenses',
    'wallet_balance',
    'wallet_is_activated',
    'wallet_date_created',
    'needsToSeeTutorials'
]

OFFERER_INCLUDES = [
    {
        "key": "managedVenues",
        "includes": [
            '-validationToken',
            "nOffers",
            "iban",
            "bic"
        ]
    },
    "nOffers",
    "isValidated",
    "userHasAccess",
    "bic",
    "iban",
    "demarchesSimplifieesApplicationId",
    "-validationToken"
]

OFFER_INCLUDES = [
    "isDigital",
    "isEditable",
    "isEvent",
    'isFullyBooked',
    'hasBookingLimitDatetimesPassed',
    'isBookable',
    "isThing",
    "lastProvider",
    "offerType",
    "availabilityMessage",
    "thumbUrl",
    {
        "key": "activeMediation",
        "includes": ["thumbUrl"]
    },
    {
        "key": "mediations",
        "includes": ["thumbUrl"]
    },
    {
        "key": "product",
        "includes": [
            '-type'
        ]
    },
    {
        "key": "stocks",
        "includes": [
            'bookingsQuantity',
            'isBookable',
            'isEventDeletable',
            'isEventExpired',
            'remainingQuantity',
        ]
    },
    {
        "key": "venue",
        "includes": [
            {
                "key": "managingOfferer",
                "includes": [
                    "-validationToken",
                    "isValidated",
                    "bic",
                    "iban"
                ]
            },
            '-validationToken',
            "isValidated",
            "bic",
            "iban"
        ]
    }
]

RECOMMENDATION_INCLUDES = [
    "thumbUrl",
    {
        "key": "offer",
        "includes": [
            "dateRange",
            "isEvent",
            'hasBookingLimitDatetimesPassed',
            'isBookable',
            'isFullyBooked',
            "isThing",
            "offerType",
            {
                "key": "stocks",
                "includes": [
                    'isBookable',
                    'remainingQuantity'
                ]
            },
            {
                "key": "venue",
                "includes": [
                    "-validationToken",
                    {
                        "key": "managingOfferer",
                        "includes": ["-validationToken"]
                    }
                ]
            },
        ]
    },
]

USER_INCLUDES = [
    '-culturalSurveyId',
    '-culturalSurveyFilledDate',
    '-hasSeenTutorials',
    '-password',
    '-resetPasswordToken',
    '-resetPasswordTokenValidityLimit',
    '-validationToken',
    'hasPhysicalVenues',
    'hasOffers',
]

WEBAPP_GET_BOOKING_INCLUDES = [
    "completedUrl",
    'isEventExpired',
    {
        "key": "stock",
        "includes": [
            'isBookable',
            'isEventExpired',
            'remainingQuantity',
            {
                "key": "offer",
                "includes": [
                    'thumbUrl',
                    'hasBookingLimitDatetimesPassed',
                    'isBookable',
                    'isDigital',
                    'isEvent',
                    "isFullyBooked",
                    "offerType",
                    {
                        "key": "stocks",
                        "includes": [
                            'isBookable',
                            'isEventExpired',
                            'remainingQuantity'
                        ]
                    },
                    {
                        "key": "venue",
                        "includes": ['-validationToken']
                    }
                ]
            },
        ]
    },
    {
        "key": "mediation",
        "includes": ['thumbUrl']
    },
]

WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES = copy.deepcopy(
    WEBAPP_GET_BOOKING_INCLUDES)
WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES.append("qrCode")

WEBAPP_PATCH_POST_BOOKING_INCLUDES = [
    "completedUrl",
    "isUserCancellable",
    {
        "key": "recommendation",
        "includes": [
            {
                "key": "offer",
                "includes": [
                    "dateRange",
                    "favorites",
                    "isEvent",
                    'hasBookingLimitDatetimesPassed',
                    "isFullyBooked",
                    "isThing",
                    "offerType",
                    "thumbUrl",
                    {
                        "key": "product",
                        "includes": ["thumbUrl"]
                    },
                    {
                        "key": "stocks",
                        "includes": [
                            'isBookable',
                            'remainingQuantity'
                        ]
                    },
                    {
                        "key": "venue",
                        "includes": ['-validationToken']
                    }
                ]
            },
            {
                "key": "mediation",
                "includes": ["thumbUrl"]
            },
            "thumbUrl"
        ]
    },
    {
        "key": "stock",
        "includes": [
            'isBookable',
            'remainingQuantity'
        ]
    },
    "thumbUrl",
    {
        "key": "user",
        "includes": BENEFICIARY_INCLUDES
    }
]

VENUE_INCLUDES = [
    'isValidated',
    'bic',
    'iban',
    'demarchesSimplifieesApplicationId',
    "-validationToken",
    {
        "key": "managingOfferer",
        "includes": [
            '-validationToken',
            "bic",
            "iban"
        ]
    }
]

VENUE_PROVIDER_INCLUDES = [
    "provider",
    "nOffers",
    "-_sa_polymorphic_on"
]

OFFERER_FOR_PENDING_VALIDATION_INCLUDES = [
    "validationToken",
    "-thumbCount",
    "-idAtProviders",
    {
        "key": "UserOfferers",
        "includes": [{
            "key": "user",
            "includes": [
                'validationToken',
                '-resetPasswordTokenValidityLimit',
                '-resetPasswordToken',
                '-clearTextPassword',
                '-password',
                '-dateOfBirth',
                '-id',
            ]
        }]
    },
    {
        "key": "managedVenues",
        "includes": [
            'validationToken',
            '-publicName',
            '-thumbCount',
            '-idAtProviders',
            '-isVirtual',
            '-lastProviderId',
            '-latitude',
            '-longitude',
            '-dateModifiedAtLastProvider',
        ]
    }
]

MEDIATION_INCLUDES = [
    "thumbUrl"
]

FEATURE_INCLUDES = [
    'nameKey'
]

USER_OFFERER_INCLUDES = [
    '-validationToken'
]
