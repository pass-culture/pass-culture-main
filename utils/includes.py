OFFERER_INCLUDES = [
    {
        "key": "managedVenues",
        "sub_joins": [
            "nOffers",
            "iban",
            "bic"
        ]
    },
    "nOffers",
    "isValidated",
    "-validationToken"
]

NOT_VALIDATED_OFFERER_INCLUDES = [
    "name",
    "siren",
    "-address",
    "-city",
    "-dateCreated",
    "-dateModifiedAtLastProvider",
    "-firstThumbDominantColor",
    "-id",
    "-idAtProviders",
    "-isActive",
    "-lastProviderId",
    "-postalCode",
    "-thumbCount",
    "-validationToken"
]

EVENT_INCLUDES = [
    {
        "key": "occurrences",
        "sub_joins": [
            {
                "key": "stock",
                "sub_joins": [
                    {
                        "key": "offerer",
                        "sub_joins": OFFERER_INCLUDES
                    }
                ]
            },
            'venue'
        ]
    },
    {
        "key": "mediations",
        "sub_joins": ["thumbUrl"]
    },
    "offers",
    "-type",
    "offerType",
    "thumbUrl"
]

OFFER_INCLUDES = [
    'isFinished',
    'isFullyBooked',
    {
        "key": "activeMediation",
        "sub_joins": ["thumbUrl"]
    },
    {
        "key": "mediations",
        "sub_joins": ["thumbUrl"]
    },
    "stockAlertMessage",
    "isEditable",
    "isEvent",
    "isDigital",
    "isThing",
    {
        "key": "product",
        "sub_joins": [
            {
                "key": "mediations",
                "sub_joins": ["thumbUrl"]
            },
            'offerType',
            {
                "key": "stock"
            },
            '-type'
        ]
    },
    {
        "key": "stocks",
        "sub_joins": ['bookings']
    },
    {
        "key": "venue",
        "sub_joins": [
            {
                "key": "managingOfferer",
                "sub_joins": [
                    "nOffers",
                    "isValidated",
                    "bic",
                    "iban"
                ]
            },
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
        "sub_joins": ["thumbUrl"]
    },
    {
        "key": "offer",
        "sub_joins": [
            "dateRange",
            "favorites",
            "isEvent",
            "isFinished",
            "isThing",
            "isFullyBooked",
            "offerType",
            {
                "key": "product",
                "sub_joins": ["thumbUrl", "offerType"]
            },
            "stocks",
            "venue",
        ]
    },
    "thumbUrl"
]

RECOMMENDATION_INCLUDES = [
    "discoveryIdentifier",
    {
        "key": "mediation",
        "sub_joins": ["thumbUrl"]
    },
    {
        "key": "offer",
        "sub_joins": [
            "dateRange",
            'favorites',
            "isEvent",
            'isFinished',
            'isFullyBooked',
            "isThing",
            "offerType",
            {
                "key": "product",
                "sub_joins": ["thumbUrl", "offerType"]
            },
            "stocks",
            {
                "key": "venue",
                "sub_joins": ["managingOfferer"]
            },
        ]
    },
    "thumbUrl"
]

USER_INCLUDES = [
    '-culturalSurveyId',
    '-password',
    '-resetPasswordToken',
    '-resetPasswordTokenValidityLimit',
    '-validationToken',
    'expenses',
    'hasPhysicalVenues',
    'hasOffers',
    'wallet_balance',
    'wallet_is_activated'
]

WEBAPP_GET_BOOKING_INCLUDES = [
    "completedUrl",
    "isUserCancellable",
    {
        "key": "recommendation",
        "sub_joins": [
            "discoveryIdentifier",
            {
                "key": "offer",
                "sub_joins": [
                    "favorites",
                    "isFinished",
                    "isFullyBooked",
                    "offerType",
                    {
                        "key": "product",
                        "sub_joins": ["thumbUrl"]
                    },
                    "stocks",
                    "venue",
                ]
            },
            {
                "key": "mediation",
                "sub_joins": ["thumbUrl"]
            },
            "thumbUrl"
        ]
    },
    "stock",
    "thumbUrl"
]

WEBAPP_PATCH_POST_BOOKING_INCLUDES = [
    "completedUrl",
    "isUserCancellable",
    {
        "key": "recommendation",
        "sub_joins": [
            "discoveryIdentifier",
            {
                "key": "offer",
                "sub_joins": [
                    "dateRange",
                    "favorites",
                    "isFinished",
                    "isFullyBooked",
                    "offerType",
                    {
                        "key": "product",
                        "sub_joins": ["thumbUrl"]
                    },
                    "stocks",
                    "venue",
                ]
            },
            {
                "key": "mediation",
                "sub_joins": ["thumbUrl"]
            },
            "thumbUrl"
        ]
    },
    "stock",
    "thumbUrl",
    {
        "key": "user",
        "sub_joins": USER_INCLUDES
    }
]

PRO_BOOKING_INCLUDES = [
    {
        "key": "stock",
        "sub_joins":
            [
                {
                    "key": "resolvedOffer",
                    "sub_joins": [
                        'isFinished',
                        'isFullyBooked',
                        {
                            "key": "product",
                            "sub_joins": ["offerType", "thumbUrl"]
                        },
                    ]
                }
            ]
    },
    {
        "key": 'user',
        "sub_joins": [
            '-id',
            '-canBookFreeOffers',
            '-clearTextPassword',
            '-culturalSurveyId',
            '-dateCreated',
            '-dateOfBirth',
            '-departementCode',
            '-isAdmin',
            '-needsToFillCulturalSurvey',
            '-offerers',
            '-password',
            '-phoneNumber',
            '-postalCode',
            '-publicName',
            '-resetPasswordToken',
            '-resetPasswordTokenValidityLimit',
            '-validationToken'
        ]
    }
]

VENUE_INCLUDES = [
    'isValidated',
    'bic',
    'iban',
    "-validationToken",
    {
        "key": "managingOfferer"
    },
    {
        "key": 'venueProviders',
        "sub_joins": ["provider"]
    },
]

VENUE_PROVIDER_INCLUDES = [
    "provider",
    "nOffers"
]

OFFERER_FOR_PENDING_VALIDATION_INCLUDES = [
    "validationToken",
    "-firstThumbDominantColor",
    "-thumbCount",
    "-idAtProviders",
    {
        "key": "UserOfferers",
        "sub_joins": [{
            "key": "user",
            "sub_joins": [
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
        "sub_joins": [
            '-publicName',
            '-thumbCount',
            '-idAtProviders',
            '-isVirtual',
            '-lastProviderId',
            '-latitude',
            '-longitude',
            '-dateModifiedAtLastProvider',
            '-firstThumbDominantColor'
        ]
    }
]

MEDIATION_INCLUDES = [
    "thumbUrl"
]

FEATURE_INCLUDES = [
    'nameKey'
]
