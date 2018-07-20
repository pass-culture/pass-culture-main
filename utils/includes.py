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

EVENT_OCCURENCE_INCLUDES = [
    'offer'
]

EVENT_INCLUDES = [
    {
        "key": "occurences",
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
                "key": "occurences",
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

OFFER_INCLUDES = [
    {
        "key": "eventOccurence",
        "sub_joins": [
            {
                "key": "occasion",
                "sub_joins": [
                    'thing',
                    'event'
                ]
            },
            "venue"
        ]
    },
    "occurencesAtVenue",
    {
        "key": "offerer",
        #"sub_joins": OFFERER_INCLUDES
    },
    {
        "key": "occasion",
        "sub_joins": [
            "thing",
            "event"
        ]
    },
    {
        "key": "recommendationOffers",
        "sub_joins": [
            {
                "key": "mediation"
            }
        ]
    }
]

RECOMMENDATION_INCLUDES = [
    {
        "key": "mediatedOccurences",
        "sub_joins": [
            {
                "key": "offer",
                "sub_joins": [
                    {
                        "key": "eventOccurence",
                        "sub_joins": ["event", "venue"],
                    },
                    "thing",
                    "venue"
                ]
            }
        ]
    },
    {
        "key": "mediation",
        "sub_joins": [
            "event",
            "thing"
        ]
    }
]

RECOMMENDATION_OFFER_INCLUDES =  [
    {
        "key": "eventOccurence",
        "sub_joins": ["event", "venue"]
    }
]

BOOKING_INCLUDES = [
    {
        "key": "offer",
        "sub_joins": 
            [
                {
                    "key": "eventOccurence",
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
        "key": "eventOccurences",
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
