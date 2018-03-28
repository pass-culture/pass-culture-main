offers_includes = [
    {
        "key": "eventOccurence",
        "sub_joins": [
            {
                "key": "event"
            }
        ]
    },
    {
        "key": "thing",
        "sub_joins": [
            {
                "key": "venue"
            }
        ]
    },
    {
        "key": "userMediationOffers",
        "sub_joins": [
            {
                "key": "mediation"
            }
        ]
    }
]

user_mediations_includes =  [
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
                    {
                        "key": "venue",
                        "sub_joins": ["venue"]
                    },
                    "thing",
                    "venue"
                ]
            }
        ]
    }
]

includes = {
    'offers': offers_includes,
    'user_mediations': user_mediations_includes
}
