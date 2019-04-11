import json

from models import Product
from models.offerer import Offerer

from models.venue import Venue
from repository.offer_queries import get_is_offer_selected_by_keywords_string_at_column

config = {
    'Product_description': Product.description,
    'Product_name': Product.name,
    'Offerer_name': Offerer.name,
    'Venue_name': Venue.name
}


def get_keywords_analyzer(offer, keywords_string):
    values = offer.query.with_entities(*config.values()).first()

    analyzer = {}
    for (index, (key, column)) in enumerate(config.items()):

        is_selected = get_is_offer_selected_by_keywords_string_at_column(
            offer,
            keywords_string,
            column
        )

        if is_selected:
            analyzer[key] = values[index]
        else:
            analyzer[key] = False

    return analyzer


def print_keywords_analyzer(offer, keywords_string):
    keywords_analyzer = get_keywords_analyzer(offer, keywords_string)
    print(json.dumps(keywords_analyzer, indent=2, sort_keys=True))
