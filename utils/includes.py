""" includes """

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
    "offers",
    "-type",
    "offerType"
]

THING_INCLUDES = [
    "mediations",
    "offers",
    "-type",
    "offerType"
]

OFFER_INCLUDES = [
    {
        "key": "event",
        "sub_joins": [
            'offerType',
            '-type'
        ]
    },
    'isFinished',
    'isFullyBooked',
    "mediations",
    {
    "key": "stocks",
    "sub_joins": ['bookings']
    },
    {
        "key": "thing",
        "sub_joins": [
            'mediations',
            'offerType',
            {
                "key": "stock"
            },
            '-type'
        ]
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


RECOMMENDATION_INCLUDES = [
    "mediation",
    {
        "key": "offer",
        "sub_joins": [
            'isFinished',
            'isFullyBooked',
            "dateRange",
            {
                "key": "eventOrThing",
                "sub_joins": [
                    "offerType"
                ]
            },
            "mediation",
            "stocks",
            {
                "key": "venue",
                "sub_joins": ["managingOfferer"]
            }
        ]
    },
]


BOOKING_INCLUDES = [
    "completedUrl",
    "isUserCancellable",
    {
        "key": "stock",
        "sub_joins":
            [
                {
                    "key": "resolvedOffer",
                    "sub_joins": [
                        "eventOrThing",
                        "venue",
                        'isFinished',
                        'isFullyBooked'
                    ]
                }
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
                    "sub_joins": [
                        'isFinished',
                        'isFullyBooked',
                        {
                            "key": "event",
                            "sub_joins": ["offerType"]
                        },
                        {
                            "key": "thing",
                            "sub_joins": ["offerType"]
                        }
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
    "provider"
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
