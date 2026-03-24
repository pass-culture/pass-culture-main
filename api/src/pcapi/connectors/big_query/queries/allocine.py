import datetime
import json
from typing import Any

import pydantic

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.serialization.allocine_serializers import AllocineMovie


def _build_runtime(raw_runtime: Any) -> str | None:
    """Convert a duration in minutes (int or str) to ISO 8601 format.

    Examples:
        >>> _build_runtime(101)
        'PT1H41M0S'
        >>> _build_runtime("120")
        'PT2H0M0S'
        >>> _build_runtime(None)
        None
    """
    if not raw_runtime:
        return None
    try:
        hours, minutes = divmod(int(raw_runtime), 60)
        return f"PT{hours}H{minutes}M0S"
    except (ValueError, TypeError):
        return None


def _build_credits(raw_credits_str: str | None) -> dict[str, list]:
    """Build the nested credits structure (edges/node).

    Example:
        >>> raw_credits = '[{"person_firstName": "Steven", "person_lastName": "Spielberg", "position_name": "Director"}]'
        >>> _build_credits(raw_credits)
        {
            'edges': [
                {
                    'node': {
                        'person': {
                            'firstName': 'Steven',
                            'lastName': 'Spielberg'
                        },
                        'position': {'name': 'Director'}
                    }
                }
            ]
        }
    """
    raw_credits = json.loads(raw_credits_str) if raw_credits_str else []
    return {
        "edges": [
            {
                "node": {
                    "person": {
                        "firstName": credit.get("person_firstName"),
                        "lastName": credit.get("person_lastName"),
                    },
                    "position": {"name": credit.get("position_name")},
                }
            }
            for credit in raw_credits
        ]
    }


def _build_cast(raw_cast_str: str | None, backlink: dict[str, str]) -> dict[str, Any]:
    """Build the nested cast structure (edges/node).

    Example:
        >>> raw_cast = '[{"firstName": "Tom", "lastName": "Hanks", "role": "Forrest Gump"}]'
        >>> backlink = {"url": "http://allocine.fr/...", "label": "Fiche Allociné"}
        >>> _build_cast(raw_cast, backlink)
        {
            'backlink': {'url': 'http://allocine.fr/...', 'label': 'Fiche Allociné'},
            'edges': [
                {
                    'node': {
                        'actor': {
                            'firstName': 'Tom',
                            'lastName': 'Hanks'
                        },
                        'role': 'Forrest Gump'
                    }
                }
            ]
        }
    """
    raw_cast = json.loads(raw_cast_str) if raw_cast_str else []
    return {
        "backlink": backlink,
        "edges": [
            {
                "node": {
                    "actor": {
                        "firstName": member.get("firstName"),
                        "lastName": member.get("lastName"),
                    },
                    "role": member.get("role"),
                }
            }
            for member in raw_cast
        ],
    }


class AllocineMovieBQ(AllocineMovie):
    """
    Pydantic model that transforms a flat BigQuery row
    into the nested `AllocineMovie` structure.
    """

    @pydantic.model_validator(mode="before")
    @classmethod
    def transform_bigquery_row(cls, data: Any) -> Any:
        """Reshape a flat BigQuery row into a nested dictionary.

        This method acts as a Pydantic pre-validator. It receives a flat dictionary
        representing a row from BigQuery and reorganizes it into the hierarchical
        structure required by the `AllocineMovie` schema.
        """

        backlink = {
            "url": data.get("backlink_url"),
            "label": data.get("backlink_label") or "Fiche Allociné",
        }

        internal_id = data.get("internalId")
        production_year = data.get("data_productionYear")

        return {
            "id": data.get("movie_id"),
            "internalId": int(internal_id) if internal_id else 0,
            "title": data.get("title"),
            "originalTitle": data.get("originalTitle"),
            "type": data.get("type"),
            "runtime": _build_runtime(data.get("runtime")),
            "synopsis": data.get("synopsis"),
            "backlink": backlink,
            "data": {
                "eidr": data.get("data_eidr"),
                "productionYear": int(production_year) if production_year else None,
            },
            "poster": {"url": data.get("poster_url")} if data.get("poster_url") else None,
            "releases": json.loads(data.get("releases")),
            "credits": _build_credits(data.get("credits_normalized")),
            "cast": _build_cast(data.get("cast_normalized"), backlink),
            "countries": json.loads(data.get("countries")),
            "genres": json.loads(data.get("genres")),
            "companies": json.loads(data.get("companies")),
        }


class AllocineMovieQuery(BaseQuery):
    def __init__(self, updated_since: datetime.datetime | None = None):
        """
        Initialize the Allocine movie query.

        Args:
            updated_since (datetime.datetime | None): Optional timestamp to filter the results.
                If provided, only movies updated after this specific date and time will be retrieved.
                If None, all available movies are fetched.
        """
        super().__init__()
        self.updated_since = updated_since

    @property
    def raw_query(self) -> str:
        """
        Build the SQL query string for BigQuery.

        Constructs a SELECT statement for the `allocine_movie` table.
        If `self.updated_since` is set, a WHERE clause (`WHERE updated_at > ...`)
        is appended to the query to filter by the modification date.

        Returns:
            str: The complete SQL query string.
        """
        where_clause = ""
        if self.updated_since:
            where_clause = f"WHERE updated_at > '{self.updated_since.isoformat()}'"

        return f"""
            SELECT
                movie_id,
                internalId,
                title,
                originalTitle,
                type,
                runtime,
                synopsis,
                poster_url,
                backlink_url,
                backlink_label,
                data_eidr,
                data_productionYear,
                cast_normalized,
                credits_normalized,
                releases,
                countries,
                genres,
                companies
            FROM
                `{settings.BIG_QUERY_TABLE_BASENAME}.allocine_movie`
            {where_clause}
            ORDER BY movie_id DESC
        """

    model = AllocineMovieBQ
