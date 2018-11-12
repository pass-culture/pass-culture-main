""" includes """

OFFERER_INCLUDES = [
    {
        "key": "managedVenues",
        "sub_joins": [
            "nOffers"
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
    "-bic",
    "-city",
    "-dateCreated",
    "-dateModifiedAtLastProvider",
    "-firstThumbDominantColor",
    "-iban",
    "-id",
    "-idAtProviders",
    "-isActive",
    "-lastProviderId",
    "-postalCode",
    "-thumbCount",
    "-validationToken"
]

EVENT_OCCURRENCE_INCLUDES = [
    'stocks'
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
    "mediations",
    "offers"
]

THING_INCLUDES = [
    "mediations",
    "offers"
]

OFFER_INCLUDES = [
    {
        "key": "event",
    },
    {
        "key": "eventOccurrences",
        "sub_joins": [
            {
                "key": "stock"
            }
        ]
    },
    "mediations",
    "stocks",
    {
        "key": "thing",
        "sub_joins": [
            {
                "key": "stock"
            },
            'mediations'
        ]
    },
    {
        "key": "venue",
        "sub_joins": [
            {
                "key": "managingOfferer",
                "sub_joins": [
                    "nOffers",
                    "isValidated"
                ]
            },
            "isValidated"
        ]
    }
]


RECOMMENDATION_INCLUDES = [
    "mediation",
    {
        "key": "offer",
        "sub_joins": [
            "dateRange",
            "eventOrThing",
            "mediation",
            {
                "key": "stocks",
                "sub_joins": ["eventOccurrence"]
            },
            {
                "key": "venue",
                "sub_joins": ["managingOfferer"]
            }
        ]
    },
]


BOOKING_INCLUDES = [
    "completedUrl",
    {
        "key": "stock",
        "sub_joins":
            [
                {
                    "key": "resolvedOffer",
                    "sub_joins": ["eventOrThing", "venue"]
                },
                "eventOccurrence"
            ]
    },
    "recommendation"
]

PRO_BOOKING_INCLUDES = [
    {
        "key": "stock",
        "sub_joins":
            [
                {
                    "key": "resolvedOffer",
                    "sub_joins": ["event", "thing"]
                },
                "eventOccurrence"
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

USER_INCLUDES = [
    '-validationToken',
    '-password',
    '-resetPasswordToken',
    '-resetPasswordTokenValidityLimit',
    'wallet_balance',
    'wallet_is_activated'
]

VENUE_INCLUDES = [
    'isValidated',
    "-validationToken",
    {
        "key": "eventOccurrences",
        "sub_joins": ["event"]
    },
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
    "-validationToken"
]


PENDING_VALIDATIONS_OFFERERS_INCLUDES = [

    "validationToken",
    "-firstThumbDominantColor",
    "-thumbcount",
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
                'phoneNumber': element['phoneNumber']
            })
        }]
    }
]

