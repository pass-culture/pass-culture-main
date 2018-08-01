""" includes """

OFFERER_INCLUDES = [
    {
        "key": "managedVenues",
        "sub_joins": [
            "nOffers"
        ]
    },
    "nOffers",
    "isValidated"
]

EVENT_OCCURRENCE_INCLUDES = [
    'stock'
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
        "sub_joins": [
            {
                "key": "occurrences",
                "sub_joins": [
                    {
                        "key": "stock"
                    },
                    'venue'
                ]
            },
            "mediations"
        ],
    },
    {
        "key": "thing",
        "sub_joins": [
            {
                "key": "stock"
            },
            'venue',
            'mediations'
        ]
    },
    {
        "key": "venue",
        "sub_joins": [
            {
                "key": "managingOfferer",
                "sub_joins": OFFERER_INCLUDES
            }
        ]
    }
]


RECOMMENDATION_INCLUDES = [
    "mediation",
    {
        "key": "offer",
        "sub_joins": [
            "eventOrThing",
            "mediation",
            {
                "key": "stocks",
                "sub_joins": ["eventOccurrence"]
            },
            "venue",
        ]
    },
]


BOOKING_INCLUDES = [
    {
        "key": "stock",
        "sub_joins":
            [
                "offer",
                {
                    "key": "eventOccurrence",
                    "sub_joins": ["venue"]
                },
                "venue"
            ]
    },
    "recommendation"
]

USER_INCLUDES = [
    '-password',
    'wallet_balance'
]

VENUE_INCLUDES = [
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
    "provider"
]
