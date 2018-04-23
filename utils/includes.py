
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
        "key": "recommendationOffers",
        "sub_joins": [
            {
                "key": "mediation"
            }
        ]
    },
    "venue"
]

RECOMMENDATIONS_INCLUDES =  [
    "mediatedOccurences",
    {
        "key": "mediation",
        "sub_joins": ["event", "thing"]
    },
    {
        "key": "recommendationBookings",
        "resolve": (lambda element, filters: element['booking']),
        "sub_joins": [
            {
                "key": "booking"
            }
        ]
    },
    {
        "key": "recommendationOffers",
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
        "key": "recommendation",
        "sub_joins": RECOMMENDATIONS_INCLUDES
    },
    {
        "key": "offer",
        "sub_joins": OFFERS_INCLUDES
    }
]

includes = {
    'bookings': BOOKINGS_INCLUDES,
    'offers': OFFERS_INCLUDES,
    'recommendations': RECOMMENDATIONS_INCLUDES
}
