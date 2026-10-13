import collections
import time
import unicodedata
import urllib.parse

import flask
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask_cors import cross_origin

from pcapi import settings
from pcapi.core.artist import models as artist_models
from pcapi.core.categories.app_search_tree import NATIVE_CATEGORIES
from pcapi.core.categories.app_search_tree import SEARCH_GROUPS
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import utils as offers_utils
from pcapi.core.search import serialization as search_serialization
from pcapi.models import db
from pcapi.routes.native import blueprint
from pcapi.utils.transaction_manager import atomic


HITS_PER_PAGE = 20
LOCALHOST_ORIGINS = [r"^https?://localhost(:\d+)?$", r"^https?://127\.0\.0\.1(:\d+)?$"]
HIGHLIGHT_PRE_TAG = "__ais-highlight__"
HIGHLIGHT_POST_TAG = "__/ais-highlight__"


def _response(hits: list[dict], query: str, start: float) -> dict:
    return {
        "hits": hits,
        "nbHits": len(hits),
        "page": 0,
        "nbPages": 1 if hits else 0,
        "hitsPerPage": HITS_PER_PAGE,
        "processingTimeMS": int((time.monotonic() - start) * 1000),
        "exhaustiveNbHits": True,
        "query": query,
        "params": urllib.parse.urlencode({"query": query}),
    }


def _normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c)).lower()


def _highlight(text: str, query: str) -> dict:
    # Map each normalized char back to its original index, to highlight despite case/accent differences
    normalized_chars, origin = [], []
    for index, char in enumerate(text):
        for normalized_char in _normalize(char):
            normalized_chars.append(normalized_char)
            origin.append(index)
    normalized_text, normalized_query = "".join(normalized_chars), _normalize(query)

    value, cursor, start = "", 0, normalized_text.find(normalized_query)
    while normalized_query and start != -1:
        end = start + len(normalized_query)
        text_start, text_end = origin[start], origin[end - 1] + 1
        value += f"{text[cursor:text_start]}{HIGHLIGHT_PRE_TAG}{text[text_start:text_end]}{HIGHLIGHT_POST_TAG}"
        cursor = text_end
        start = normalized_text.find(normalized_query, end)
    value += text[cursor:]

    if not normalized_query or cursor == 0:
        return {"value": text, "matchLevel": "none", "matchedWords": []}
    match_level = "full" if normalized_text == normalized_query else "partial"
    return {"value": value, "matchLevel": match_level, "matchedWords": normalized_query.split()}


def _facets(counts_by_subcategory: dict[str, int]) -> dict:
    facets = {}
    for key, categories in (("offer.searchGroups", SEARCH_GROUPS), ("offer.nativeCategoryId", NATIVE_CATEGORIES)):
        counter: collections.Counter = collections.Counter()
        for category in categories:
            for subcategory_id, count in counts_by_subcategory.items():
                if subcategory_id in category.included_subcategories:
                    counter[category.search_value] += count
        facets[key] = [{"value": value, "count": count} for value, count in counter.most_common()]
    return facets


# Hackathon POC: local search without Algolia; each hit is both a Query Suggestion and an AlgoliaOffer
@blueprint.native_route("/search/offers", methods=["GET"])
@cross_origin(origins=LOCALHOST_ORIGINS, supports_credentials=True)
@atomic()
def search_offers() -> dict:
    start = time.monotonic()
    query = flask.request.args.get("query", "").strip()

    hits = []
    if query:
        offers = (
            db.session.query(offers_models.Offer)
            .filter(offers_models.Offer.name.icontains(query, autoescape=True))
            .options(
                sa_orm.joinedload(offers_models.Offer.offererAddress).joinedload(
                    offerers_models.OffererAddress.address
                ),
                sa_orm.joinedload(offers_models.Offer.venue)
                .joinedload(offerers_models.Venue.offererAddress)
                .joinedload(offerers_models.OffererAddress.address),
                sa_orm.selectinload(offers_models.Offer.stocks),
            )
            .order_by(offers_models.Offer.id)
            .limit(HITS_PER_PAGE)
            .all()
        )

        counts_by_name: dict[str, dict[str, int]] = collections.defaultdict(dict)
        if settings.ALGOLIA_OFFERS_INDEX_NAME and offers:
            name_col = sa.func.lower(offers_models.Offer.name)
            rows = (
                db.session.query(name_col, offers_models.Offer.subcategoryId, sa.func.count())
                .filter(name_col.in_({offer.name.lower() for offer in offers}))
                .group_by(name_col, offers_models.Offer.subcategoryId)
                .all()
            )
            for name, subcategory_id, count in rows:
                counts_by_name[name][subcategory_id] = count

        for offer in offers:
            suggestion = offer.name.lower()
            stocks = offer.searchableStocks
            address = offers_utils.get_offer_address(offer)
            hit: dict = {
                "objectID": str(offer.id),
                "query": suggestion,
                "_highlightResult": {"query": _highlight(suggestion, query)},
                "offer": {
                    "name": offer.name,
                    "subcategoryId": offer.subcategoryId,
                    "thumbUrl": offer.thumbUrl,
                    "prices": sorted({float(stock.price) for stock in stocks}),
                    "dates": sorted(
                        {stock.beginningDatetime.timestamp() for stock in stocks if stock.beginningDatetime}
                    ),
                    "isDigital": offer.isDigital,
                    "isDuo": offer.isDuo,
                    "searchGroupName": next(
                        (
                            group.search_value
                            for group in SEARCH_GROUPS
                            if offer.subcategoryId in group.included_subcategories
                        ),
                        None,
                    ),
                },
                "_geoloc": search_serialization.format_coordinates(address.latitude, address.longitude),
                "venue": {
                    "id": offer.venue.id,
                    "name": offer.venue.publicName or offer.venue.name,
                    "publicName": offer.venue.publicName,
                    "city": address.city,
                    "postalCode": address.postalCode,
                    "address": address.street,
                },
            }
            if settings.ALGOLIA_OFFERS_INDEX_NAME:
                counts_by_subcategory = counts_by_name[suggestion]
                facets = _facets(counts_by_subcategory)
                hit[settings.ALGOLIA_OFFERS_INDEX_NAME] = {
                    "exact_nb_hits": sum(counts_by_subcategory.values()),
                    "facets": {"analytics": facets, "exact_matches": facets},
                }
            hits.append(hit)

    return _response(hits, query, start)


@blueprint.native_route("/search/artists", methods=["GET"])
@cross_origin(origins=LOCALHOST_ORIGINS, supports_credentials=True)
@atomic()
def search_artists() -> dict:
    start = time.monotonic()
    query = flask.request.args.get("query", "").strip()

    hits = []
    if query:
        normalized_query = db.session.scalar(sa.select(sa.func.lower(sa.func.immutable_unaccent(query))))
        normalized_name = sa.func.lower(sa.func.immutable_unaccent(artist_models.Artist.name))
        relevance = sa.case(
            (normalized_name == normalized_query, 0),
            (normalized_name.startswith(normalized_query, autoescape=True), 1),
            else_=2,
        )
        artists = (
            db.session.query(artist_models.Artist)
            .filter(
                sa.not_(artist_models.Artist.is_blacklisted),
                normalized_name.contains(normalized_query, autoescape=True),
            )
            .order_by(relevance, artist_models.Artist.name)
            .limit(HITS_PER_PAGE)
            .all()
        )
        hits = [
            {
                "objectID": artist.id,
                "name": artist.name,
                "image": artist.thumbUrl,
                "description": artist.biography or artist.description,
                "_highlightResult": {"name": _highlight(artist.name, query)},
            }
            for artist in artists
        ]

    return _response(hits, query, start)
