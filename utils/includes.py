
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
    "offerer",
    {
        "key": "thing",
        "sub_joins": [
            "mediations",
            "venue"
        ]
    },
    {
        "key": "userMediationOffers",
        "sub_joins": [
            {
                "key": "mediation"
            }
        ]
    },
    "venue"
]

USER_MEDIATIONS_INCLUDES =  [
    {
        "key": "mediation",
        "sub_joins": ["event", "thing"]
    },
    {
        "key": "userMediationBookings",
        "resolve": (lambda element, filters: element['booking']),
        "sub_joins": [
            {
                "key": "booking"
            }
        ]
    },
    {
        "key": "userMediationOffers",
        "resolve": (lambda element, filters: element['offer']),
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
    }
]

BOOKINGS_INCLUDES = [
    {
        "key": "userMediations",
        "sub_joins": USER_MEDIATIONS_INCLUDES
    },
    {
        "key": "offer",
        "sub_joins": OFFERS_INCLUDES
    }
]

includes = {
    'bookings': BOOKINGS_INCLUDES,
    'offers': OFFERS_INCLUDES,
    'user_mediations': USER_MEDIATIONS_INCLUDES
}
