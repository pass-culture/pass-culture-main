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
    "bic",
    "iban",
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

THING_INCLUDES = [
    {
        "key": "mediations",
        "sub_joins": ["thumbUrl"]
    },
    "offers",
    "-type",
    "offerType"
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
        "sub_joins": [
            "thumbUrl"
        ]
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
            {
                "key": "product",
                "sub_joins": [
                    "thumbUrl"
                ]
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
            'favorites',
            'isFinished',
            'isFullyBooked',
            "dateRange",
            "isEvent",
            "isThing",
            "stocks",
            {
                "key": "venue",
                "sub_joins": ["managingOfferer"]
            },
            {
                "key": "product",
                "sub_joins": ["thumbUrl", "offerType"]
            }
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
            {
                "key": "offer",
                "sub_joins": [
                    "favorites",
                    "isFinished",
                    "isFullyBooked",
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
            {
                "key": "offer",
                "sub_joins": [
                    "dateRange",
                    "favorites",
                    "isFinished",
                    "isFullyBooked",
                    {
                        "key": "product",
                        "sub_joins": ["offerType", "thumbUrl"]
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
        "resolve": (lambda element, filters: {
            'email': element['email'],
            'firstName': element['firstName'],
            'lastName': element['lastName']
        }),
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
        "resolve": (lambda element, filters: element['provider']),
        "sub_joins": ["provider"]
    },
    {
        "key": "stocks",
        "sub_joins": ["thing"]
    }
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
            "resolve": (lambda element, filters: {
                'email': element['email'],
                'publicName': element['publicName'],
                'dateCreated': element['dateCreated'],
                'departementCode': element['departementCode'],
                'canBookFreeOffers': element['canBookFreeOffers'],
                'isAdmin': element['isAdmin'],
                'firstName': element['firstName'],
                'lastName': element['lastName'],
                'postalCode': element['postalCode'],
                'phoneNumber': element['phoneNumber'],
                'validationToken': element['validationToken']
            })
        }]
    },
    {
        "key": "managedVenues",
        "resolve": (lambda element, filters: {
            'id': element['id'],
            'name': element['name'],
            'siret': element['siret'],
            'managingOffererId': element['managingOffererId'],
            'bookingEmail': element['bookingEmail'],
            'address': element['address'],
            'postalCode': element['postalCode'],
            'city': element['city'],
            'departementCode': element['departementCode'],
            'comment': element['comment'],
            'validationToken': element['validationToken']
        })
    }
]

MEDIATION_INCLUDES = [
    "thumbUrl"
]
