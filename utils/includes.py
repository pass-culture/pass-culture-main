""" includes """

OFFERERS_INCLUDES = [
    "managedVenues"
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
                        "sub_joins": OFFERERS_INCLUDES
                    }
                ]
            },
            'venue'
        ]
    },
    "mediations"
]

THING_INCLUDES = [
    "mediations"
]

OCCASION_INCLUDES = [
    {
        "key": "occurences",
        "sub_joins": [
            {
                "key": "offer",
                "sub_joins": [
                    {
                        "key": "offerer",
                        "sub_joins": OFFERERS_INCLUDES
                    }
                ]
            },
            'venue'
        ]
    },
    "mediations"
]

OFFERS_INCLUDES = [
    {
        "key": "eventOccurence",
        "sub_joins": [
            {
                "key": "event",
                "sub_joins": ['mediations']
            },
            "venue"
        ]
    },
    "occurencesAtVenue",
    {
        "key": "offerer",
        #"sub_joins": OFFERERS_INCLUDES
    },
    {
        "key": "thing",
        "sub_joins": [
            "mediations",
            "venue"
        ]
    },
    {
        "key": "recommendationOffers",
        "sub_joins": [
            {
                "key": "mediation"
            }
        ]
    },
    "venue"
]

RECOMMENDATIONS_INCLUDES = [
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
    },
    "bookings",
    {
        "key": "recommendationBookings",
        "resolve": (lambda element, filters: element['booking']),
        "sub_joins": [
            {
                "key": "booking"
            }
        ]
    }
]

RECOMMENDATION_OFFER_INCLUDES =  [
    {
        "key": "eventOccurence",
        "sub_joins": ["event", "venue"]
    }
]

BOOKINGS_INCLUDES = [
    {
        "key": "recommendation",
        "sub_joins": RECOMMENDATIONS_INCLUDES
    },
    {
        "key": "offer",
        "sub_joins": OFFERS_INCLUDES
    }
]

USERS_INCLUDES = [
    '-password'
]

VENUES_INCLUDES = [
    {
        "key": 'venueProviders',
        "resolve": (lambda element, filters: element['provider']),
        "sub_joins": ["provider"]
    },
    "offers"
]

VENUE_PROVIDER_INCLUDES = [
    "provider"
]

includes = {
    'bookings': BOOKINGS_INCLUDES,
    'events': EVENT_INCLUDES,
    'occasions': OCCASION_INCLUDES,
    'offerers': OFFERERS_INCLUDES,
    'offers': OFFERS_INCLUDES,
    'recommendations': RECOMMENDATIONS_INCLUDES,
    'things': THING_INCLUDES,
    'users': USERS_INCLUDES,
    'venues': VENUES_INCLUDES,
    'venueProviders': VENUE_PROVIDER_INCLUDES
}
