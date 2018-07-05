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
                        "key": "offer",
                        #"sub_joins": [
                        #    {
                        #        "key": "offerer",
                        #        "sub_joins": OFFERER_INCLUDES
                        #    }
                        #]
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
                "key": "offer",
                #"sub_joins": [
                #    {
                #        "key": "offerer",
                #        "sub_joins": OFFERER_INCLUDES
                #    }
                #]
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
                "key": "event",
                "sub_joins": ['mediations']
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

BOOKING_INCLUDES = [
    {
        "key": "recommendation",
        "sub_joins": RECOMMENDATION_INCLUDES
    },
    {
        "key": "offer",
        "sub_joins": OFFER_INCLUDES
    }
]

USER_INCLUDES = [
    '-password'
]

VENUE_INCLUDES = [
    {
        "key": "eventOccurences",
        "sub_joins": ["event"]
    },
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
    'bookings': BOOKING_INCLUDES,
    'events': EVENT_INCLUDES,
    'eventOccurences': EVENT_OCCURENCE_INCLUDES,
    'occasions': OCCASION_INCLUDES,
    'offerers': OFFERER_INCLUDES,
    'offers': OFFER_INCLUDES,
    'recommendations': RECOMMENDATION_INCLUDES,
    'things': THING_INCLUDES,
    'users': USER_INCLUDES,
    'venues': VENUE_INCLUDES,
    'venueProviders': VENUE_PROVIDER_INCLUDES
}
