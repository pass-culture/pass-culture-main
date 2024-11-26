import argparse
from dataclasses import dataclass
import datetime
import json
import math
import os
from pathlib import Path

import requests


MOCK_FILE = "./resp.json"

LOCATIONS = {"boetie": (48.87171, 2.308289)}
LOCATION = LOCATIONS["boetie"]


class InvalidEnvironment(Exception): ...


class AlgoliaAPIException(Exception): ...


@dataclass
class Offer:
    bookings_count: int
    distance: int
    distinct: str
    id: int
    indexed_at: str
    name: str


def algolia(index: str, query: str, subcategory: str, nb_hits: int, mock: bool = False) -> None:
    api_key = os.environ.get("ALGOLIA_API_KEY")
    app_id = os.environ.get("ALGOLIA_APP_ID")
    if not api_key or not app_id:
        raise InvalidEnvironment("Error: environment variables ALGOLIA_API_KEY and ALGOLIA_APP_ID are not set")

    if mock:
        if not Path(MOCK_FILE).is_file():
            raise FileNotFoundError(f"Error: mock file {MOCK_FILE} does not exist")

        with open(MOCK_FILE) as output_fd:
            return json.load(output_fd)

    data = {
        "requests": [
            {
                "indexName": f"{index}",
                "query": f'"{query}"',
                "advancedSyntax": True,
                "params": f"page=0&hitsPerPage={nb_hits}",
                "aroundRadius": "1000000",
                "aroundLatLng": f"{LOCATION[0]}, {LOCATION[1]}",
                "facetFilters": [[f"offer.subcategoryId:{subcategory}"]],
                "attributesToRetrieve": [
                    "_geoloc",
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
    requests.packages.urllib3.disable_warnings()
    response = requests.post(
        "https://e2ikxj325n-dsn.algolia.net/1/indexes/*/queries",
        headers={"x-algolia-api-key": api_key, "x-algolia-application-id": app_id},
        json=data,
        verify=False,
    )
    if not response.ok:
        raise AlgoliaAPIException(f"Code: {response.status_code}. Error: {response.json()}")

    results = response.json()
    if not mock:
        with open(MOCK_FILE, "w") as fd:
            fd.write(json.dumps(results))

    return results


def parse(data: dict) -> list[Offer]:
    hits = data["results"][0]["hits"]
    return [
        Offer(
            bookings_count=hit["offer"]["last30DaysBookings"],
            distinct=hit["distinct"],
            distance=int(
                math.sqrt((LOCATION[0] - hit["_geoloc"]["lat"]) ** 2 + (LOCATION[1] - hit["_geoloc"]["lng"]) ** 2)
                * 1000
            ),
            id=hit["objectID"],
            indexed_at=hit["offer"].get("indexedAt", "1900-01-01"),
            name=hit["offer"]["name"],
        )
        for hit in hits
    ]


def aggregate(offers: list[Offer]) -> list[tuple[tuple, dict]]:
    mapping = {}
    for offer in offers:
        indexation_date = datetime.datetime.fromisoformat(offer.indexed_at).date().isoformat()
        key = (offer.distinct, offer.bookings_count, indexation_date)
        if key not in mapping:
            mapping[key] = {"count": 1, "offers": [offer]}
        else:
            mapping[key]["count"] += 1
            mapping[key]["offers"].append(offer)

    return list(mapping.items())


def display(data: list[tuple[tuple, dict]]) -> None:
    print(
        f'{"distinct":15s} | {"name":15s} | {"distance":8s} | {"bookings":8s} | {"indexed at":30s} | {"records count":15s} | {"example id":12s}'
    )
    print("-" * (15 + 15 + 8 + 8 + 30 + 15 + 12 + 3 * 6))
    for key, value in data:
        distinct, bookings_count, indexed_at = key
        records_count = value["count"]
        offer_example = value["offers"][0]
        print(
            f"{distinct:15s} | {offer_example.name[:15]:15s} | {offer_example.distance:8d} | {str(bookings_count):8s} | {indexed_at:30s} | {records_count:15d} | {offer_example.id}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="algolia_client", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--index", type=str, default="PRODUCTION B", help="Algolia index to query from")
    parser.add_argument("-q", "--query", type=str, default="", help="Text query")
    parser.add_argument(
        "-s", "--subcategory", type=str, default="LIVRE_PAPIER", help="subcategoryId filter for records"
    )
    parser.add_argument("-n", "--nb-hits", type=int, default=2, help="Number of results to fetch (maximum is 1000)")
    args = parser.parse_args()
    display(
        aggregate(
            parse(algolia(index=args.index, query=args.query, subcategory=args.subcategory, nb_hits=args.nb_hits))
        )
    )
