"""Benchmark Algolia and App Search search results on a set of
predefined search criteria.

Input: a YAML file (see `benchmark_search.yaml`).

Output: a re-usable JSON file and an HTML summary file. The JSON file
is merely useful when you debug the script and you want to re-generate
the HTML output without performing search requests again.

Requirements: you must set environment variables to access Algolia and
App Search API. See the code below for the list of such variables.

General usage:

    $ python benchmark_search.py input.yaml output.html

Regenerate HTML summary from a previous run:

    $ python benchmark_search.py output.json output.html
"""


import argparse
import dataclasses
import datetime
import json
import os
import pathlib
import pprint
import re
import time
import urllib.parse

import algoliasearch.search_client
import jinja2
import pytz
import requests
import requests.exceptions
import simplejson.errors
import yaml

from pcapi.utils import human_ids


ALGOLIA_API_KEY = os.environ["ALGOLIA_API_KEY"]
ALGOLIA_APPLICATION_ID = os.environ["ALGOLIA_APPLICATION_ID"]
ALGOLIA_INDEX_NAME = os.environ["ALGOLIA_OFFERS_INDEX_NAME"]
APPSEARCH_API_KEY = os.environ["APPSEARCH_API_KEY"]
APPSEARCH_HOST = os.environ["APPSEARCH_HOST"].rstrip("/")
APPSEARCH_ENGINE_NAME = "offers-meta"

OFFER_URL = "https://app.passculture.beta.gouv.fr/accueil/details/{human_id}"
TZ = pytz.timezone("Europe/Paris")

SLOW_QUERY_THRESHOLD = 1


def time_to_seconds(time_as_str):
    # Times are indexed in UTC, we must query in UTC too.
    offset = TZ.utcoffset(datetime.datetime.now()).seconds
    hours, minutes = time_as_str.split(":")
    return int(hours) * 3600 + int(minutes) * 60 - offset


class AlgoliaBackend:
    name = "algolia"

    def __init__(self):
        client = algoliasearch.search_client.SearchClient.create(ALGOLIA_APPLICATION_ID, ALGOLIA_API_KEY)
        self.index = client.init_index(ALGOLIA_INDEX_NAME)

    def date_as_timestamp(self, dt, start_of_day=False, end_of_day=False):
        if isinstance(dt, str):
            dt = datetime.datetime.fromisoformat(dt)
        if start_of_day:
            dt = datetime.datetime.combine(dt, datetime.time.min)
        if end_of_day:
            dt = datetime.datetime.combine(dt, datetime.time.max)
        return int(TZ.localize(dt).timestamp())

    def bool_as_str(self, boolean):
        return "true" if boolean else "false"

    def _build_filters(self, criteria):
        filters = {}
        facet_filters = []
        numeric_filters = []

        if "position" in criteria:
            filters["aroundLatLng"] = criteria["position"]
            filters["aroundRadius"] = 100_000  # meters

        if "around" in criteria:
            filters["aroundLatLng"] = criteria["around"]["position"]
            filters["aroundRadius"] = criteria["around"]["distance"] * 1000  # meters

        if "categories" in criteria:
            facet_filters.append([f"offer.category:{category}" for category in criteria["categories"]])

        if {"is_digital", "is_event", "is_thing"} & set(criteria):
            facet_filters.append([])
            for field, key in {"is_digital": "isDigital", "is_event": "isEvent", "is_thing": "isThing"}.items():
                if field in criteria:
                    value = self.bool_as_str(criteria[field])
                    facet_filters[-1].append(f"offer.{key}:{value}")

        if "is_duo" in criteria:
            facet_filters.append(f'offer.isDuo:{self.bool_as_str(criteria["is_duo"])}')

        if "is_free" in criteria:
            numeric_filters.append("offer.prices = 0")

        if "price_range" in criteria:
            low, high = criteria["price_range"]
            numeric_filters.append(f"offer.prices: {low} TO {high}")

        if "date_range" in criteria:
            start, end = criteria["date_range"]
            start = self.date_as_timestamp(start, start_of_day=True)
            end = self.date_as_timestamp(end, end_of_day=True)
            numeric_filters.append(f"offer.dates: {start} TO {end}")

        if "time_range" in criteria:
            start, end = criteria["time_range"]
            start = time_to_seconds(start)
            end = time_to_seconds(end)
            numeric_filters.append(f"offer.times: {start} TO {end}")

        if "newest_only" in criteria:
            now = datetime.datetime.now()
            start = self.date_as_timestamp(now - datetime.timedelta(days=15), start_of_day=True)
            end = self.date_as_timestamp(now, end_of_day=True)
            numeric_filters.append(f"offer.stocksDateCreated: {start} TO {end}")

        filters["facetFilters"] = facet_filters
        filters["numericFilters"] = numeric_filters
        return filters

    def search(self, description, criteria):
        filters = self._build_filters(criteria)
        start = time.perf_counter()
        results = self.index.search(criteria.get("text", ""), filters)
        elapsed = time.perf_counter() - start
        # XXX: apparently, the Algolia index still contains offers
        # whose 'objectID' are a humanized id. This should not happen
        # anymore and those offers should be reindexed under their
        # numeric id instead. Example: CUUEE.
        for result in results["hits"]:
            if not result["objectID"].isdigit():
                print(f'[Algolia] Found offer indexed with its humanized id: {result["objectID"]}')
                result["objectID"] = human_ids.dehumanize(result["objectID"])
        return ResultSet(
            elapsed=elapsed,
            query=filters,  # searched text is missing but we don't need it for Algolia
            results=[
                Result(
                    id=int(result["objectID"]),
                    score=None,  # not useful for Algolia results
                    name=result["offer"]["name"],
                    full=result,
                )
                for result in results["hits"]
            ],
        )


class AppSearchBackend:
    # Links to the reference implementation on frontend:
    # - https://github.com/pass-culture/pass-culture-app-native/blob/master/src/libs/search/filters/constants.ts
    # - https://github.com/pass-culture/pass-culture-app-native/blob/master/src/libs/search/filters/index.ts
    name = "appsearch"
    url = f"{APPSEARCH_HOST}/api/as/v1/engines/{APPSEARCH_ENGINE_NAME}/search"
    headers = {"Authorization": f"Bearer {APPSEARCH_API_KEY}"}
    result_fields = {
        field: {"raw": {}}
        for field in [
            "category",
            "dates",
            "id",
            "is_digital",
            "is_duo",
            "name",
            "prices",
            "thumb_url",
            "venue_position",
        ]
    }
    sort = [{"_score": "desc"}, {"ranking_weight": "desc"}, {"date_created": "asc"}]

    def date_as_string(self, dt, start_of_day=False, end_of_day=False):
        if isinstance(dt, str):
            dt = datetime.datetime.fromisoformat(dt)
        if start_of_day:
            dt = datetime.datetime.combine(dt, datetime.time.min)
        if end_of_day:
            dt = datetime.datetime.combine(dt, datetime.time.max)
        return TZ.localize(dt).isoformat()

    def _build_filters(self, criteria):
        filters = {}
        now = datetime.datetime.now()
        for field, value in criteria.items():
            if field == "text":  # directly set in `search()`
                continue
            if field == "categories":
                filters["category"] = value  # string or list
            elif field == "position":
                filters["venue_position"] = {"center": value, "distance": 100, "unit": "km"}
            elif field == "around":
                filters["venue_position"] = {"center": value["position"], "distance": value["distance"], "unit": "km"}
            elif field in ("is_duo", "is_digital", "is_event", "is_thing"):
                filters[field] = int(value)  # bool -> int
            elif field == "is_free":
                filters["prices"] = {"to": 1}
            elif field == "price_range":
                filters["prices"] = {"from": 100 * value[0], "to": 100 * value[1]}
            elif field == "date_range":
                filters["dates"] = {
                    "from": self.date_as_string(value[0], start_of_day=True),
                    "to": self.date_as_string(value[1], end_of_day=True),
                }
            elif field == "time_range":
                filters["times"] = {"from": time_to_seconds(value[0]), "to": time_to_seconds(value[1])}
            elif field == "newest_only":
                filters["stocks_date_created"] = {
                    "from": self.date_as_string(now - datetime.timedelta(days=15), start_of_day=True),
                    "to": self.date_as_string(now, end_of_day=True),
                }
            else:
                raise ValueError(f"Unsupported criterion: {field}")
        return filters

    def search(self, description, criteria):
        filters = self._build_filters(criteria)
        query = {
            "query": criteria.get("text", ""),
            "result_fields": self.result_fields,
            "page": {
                "current": 1,
                "size": 20,
            },
            "group": {"field": "group"},
            "sort": self.sort,
        }
        if filters:
            query["filters"] = {"all": [{key: value} for key, value in filters.items()]}
        if "position" in criteria:
            query["boosts"] = {
                "venue_position": {
                    "type": "proximity",
                    "function": "exponential",
                    "center": criteria["position"],
                    "factor": 10,
                }
            }
        try:
            response = requests.get(self.url, headers=self.headers, json=query, timeout=30)
            out = response.json()
            error_details = out.get("errors")
        except (requests.exceptions.RequestException, simplejson.errors.JSONDecodeError) as exc:
            response = None
            error_details = str(exc)
        if not response or not response.ok:
            print(f'[App Search] Error for "{description}" with the following query: ')
            pprint.pprint(query)
            print(error_details)
            results = []
        else:
            results = out["results"]
        return ResultSet(
            elapsed=response.elapsed.total_seconds() if response else 0,
            query=query,
            results=[
                Result(
                    id=int(result["id"]["raw"].split("|")[-1]),
                    score=result["_meta"]["score"],
                    name=result["name"]["raw"],
                    full={key: value["raw"] for key, value in result.items() if not key.startswith("_")},
                )
                for result in results
            ],
        )


@dataclasses.dataclass
class Result:
    id: int
    score: float
    name: str
    full: dict

    @property
    def url(self):
        return OFFER_URL.format(human_id=human_ids.humanize(self.id))


@dataclasses.dataclass
class ResultSet:
    elapsed: float
    query: dict
    results: [Result]

    @property
    def pretty_printed_query(self):
        return pprint.pformat(self.query)

    @property
    def is_slow(self):
        return self.elapsed > SLOW_QUERY_THRESHOLD


@dataclasses.dataclass
class Case:
    description: str
    criteria: dict
    results_per_backend: [ResultSet]

    @property
    def html_anchor(self):
        return urllib.parse.quote_plus(self.description)

    @property
    def pretty_printed_criteria(self):
        return pprint.pformat(self.criteria)

    @property
    def is_slow(self):
        return any(result_set.is_slow for result_set in self.results_per_backend)

    @property
    def max_elapsed(self):
        return max(result_set.elapsed for result_set in self.results_per_backend)


@dataclasses.dataclass
class Benchmark:
    backends: [str]
    cases: [Case] = dataclasses.field(default_factory=list)
    date: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)


class BenchmarkJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Benchmark):
            return {"__type__": "Benchmark", "value": {"backends": obj.backends, "cases": obj.cases, "date": obj.date}}
        if isinstance(obj, Case):
            return {
                "__type__": "Case",
                "value": {
                    "description": obj.description,
                    "criteria": obj.criteria,
                    "results_per_backend": obj.results_per_backend,
                },
            }
        if isinstance(obj, Result):
            return {
                "__type__": "Result",
                "value": {"id": obj.id, "score": obj.score, "name": obj.name, "full": obj.full},
            }
        if isinstance(obj, ResultSet):
            return {
                "__type__": "ResultSet",
                "value": {"elapsed": obj.elapsed, "query": obj.query, "results": obj.results},
            }
        if isinstance(obj, datetime.datetime):
            return {"__type__": "datetime.datetime", "value": obj.isoformat()}
        return json.JSONEncoder.default(self, obj)


class BenchmarkJsonDecoder(json.JSONDecoder):
    def decode(self, obj, *args, **kwargs):
        obj = super().decode(obj, *args, **kwargs)
        return self.post_decode(obj)

    @classmethod
    def post_decode(cls, obj):  # pylint: disable=too-many-return-statements
        if isinstance(obj, list):
            return [cls.post_decode(i) for i in obj]
        if not isinstance(obj, dict):
            return obj
        if obj.get("__type__") == "datetime.datetime":
            return datetime.datetime.fromisoformat(obj["value"])
        if obj.get("__type__") == "Benchmark":
            return Benchmark(**cls.post_decode(obj["value"]))
        if obj.get("__type__") == "Case":
            return Case(**cls.post_decode(obj["value"]))
        if obj.get("__type__") == "Result":
            return Result(**cls.post_decode(obj["value"]))
        if obj.get("__type__") == "ResultSet":
            return ResultSet(**cls.post_decode(obj["value"]))
        for key, value in list(obj.items()):
            obj[key] = cls.post_decode(value)
        return obj


def process(input_path, only_patterns, only_backend):
    with open(input_path) as fp:
        cases = yaml.safe_load(fp)
    backends = [AlgoliaBackend(), AppSearchBackend()]
    if only_backend.lower() == "appsearch":
        backends.pop(0)
    elif only_backend.lower() == "algolia":
        backends.pop(1)
    elif only_backend.lower():
        raise ValueError(f"Unknown backend: '{only_backend}'")
    benchmark = Benchmark(backends=[backend.name for backend in backends])
    for case in cases["cases"]:
        if only_patterns and not any(re.match(pattern, case["description"]) for pattern in only_patterns):
            continue
        results = [backend.search(case["description"], case["criteria"]) for backend in backends]
        benchmark.cases.append(Case(case["description"], case["criteria"], results))
        print(".", end="", flush=True)
    print()
    return benchmark


def write_json(benchmark, output_path):
    json.dump(benchmark, output_path.open("w"), cls=BenchmarkJsonEncoder)
    print(f"Wrote raw results in {output_path}")


def read_json(input_path):
    return json.load(input_path.open(), cls=BenchmarkJsonDecoder)


def write_html(benchmark, output_path):
    html = HTML_TEMPLATE.render(benchmark=benchmark, backends_len=len(benchmark.backends))
    output_path.write_text(html)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("html_output")
    parser.add_argument(
        "--only-cases",
        nargs="+",
        help="List of regular expressions that the case description must match to be included",
        default=[],
    )
    parser.add_argument(
        "--only-backend",
        choices=["algolia", "appsearch"],
        help="Run benchmark only on the requested backend",
        default="",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    input_path = pathlib.Path(args.input)
    html_output_path = pathlib.Path(args.html_output)
    if input_path.suffix in (".yaml", ".yml"):
        print("Running test cases...")
        benchmark = process(input_path, args.only_cases, args.only_backend)
        json_output_path = html_output_path.parent / pathlib.Path(f"{html_output_path.stem}.json")
        write_json(benchmark, json_output_path)
    else:  # read from JSON output of a previous run
        print("Reading from previous run...")
        benchmark = read_json(input_path)
    write_html(benchmark, html_output_path)
    print(f"Wrote HTML output to {html_output_path}")


HTML_TEMPLATE = jinja2.Template(
    """
<html>
<head>
  <title>Benchmark - {{ benchmark.date.strftime("%d/%m/%Y %H:%M:%S") }}</title>
  <style>
    table {
      border-collapse: collapse;
    }

    table, tr, td {
      border: 1px solid black;
    }

    .toc {
      margin-bottom: 1em;
    }

    .elapsed {
      padding: 1em 0 0 1em;
    }

    .slow-search {
      font-weight: bold;
      color: red;
    }
  </style>
</head>
<body>

<h1>Benchmark - {{ benchmark.date.strftime("%d/%m/%Y %H:%M:%S") }}</h1>

<details class="toc">
  <summary>Table des matières</summary>
  <ol class="toc">
    {% for case in benchmark.cases %}
      <li>
        <a href="#{{ case.html_anchor }}"
           class="elapsed {% if case.is_slow %} slow-search{% endif %}">{{ case.description }}</a>
        ({{ "%.3f"|format(case.max_elapsed) }}s)
      </li>
    {% endfor %}
  </ol>
</details>

<table>
  <thead>
    <tr>
      {% for backend in benchmark.backends %}
        <th>{{ backend }}</th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for case in benchmark.cases %}
      <tr class="case-header" id="{{ case.html_anchor }}">
        <th colspan="{{ backends_len }}" title="{{ case.pretty_printed_criteria }}">
          {{ case.description }}
        </th>
      </tr>
      <tr class="case-results">
        {% for result_set in case.results_per_backend %}
          <td>
            <div class="elapsed {% if result_set.is_slow %} slow-search{% endif %}">
              Temps de réponse : {{ "%.3f"|format(result_set.elapsed) }}s
              <details>
                <summary>Requête</summary>
                <pre>{{ result_set.pretty_printed_query }}</pre>
              </details>
            </div>
            <ol>
              {% for result in result_set.results %}
                <li><a href="{{ result.url }}" title="score : {{ result.score }}">[{{ result.id }}] {{ result.name }}</a></li>
              {% endfor %}
            </ol>
          </td>
        {% endfor %}
      </tr>
    {% endfor %}
  </tbody>
</table>

</body>
</html>
"""
)


if __name__ == "__main__":
    main()
