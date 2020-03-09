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
    "-validationToken"
]

EVENT_INCLUDES = [
    {
        "key": "occurrences",
        "includes": [
            {
                "key": "stock",
                "includes": [
                    {
                        "key": "offerer",
                        "includes": OFFERER_INCLUDES
                    }
                ]
            },
            'venue'
        ]
    },
    {
        "key": "mediations",
        "includes": ["thumbUrl"]
    },
    "offers",
    "-type",
    "offerType",
    "thumbUrl"
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
    "stockAlertMessage",
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
            'thumbUrl',
            '-type'
        ]
    },
    {
        "key": "stocks",
        "includes": ['isBookable']
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

FAVORITE_INCLUDES = [
    "-userId",
    {
        "key": "mediation",
        "includes": ["thumbUrl"]
    },
    {
        "key": "offer",
        "includes": [
            "dateRange",
            "favorites",
            "isEvent",
            "isBookable",
            'hasBookingLimitDatetimesPassed',
            "isThing",
            "isFullyBooked",
            "offerType",
            {
                "key": "product",
                "includes": ["thumbUrl"]
            },
            {
                "key": "stocks",
                "includes": ["isBookable"]
            },
            {
                "key": "venue",
                "includes": ['-validationToken']
            }
        ]
    },
    "thumbUrl"
]

RECOMMENDATION_INCLUDES = [
    "productOrTutoIdentifier",
    {
        "key": "mediation",
        "includes": ["thumbUrl"]
    },
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
                "key": "product",
                "includes": ["thumbUrl"]
            },
            {
                "key": "stocks",
                "includes": ["isBookable"]
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
    "thumbUrl"
]

USER_INCLUDES = [
    '-culturalSurveyId',
    '-culturalSurveyFilledDate',
    '-password',
    '-resetPasswordToken',
    '-resetPasswordTokenValidityLimit',
    '-validationToken',
    'expenses',
    'hasPhysicalVenues',
    'hasOffers',
    'wallet_balance',
    'wallet_is_activated',
    'wallet_date_created'
]

WEBAPP_GET_BOOKING_INCLUDES = [
    "completedUrl",
    'isEventExpired',
    "isUserCancellable",
    {
        "key": "stock",
        "includes": [
            "isBookable",
            {
                "key": "offer",
                "includes": [
                    'isDigital',
                    'isEvent',
                    'hasBookingLimitDatetimesPassed',
                    'isBookable',
                    "isFullyBooked",
                    "offerType",
                    {
                        "key": "product",
                        "includes": ["thumbUrl"]
                    },
                    {
                        "key": "stocks",
                        "includes": ["isBookable"]
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
    "thumbUrl"
]

WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES = [
    "completedUrl",
    'isEventExpired',
    "isUserCancellable",
    {
        "key": "stock",
        "includes": [
            "isBookable",
            {
                "key": "offer",
                "includes": [
                    'isDigital',
                    'isEvent',
                    'isBookable',
                    'hasBookingLimitDatetimesPassed',
                    "isFullyBooked",
                    "offerType",
                    {
                        "key": "product",
                        "includes": ["thumbUrl"]
                    },
                    {
                        "key": "stocks",
                        "includes": ["isBookable"]
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
    "qrCode",
    "thumbUrl"
]

WEBAPP_PATCH_POST_BOOKING_INCLUDES = [
    "completedUrl",
    "isUserCancellable",
    {
        "key": "recommendation",
        "includes": [
            "productOrTutoIdentifier",
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
                    {
                        "key": "product",
                        "includes": ["thumbUrl"]
                    },
                    {
                        "key": "stocks",
                        "includes": ["isBookable"]
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
        "includes": ["isBookable"]
    },
    "thumbUrl",
    {
        "key": "user",
        "includes": USER_INCLUDES
    }
]

VENUE_INCLUDES = [
    'isValidated',
    'bic',
    'iban',
    "-validationToken",
    {
        "key": "managingOfferer",
        "includes": ['-validationToken']
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
