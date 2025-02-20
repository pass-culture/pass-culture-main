from dataclasses import dataclass
import json
import os
from time import time

import requests


ALGOLIA_APP_ID = os.environ.get("ALGOLIA_APP_ID")
ALGOLIA_API_KEY = os.environ.get("ALGOLIA_API_KEY")

INDEX_NAME = "PRODUCTION"

ALGOLIA_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{INDEX_NAME}/query"


@dataclass
class Location:
    lat: float
    lng: float
    city: str


@dataclass
class Theme:
    name: str
    categories: list[str]


@dataclass
class AlgoliaParams:
    location: Location
    radius: int
    theme: Theme
    days_from_now: int

    def get_query(self) -> dict:
        return {
            "analytics": False,
            "aroundLatLng": self._fmt_geoloc(),
            "aroundRadius": self.radius,
            "attributesToRetrieve": ["offer.name"],
            "attributesToSnippet": ["*:1"],
            "clickAnalytics": False,
            "enableABTest": False,
            "explain": ["*"],
            "facetFilters": self._fmt_subcategories(),
            "facets": ["*"],
            "getRankingInfo": False,
            "hitsPerPage": 10,
            "numericFilters": [self._fmt_date_range()],
            "page": 0,
            "responseFields": ["*"],
            "snippetEllipsisText": "…",
        }

    def _fmt_geoloc(self):
        return f"{self.location.lat},{self.location.lng}"

    def _fmt_subcategories(self):
        return [[f"offer.subcategoryId:{category}" for category in self.theme.categories]]

    def _fmt_date_range(self):
        now = int(time())
        return f"offer.dates:{now} TO {now + self.days_from_now * 24 * 3600}"

    def __repr__(self):
        return f"{self.location.city},{self.radius // 1000}km,{self.theme.name},les {self.days_from_now} jours à venir"

    @classmethod
    def headers(self):
        return "Ville,Rayon,Catégorie,Temporalité"


@dataclass
class AlgoliaQuery:
    params: AlgoliaParams
    result: dict | None = None

    def execute(self) -> dict | None:
        headers = {
            "X-Algolia-Application-Id": ALGOLIA_APP_ID,
            "X-Algolia-API-Key": ALGOLIA_API_KEY,
            "Content-Type": "application/json",
        }
        body = json.dumps(self.params.get_query())
        response = requests.post(ALGOLIA_URL, headers=headers, data=body)

        if response.status_code == 200:
            self.result = response.json()
        else:
            print(f"Error: {response.status_code}")
            self.result = None

        return self.result

    def __repr__(self):
        if self.result:
            return f"{self.params},{str(self.result['nbHits'])}"
        else:
            return f"{self.params},Error"

    @classmethod
    def headers(self):
        return f"{AlgoliaParams.headers()},Nombre de résultats"


paris_loc = Location(city="Paris", lat=48.861706, lng=2.351652)
toulouse_loc = Location(city="Toulouse", lat=43.600714, lng=1.450290)
st_jean_de_braye_loc = Location(city="St Jean de Braye", lat=47.918133, lng=1.977815)
aurillac_loc = Location(city="Aurillac", lat=44.917963, lng=2.440018)
st_jean_du_gard_loc = Location(city="St Jean du Gard", lat=44.101768, lng=3.881658)
locations = [paris_loc, toulouse_loc, st_jean_de_braye_loc, aurillac_loc, st_jean_du_gard_loc]

cinema_theme = Theme(name="Cinema", categories=["EVENEMENT_CINE", "SEANCE_CINE", "FESTIVAL_CINE"])
concert_theme = Theme(name="Concert", categories=["CONCERT", "FESTIVAL_MUSIQUE", "EVENEMENT_MUSIQUE"])
musees_theme = Theme(
    name="Musées", categories=["VISITE_GUIDEE", "VISITE", "EVENEMENT_PATRIMOINE", "MUSEE_VENTE_DISTANCE"]
)
spectacle_theme = Theme(
    name="Spectacle vivant", categories=["SPECTACLE_VENTE_DISTANCE", "FESTIVAL_SPECTACLE", "SPECTACLE_REPRESENTATION"]
)
categories_sets = [cinema_theme, concert_theme, musees_theme, spectacle_theme]

radiuses = [10_000, 20_000, 30_000, 50_000]

days_from_now_set = [7, 30, 90]

print(AlgoliaQuery.headers())
for location in locations:
    for radius in radiuses:
        for days_from_now in days_from_now_set:
            for theme in categories_sets:
                query = AlgoliaQuery(
                    params=AlgoliaParams(
                        location=location,
                        radius=radius,
                        theme=theme,
                        days_from_now=days_from_now,
                    )
                )
                query.execute()
                print(query)
