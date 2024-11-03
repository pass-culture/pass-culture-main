from dataclasses import dataclass
import json
import os
import sys

import requests

USE_MOCK = True
MOCK_FILE = "./resp.json"


@dataclass
class Offer:
    bookings_count: int
    distinct: str
    id: int
    indexed_at: str
    name: str


def algolia() -> None:
    api_key = os.environ.get("ALGOLIA_API_KEY")
    app_id = os.environ.get("ALGOLIA_APP_ID")
    if not api_key or not app_id:
        print("Error: environment variables ALGOLIA_API_KEY and ALGOLIA_APP_ID are not set", file=sys.stderr)
        return

    index = "PRODUCTION B"
    query = "jamais plus"
    subcategory = "LIVRE_PAPIER"
    nb_results = 2

    if USE_MOCK:
        with open(MOCK_FILE) as output_fd:
            return json.load(output_fd)

    data = {
        "requests": [
            {
                "indexName": f"{index}",
                "query": f'"{query}"',
                "advancedSyntax": True,
                "params": f"page=0&hitsPerPage={nb_results}",
                "aroundRadius": "1000000",
                "aroundLatLng": "48.87171, 2.308289",
                "facetFilters": [[f"offer.subcategoryId:{subcategory}"]],
                "attributesToRetrieve": [
                    "distinct",
                    "objectID",
                    "offer.indexedAt",
                    "offer.last30DaysBookings",
                    "offer.name",
                ],
                "distinct": False,
            }
        ]
    }
    response = requests.post(
        "https://e2ikxj325n-dsn.algolia.net/1/indexes/*/queries",
        headers={"x-algolia-api-key": api_key, "x-algolia-application-id": app_id},
        data=data,
    )
    return response.json()


def parse(data: dict) -> list[Offer]:
    hits = data["results"][0]["hits"]
    return [
        Offer(
            bookings_count=hit["offer"]["last30DaysBookings"],
            distinct=hit["distinct"],
            id=hit["objectID"],
            indexed_at=hit["offer"]["indexedAt"],
            name=hit["offer"]["name"],
        )
        for hit in hits
    ]


def aggregate(offers: list[Offer]) -> dict:
    mapping = {}
    for offer in offers:
        key = (offer.distinct, offer.bookings_count, offer.indexed_at)
        if key not in mapping:
            mapping[key] = {"count": 1, "offers": [offer]}
        else:
            mapping[key]["count"] += 1
            mapping[key]["offers"].append(offer)

    return mapping


def display(data: dict) -> None:
    print(f'{"distinct":15s} | {"bookings":8s} | {"indexed at":12s} | {"count":5s} | {"example id":12s}')
    print("-" * (15 + 8 + 12 + 5 + 12 + 3 * 4))
    for key, value in data.items():
        print(f'{key[0]:15s} | {str(key[1]):8s} | {key[2]:12s} | {value["count"]:5d} | {value["offers"][0].id}')


if __name__ == "__main__":
    display(aggregate(parse(algolia())))
