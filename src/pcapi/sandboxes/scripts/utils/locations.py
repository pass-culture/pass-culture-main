from pcapi.sandboxes.scripts.utils.ban import get_locations_from_postal_code


OFFERER_PLACES = [
    {
        "address": "148 RUE HENRI LANGLOIS",
        "city": "Drancy",
        "latitude": 48.91,
        "longitude": 2.44,
        "postalCode": "93700",
    },
    {
        "address": "148 ROUTE DE BONDY",
        "city": "Aulnay-sous-bois",
        "latitude": 48.92,
        "longitude": 2.48,
        "postalCode": "93600",
    },
    {"address": "1 AVENUE DE L ANSE", "city": "Kourou", "latitude": -52.64, "longitude": 5.16, "postalCode": "97310"},
    {"address": "1 ROUTE DE RABAN", "city": "Cayenne", "latitude": -52.18, "longitude": 4.55, "postalCode": "97300"},
]


def create_locations_from_places(places, max_location_per_place=2):
    locations = []
    for place in places:
        place_locations = get_locations_from_postal_code(place["postalCode"])
        if len(place_locations) > max_location_per_place:
            place_locations = place_locations[:max_location_per_place]
        locations += place_locations
    return locations
