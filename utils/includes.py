""" includes """

OFFERER_INCLUDES = [
    {
        "key": "managedVenues",
        "sub_joins": [
            "nOccasions"
        ]
    },
    "nOccasions",
    "isValidated"
]

EVENT_OCCURRENCE_INCLUDES = [
    'offer'
]

EVENT_INCLUDES = [
    {
        "key": "occurrences",
        "sub_joins": [
            {
                "key": "offer",
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
    "occasions"
]

THING_INCLUDES = [
    "mediations",
    "occasions"
]

OCCASION_INCLUDES = [
    {
        "key": "event",
        "sub_joins": [
            {
                "key": "occurrences",
                "sub_joins": [
                    {
                        "key": "offer"
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
                "key": "offer"
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
        "key": "occasion",
        "sub_joins": [
            "eventOrThing",
            "mediation",
            {
                "key": "offers",
                "sub_joins": ["eventOccurrence"]
            },
            "venue",
        ]
    },
]


BOOKING_INCLUDES = [
    {
        "key": "offer",
        "sub_joins": 
            [
                {
                    "key": "eventOccurrence",
                    "sub_joins": ["venue"]
                },
                "venue"
            ]
    }
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
        "key": "offers",
        "sub_joins": ["thing"]
    }
]

VENUE_PROVIDER_INCLUDES = [
    "provider"
]
