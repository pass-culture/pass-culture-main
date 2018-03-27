from flask import current_app as app

from utils.string_processing import inflect_engine

offers_include = [
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

includes = {
    'offers': offers_include
}

# helpful
""" magic call like get('offers', Offer.price > 10, lambda obj: obj['id']) """
def get(collection_name, filter = None, resolve = lambda obj: obj):
    model_name = inflect_engine.singular_noun(collection_name, 1)
    model = app.model[model_name[0].upper() + model_name[1:]]
    query = model.query.filter() if filter is None else model.query.filter(filter)
    include = includes.get(collection_name)
    return [resolve(obj._asdict(include=include)) for obj in query]
